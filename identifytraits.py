#Copyright (c) 2011 David Klein and Simon Weber
#Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php

import commentIdentify

#this file contains one function for each statistical feature
#the functions process source code for unknown languages and return a
#dictionary containing keys (one for each known language) mapped to values
#(normalized to add to 1, where larger values mean that the language is more likely)

#constants that can be optimized for greater accuracy:
#checks the top X elements of each statistical feature
lastCharacterNum = 5
firstWordNum = 20
operatorNum = 20
commentsNum = 2
keywordNum = 20

#identifies based on which line-ending characters occur most frequently
def identifyLastCharacter(languages, source):
	characters = {}
	scores = {}

	#parse source
	num_lines = 0.0
	for line in source:
		if line.strip() == '':
			continue
		num_lines += 1
		char = line.strip()[-1]
		if characters.has_key(char):
			characters[char] += 1
		else:
			characters[char] = 1


	for lang in languages:
		#read database for each language into memory
		databasefile = open('./database/'+lang+'/lastCharacter.txt', 'r')
		lines = databasefile.readlines()
		database_characters = []
		
		#database_characters[i] = [frequency of occurence, character]
		for line in lines:
			database_characters.append([])
			database_characters[-1].append(int(line.strip()[2:]))
			database_characters[-1].append(line[0])
		database_characters.sort()

		summed = 0.0
		for i in database_characters:
			summed += i[0]

		#lang_score = 1/sum(((%freq of char in source - %freq of char in database)/%freq of char in database)^2) where sum is for the 5 most common characters in the language
		i = -1
		lang_score = 0
		while i > -1 - lastCharacterNum and i*-1 <= len(database_characters):
			if summed == 0:
				summed = 0.00000000001
			if num_lines == 0:
				num_lines = 0.00000000001
			if characters.has_key(database_characters[i][1]):
				lang_score += ((database_characters[i][0]/summed - characters[database_characters[i][1]]/num_lines)/(database_characters[i][0]/summed))**2
			else:
				lang_score += 1
			i -= 1
		if lastCharacterNum > len(database_characters):
			lang_score *= lastCharacterNum/len(database_characters)
		if lang_score == 0:
			lang_score = 0.0000000000000001
		lang_score = 1 / lang_score
		scores[lang] = lang_score
		databasefile.close()

	summed_scores = 0
	for lang in languages:
		summed_scores += scores[lang]

	for lang in languages:
		try:
			scores[lang] /= summed_scores
		except ZeroDivisionError:
			scores[lang] = 0

	return scores

#identifies based on the first 'word' on each line
def identifyFirstWord(languages, source):
	words = {}
	scores = {}

	#parse source
	num_lines = 0.0
	for line in source:
		if line.strip() == '':
			continue
		num_lines += 1
		
		word = line.strip().split(" ")[0]

		if words.has_key(word):
			words[word] += 1
		else:
			words[word] = 1


	for lang in languages:
		#read database for each language into memory
		databasefile = open('./database/'+lang+'/firstWord.txt', 'r')
		lines = databasefile.readlines()
		database_words = []
		
		#database_words[i] = [frequency of occurence, word]
		for line in lines:
			database_words.append([])
			database_words[-1].append(int(line.strip().split(" ")[1]))
			database_words[-1].append(line.split(" ")[0])
		database_words.sort()

		summed = 0.0
		for i in database_words:
			summed += i[0]

		#lang_score = 1/sum(((%freq of word in source - %freq of word in database)/%freq of word in database)^2) where sum is for the 5 most common characters in the language
		i = -1
		lang_score = 0
		while i > -1 - firstWordNum  and i*-1 <= len(database_words):
			if summed == 0:
				summed = 0.00000000001
			if num_lines == 0:
				num_lines = 0.00000000001
			if words.has_key(database_words[i][1]):
				lang_score += ((database_words[i][0]/summed - words[database_words[i][1]]/num_lines)/(database_words[i][0]/summed))**2
			else:
				lang_score += 1
			i -= 1
		if firstWordNum > len(database_words):
			lang_score *= firstWordNum/len(database_words)
		if lang_score == 0:
			lang_score = 0.0000000000000000001
		lang_score = 1 / lang_score
		scores[lang] = lang_score
		databasefile.close()

	summed_scores = 0
	for lang in languages:
		summed_scores += scores[lang]

	for lang in languages:
		try:
			scores[lang] /= summed_scores
		except ZeroDivisionError:
			scores[lang] = 0

	return scores

