import sys
import time
import re
import os
from termcolor import colored
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

class letter:
	def __init__(self, char, colour, relativePosition):
		self.char = char
		if colour == "cell-content bg-sky-600":
			self.colour = "blue"
		elif colour in ["cell-content","cell-content -"]:
			self.colour = "white"
		elif colour == "cell-content y":
			self.colour = "yellow"
		elif colour == "cell-content r":
			self.colour = "red"
		self.relativePosition = relativePosition

def printWord(word):
	i=1
	for letter in word:
		if letter.relativePosition==1 and i != 1:
			print(" ")
		print(colored(letter.char,letter.colour), end='')
		i+=1
	print(" ")

def getDisplayedWordLength():
	text="."
	i=2
	while text == ".":
		text = driver.find_element(By.XPATH, "//div[@class='motus-grid']//div["+str(i)+"]//div[1]").text
		i += 1
	return i - 2

def getDisplayedWord(length, line):
	l1=None
	absolutePosition = 1+((line-1)*length)
	relativePosition = 1
	element = driver.find_element(By.XPATH, "//div[@class='motus-grid']//div["+str(absolutePosition)+"]//div[1]")
	l1=letter(element.text, element.get_attribute("class"),relativePosition)
	displayedWord=[l1]
	absolutePosition += 1
	relativePosition += 1
	while absolutePosition <= length*line:
		element = driver.find_element(By.XPATH, "//div[@class='motus-grid']//div["+str(absolutePosition)+"]//div[1]")
		displayedWord.append(letter(element.text, element.get_attribute("class"),relativePosition))
		absolutePosition += 1
		relativePosition += 1
	return displayedWord

def generateRegex(length,tries):
	bannedLetter=""
	regex="^"
	yellowLettersString=""
	redLettersString=""
	whiteLettersString=""
	
	yellowLetters=[None] * (length+1)
	for i in range(0,length+1):
		yellowLetters[i]=""

	whiteLetters=[None] * (length+1)
	for i in range(0,length+1):
		whiteLetters[i]=""

	if tries == 1:
		currentWord=getDisplayedWord(length,tries)
		regex=regex+currentWord[0].char+"[A-Z]{"+str(length-1)+"}$"
	else:
		previousWords=getDisplayedWord(length,1)
		if tries >= 3:
			for i in range(2,tries):
				previousWords=previousWords+getDisplayedWord(length,i)
		printWord(previousWords)
		for letter in previousWords:
			if letter.colour == "white":
				whiteLettersString=whiteLettersString+letter.char
				whiteLetters[letter.relativePosition]=whiteLetters[letter.relativePosition]+letter.char
			if letter.colour == "yellow":
				yellowLetters[letter.relativePosition]=yellowLetters[letter.relativePosition]+letter.char
				yellowLettersString=yellowLettersString+letter.char
			if letter.colour == "red":
				redLettersString=redLettersString+letter.char

		# Removing duplicates
		whiteLettersString = "".join(set(whiteLettersString))
		yellowLettersString = "".join(set(yellowLettersString))
		redLettersString = "".join(set(redLettersString))

		#Remove yellow letters from banned letters
		for letter in whiteLettersString:
			if letter not in yellowLettersString:
				bannedLetter=bannedLetter+letter

		currentWord=getDisplayedWord(length,tries)
		for letter in yellowLettersString:
			regex=regex+"(?=.*"+letter+".*)"
		for letter in currentWord:
			if letter.char != ".":
				regex=regex+letter.char
			else:
				letterToExclude="".join(set(bannedLetter+yellowLetters[letter.relativePosition]+whiteLetters[letter.relativePosition]))
				regex=regex+"(?!["+letterToExclude+"])[A-Z]"
		regex=regex+"$"
	# print("Regex : "+regex)
	return regex

def searchForAWordInDictionnary(regex):
	pattern = re.compile(regex)
	for line in open('listes/mots.txt'):
		matches=re.finditer(pattern, line)
		for match in matches:
			return match.group()
	sys.exit("No word was found")

def typeACharacterInGame(char):
	element = driver.find_element(By.XPATH, "//span[normalize-space()='"+char+"']")
	element.click()

def validateWord():
	element = driver.find_element(By.XPATH, "//i[@class='fas fa-sign-in-alt']")
	element.click()

def checkGameWordCounter():
	try:
		element = driver.find_element(By.XPATH, "//div[@class='game-wrapper']//div[@class='game-header']//div[1]//div[2]")
	except:
		return 0
	counter=int(element.text.strip())
	return counter

def checkIfWordIsAccepted(length,tries):
	nextWord = getDisplayedWord(length, tries+1)
	returnValue = nextWord[0].char.isalpha()
	return returnValue


def typeWordInGame(word):
	for character in word:
		typeACharacterInGame(character)
		time.sleep(0.01)
	validateWord()

def deleteWordFromList(word):
	with open("listes/mots.txt", "r") as input:
		with open("listes/temp.txt", "w") as output:
			for line in input:
				if line.strip("\n") != word:
					output.write(line)
	os.replace("listes/temp.txt", "listes/mots.txt")

driver = webdriver.Firefox()
driver.set_window_position(0, 0)
driver.set_window_size(960, 1000)
driver.get("http://www.tusmo.xyz/")
time.sleep(1)
element = driver.find_element(By.XPATH, "//span[normalize-space()='Solo']")
element.click()
time.sleep(1)

for x in range(1,100):
	time.sleep(1)
	length=getDisplayedWordLength()
	print("\n\nWord " + str(x) + " with length : " + str(length))

	for i in range(1,7):
		print(" ")
		wordAcceptedByGame = False
		regex=generateRegex(length,i)
		printWord(getDisplayedWord(length, i))
		while wordAcceptedByGame is not True:
			suggestedWord=searchForAWordInDictionnary(regex)
			print(suggestedWord)
			typeWordInGame(suggestedWord)
			time.sleep(1.5)
			GameWordCounter = checkGameWordCounter()
			match GameWordCounter:
				case 0:
					sys.exit("Lost the game")
				case GameWordCounter if GameWordCounter == x:
					wordAcceptedByGame=checkIfWordIsAccepted(length,i)
					if wordAcceptedByGame is False:
						deleteWordFromList(suggestedWord)
						print("Word deleted from list")
				case GameWordCounter if GameWordCounter > x:
					wordAcceptedByGame = True
		if GameWordCounter > x:
			break
		
	print("Found the word !")
driver.quit()