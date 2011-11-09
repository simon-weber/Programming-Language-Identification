#Copyright (c) 2011 David Klein and Simon Weber
#Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php

#this file contains one function for each statistical feature
#these functions process source code from known languages and adds them to the database

#reads data into a dictionary from the database file and returns it
def getDataFromFile(language, filename):
	fileExists = False
	data = {}
	#IOError if file does not exist already
	try:
		textfile = open('./database/'+str(language)+'/' + str(filename), 'r')

		fileExists = True
	except:
		pass

	#read database into memory
	if fileExists:
		temp = textfile.readline().strip()
		while temp != '':
			data[temp.split(" ")[0]] = int(temp.split(" ")[1])
			temp = textfile.readline().strip()
		textfile.close()
	return data
	

#checks for similarities based on the last character on each line
def addLastCharacter(language, source):

	characters = getDataFromFile(language, 'lastCharacter.txt')

	#parse sourcecode for characters
	for line in source:
		if line.strip() == '':
			continue
		char = line.strip()[-1]
		if characters.has_key(char):
			characters[char] += 1
		else:
			characters[char] = 1

	#write database back to file	
	writefile = open('./database/'+str(language)+'/lastCharacter.txt', 'w')
	for char in characters:
		writefile.write(str(char) + ' ' + str(characters[char]) + '\n')
	writefile.close()

#checks for similarities based on the first word (i.e. all characters before the first space) on each line
def addFirstWord(language, source):

	words = getDataFromFile(language, 'firstWord.txt')
	#parse sourcecode for first word
	for line in source:
		if line.strip() == '':
			continue
		word = line.strip().split(" ")[0]
		if words.has_key(word):
			words[word] += 1
		else:
			words[word] = 1

	#write database back to file	
	writefile = open('./database/'+str(language)+'/firstWord.txt', 'w')
	for word in words:
		writefile.write(str(word) + ' ' + str(words[word]) + '\n')
	writefile.close()

#check for similarities in the frequency of different operators
def addOperator(language, source):
	
	operators = getDataFromFile(language, 'operators.txt')

	translationTable = '                                 !"#$%&\'()*+,-./          :;<=>?@                          [\\]^_`                          {|}~                                                                                                                                 '

	#parse sourcecode for operators
	oplist = []
	for line in source:
		if line.strip() == '':
			continue

		temp = line.translate(translationTable).strip()
		
		reading = False
		start = 0
		for i in range(len(temp)):
			if reading == False and temp[i] != ' ':
				start = i
				reading = True
			elif reading == True and temp[i] == ' ':
				oplist.append(temp[start:i])
				reading = False
		if reading == True:
			oplist.append(temp[start:])
	
	for operator in oplist:
		if operators.has_key(operator):
			operators[operator] += 1
		else:
			operators[operator] = 1	

	#write database back to file	
	writefile = open('./database/'+str(language)+'/operators.txt', 'w')
	for operator in operators:
		writefile.write(str(operator) + ' ' + str(operators[operator]) + '\n')
	writefile.close()

#counts relative prevalence of various types of brackets
def addBrackets(language, source):
	brackets = getDataFromFile(language, 'brackets.txt')
	
	bracketslist = "{}()<>[]"
	for brack in bracketslist:
		if brackets.has_key(brack):
			pass
		else:
			brackets[brack] = 0

	for line in source:
		for char in line:
			if brackets.has_key(char):
				brackets[char] += 1


	#write database back to file	
	writefile = open('./database/'+str(language)+'/brackets.txt', 'w')
	for brack in brackets:
		writefile.write(str(brack) + ' ' + str(brackets[brack]) + '\n')
	writefile.close()

#counts relative prevalence of various types of punctuation vs letters
def addPunctuation(language, source):
	puncnum = getDataFromFile(language, 'punctuation.txt')
	
	punclist = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
	letterlist = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

	if not puncnum.has_key(';'):
		puncnum[';'] = 0
	if not puncnum.has_key('a'):
		puncnum['a'] = 0

	for line in source:
		for char in line:
			if char in punclist:
				puncnum[';'] += 1
			elif char in letterlist:
				puncnum['a'] += 1


	#write database back to file	
	writefile = open('./database/'+str(language)+'/punctuation.txt', 'w')
	for punc in puncnum:
		writefile.write(str(punc) + ' ' + str(puncnum[punc]) + '\n')
	writefile.close()


#check for similarities in the frequency of different keywords
def addKeywords(language, source):
	
	keywords = getDataFromFile(language, 'keywords.txt')

	translationTable = '                                                                 ABCDEFGHIJKLMNOPQRSTUVWXYZ      abcdefghijklmnopqrstuvwxyz                                                                                                                                     '

	#parse sourcecode for operators
	wordlist = []
	for line in source:
		if line.strip() == '':
			continue

		temp = line.translate(translationTable).strip()
		
		reading = False
		start = 0
		for i in range(len(temp)):
			if reading == False and temp[i] != ' ':
				start = i
				reading = True
			elif reading == True and temp[i] == ' ':
				wordlist.append(temp[start:i])
				reading = False
		if reading == True:
			wordlist.append(temp[start:])
	
	for word in wordlist:
		if keywords.has_key(word):
			keywords[word] += 1
		else:
			keywords[word] = 1	

	#write database back to file	
	writefile = open('./database/'+str(language)+'/keywords.txt', 'w')
	for word in keywords:
		writefile.write(str(word) + ' ' + str(keywords[word]) + '\n')
	writefile.close()