#identifies based on the frequency of different operators
def identifyOperator(languages, source):
	operators = {}
	scores = {}

	#parse source
	num_ops = 0.0
	oplist = []
	translationTable = '                                 !"#$%&\'()*+,-./          :;<=>?@                          [\\]^_`                          {|}~                                                                                                                                 '

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
				num_ops += 1
				oplist.append(temp[start:i])
				reading = False
		if reading == True:
			num_ops += 1
			oplist.append(temp[start:])

	for operator in oplist:
		if operators.has_key(operator):
			operators[operator] += 1
		else:
			operators[operator] = 1


	for lang in languages:
		#read database for each language into memory
		databasefile = open('./database/'+lang+'/operators.txt', 'r')
		lines = databasefile.readlines()
		database_operator = []
		
		#database_operator[i] = [frequency of occurence, operator]
		for line in lines:
			database_operator.append([])
			database_operator[-1].append(int(line.strip().split(" ")[1]))
			database_operator[-1].append(line.split(" ")[0])
		database_operator.sort()

		summed = 0.0
		for i in database_operator:
			summed += i[0]

		#lang_score = 1/sum(((%freq of operator in source - %freq of operator in database)/%freq of operator in database)^2) where sum is for the 5 most common characters in the language
		i = -1
		lang_score = 0
		while i > -1 - operatorNum and i*-1 <= len(database_operator):
			if summed == 0:
				summed = 0.00000000001
			if num_ops == 0:
				num_ops = 0.00000000001
			if operators.has_key(database_operator[i][1]):
				lang_score += ((database_operator[i][0]/summed - operators[database_operator[i][1]]/num_ops)/(database_operator[i][0]/summed))**2
			else:
				lang_score += 1
			i -= 1		
		if operatorNum > len(database_operator):
			lang_score *= operatorNum/len(database_operator)
		if lang_score == 0:
			lang_score = 0.000000000000000000000001
		lang_score = 1 / lang_score
		scores[lang] = lang_score
		databasefile.close()

	summed_scores = 0
	for lang in languages:
		summed_scores += scores[lang]

	for lang in languages:
		try:
			scores[lang] /= summed_scores
		except ZeroDivisionError:
			scores[lang] = 0

	return scores

#identifies based on relative frequencies of the different types of brackets
def identifyBrackets(languages, source):
	brackets = {}
	brackets_list = "{}<>()[]"
	scores = {}

	num_brackets = 0.0

	for brack in brackets_list:
		brackets[brack] = 0

	for line in source:
		for char in line:
			if brackets.has_key(char):
				brackets[char] += 1

	for brack in brackets_list:
		num_brackets += brackets[brack]

	for lang in languages:
		#read database for each language into memory
		databasefile = open('./database/'+lang+'/brackets.txt', 'r')
		lines = databasefile.readlines()
		database_brackets = []
		
		#database_brackets[i] = [frequency of occurence, brackets]
		for line in lines:
			database_brackets.append([])
			database_brackets[-1].append(int(line.strip().split(" ")[1]))
			database_brackets[-1].append(line.split(" ")[0])

		summed = 0.0
		for i in database_brackets:
			summed += i[0]

		#lang_score = 1/sum(((%freq of char in source - %freq of char in database)/%freq of char in database)^2) where sum is for the 5 most common characters in the language
		lang_score = 0
		for brack in brackets_list:
			for i in database_brackets:
				if i[1] == brack:
					if summed == 0:
						summed = 0.00000000001
					if num_brackets == 0:
						num_brackets = 0.00000000001
					lang_score += (i[0]/summed - brackets[brack]/num_brackets)**2
		if lang_score == 0:
			lang_score = 0.0000000000000001
		lang_score = 1 / lang_score
		scores[lang] = lang_score
		databasefile.close()

	summed_scores = 0
	for lang in languages:
		summed_scores += scores[lang]

	for lang in languages:
		try:
			scores[lang] /= summed_scores
		except ZeroDivisionError:
			scores[lang] = 0

	return scores

#identifies based on the comments and strings
def identifyCommentAndString(languages, source):
	scores = {}

	#parse source
	num_lines = float(len(source))

	result = commentIdentify.guessTokens(source)
	for lang in languages:
		#read database for each language into memory
		databasefile = open('./database/'+lang+'/lineComments.txt', 'r')
		lineCommentlines = databasefile.readlines()
		databasefile.close()
		databasefile = open('./database/'+lang+'/blockComments.txt', 'r')
		blockCommentlines = databasefile.readlines()
		databasefile.close()
		databasefile = open('./database/'+lang+'/strings.txt', 'r')
		stringlines = databasefile.readlines()
		databasefile.close()
		
		database_linecomments = []
		
		#create databases
		for line in lineCommentlines:
			database_linecomments.append([])
			database_linecomments[-1].append(int(line.strip().split(" ")[-1]))
			database_linecomments[-1].append(line.split(" ")[0])
		database_linecomments.sort()

		database_blockcomments = []
		
		
		for line in blockCommentlines:
			database_blockcomments.append([])
			database_blockcomments[-1].append(int(line.strip().split(" ")[-1]))
			database_blockcomments[-1].append([line.split(" ")[0], line.split(" ")[1]])
		database_blockcomments.sort()

		database_strings = []
		
		
		for line in stringlines:
			database_strings.append([])
			database_strings[-1].append(int(line.strip().split(" ")[-1]))
			database_strings[-1].append(line.split(" ")[0])
		database_strings.sort()

		#lang_score gets 1 'point' every time you find a match in terms of comment and string tokens
		i = -1
		lang_score = 0
		while i > -1 - commentsNum  and i*-1 <= len(database_blockcomments):			
			for start, end in result[0]:
				if database_blockcomments[i][1][0] == start and database_blockcomments[i][1][0] == end:
					lang_score += 1
			i -= 1
		j = i
		i = -1
		while i > -1 - commentsNum  and i*-1 <= len(database_linecomments):			
			for tok in result[1]:
				if database_linecomments[i][1] == tok:
					lang_score += 1
			i -= 1
		j += i
		i = -1
		while i > -1 - commentsNum  and i*-1 <= len(database_strings):			
			for tok in result[2]:
				if database_strings[i][1] == tok:
					lang_score += 1
			i -= 1
		j += i

		lang_score *= j/((commentsNum+1)*3)
		if lang_score == 0:
			lang_score = 0.0000000000000000001
		scores[lang] = lang_score
		

	summed_scores = 0
	for lang in languages:
		summed_scores += scores[lang]

	for lang in languages:
		try:
			scores[lang] /= summed_scores
		except ZeroDivisionError:
			scores[lang] = 0

	return scores

#identifies based on the frequency of different keywords
def identifyKeywords(languages, source):
	keywords = {}
	scores = {}

	#parse source
	num_words = 0.0
	wordlist = []
	translationTable = '                                                                 ABCDEFGHIJKLMNOPQRSTUVWXYZ      abcdefghijklmnopqrstuvwxyz                                                                                                                                     '


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
				num_words += 1
				wordlist.append(temp[start:i])
				reading = False
		if reading == True:
			num_words += 1
			wordlist.append(temp[start:])

	for word in wordlist:
		if keywords.has_key(word):
			keywords[word] += 1
		else:
			keywords[word] = 1


	for lang in languages:
		#read database for each language into memory
		databasefile = open('./database/'+lang+'/keywords.txt', 'r')
		lines = databasefile.readlines()
		database_keywords = []
		
		#database_operator[i] = [frequency of occurence, operator]
		for line in lines:
			database_keywords.append([])
			database_keywords[-1].append(int(line.strip().split(" ")[1]))
			database_keywords[-1].append(line.split(" ")[0])
		database_keywords.sort()

		summed = 0.0
		for i in database_keywords:
			summed += i[0]

		#lang_score = 1/sum((%freq of keyword in source - %freq of keyword in database)^2) where sum is for the 5 most common characters in the language
		i = -1
		lang_score = 0
		while i > -1 - keywordNum and i*-1 <= len(database_keywords):
			if summed == 0:
				summed = 0.00000000001
			if num_words == 0:
				num_words = 0.00000000001
			if keywords.has_key(database_keywords[i][1]):
				lang_score += ((database_keywords[i][0]/summed - keywords[database_keywords[i][1]]/num_words)/(database_keywords[i][0]/summed))**2
			else:
				lang_score += 1
			i -= 1		
		if keywordNum > len(database_keywords):
			lang_score *= keywordNum/len(database_keywords)
		if lang_score == 0:
			lang_score = 0.000000000000000000000001
		lang_score = 1 / lang_score
		scores[lang] = lang_score
		databasefile.close()

	summed_scores = 0
	for lang in languages:
		summed_scores += scores[lang]

	for lang in languages:
		try:
			scores[lang] /= summed_scores
		except ZeroDivisionError:
			scores[lang] = 0

	return scores

#identifies based on relative frequencies of the different types of punctuation
def identifyPunctuation(languages, source):
	punctuation = {}
	punclist = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
	letterlist = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
	scores = {}

	punctuation[';'] = 0.0
	punctuation['a'] = 0.0

	for line in source:
		for char in line:
			if char in punclist:
				punctuation[';'] += 1
			elif char in letterlist:
				punctuation['a'] += 1

	for lang in languages:
		#read database for each language into memory
		databasefile = open('./database/'+lang+'/punctuation.txt', 'r')
		lines = databasefile.readlines()
		database_punctuation = {}
		
		for line in lines:
			line = line.strip().split(" ")
			if line[0] == 'a':
				database_punctuation['a'] = float(line[1])
			elif line[0] == ';':
				database_punctuation[';'] = float(line[1])
		lang_score = 0.0
		lang_score += abs((punctuation['a']/(punctuation[';']+punctuation['a']))-(database_punctuation['a']/(database_punctuation[';']+database_punctuation['a'])))
		lang_score += abs((punctuation[';']/(punctuation[';']+punctuation['a']))-(database_punctuation[';']/(database_punctuation[';']+database_punctuation['a'])))
		if lang_score == 0:
			lang_score = 0.000000000001
		lang_score = 1 / (lang_score**.5)
		scores[lang] = lang_score
		databasefile.close()

	summed_scores = 0
	for lang in languages:
		summed_scores += scores[lang]

	for lang in languages:
		try:
			scores[lang] /= summed_scores
		except ZeroDivisionError:
			scores[lang] = 0

	return scores

