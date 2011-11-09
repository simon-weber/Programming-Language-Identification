#Copyright (c) 2011 David Klein and Simon Weber
#Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php

import sys
from identifytraits import *
import commentIdentify

#gets a list of all the languages known so far
def getLanguages():
	
	try:	
		#open file
		language_file = open('languagesknown.txt', 'r+')
	except:
		language_file = open('languagesknown.txt', 'w')
		language_file.close()
		return []

	#read all known languages into array
	languages = []
	s = language_file.readline()
	while s != '':
		if s.strip() != '':
			languages.append(s.strip())
		s = language_file.readline()

	language_file.close()

	return languages

#takes all the individual scores and turns them into a final guess
def combineScores(list_of_scores, languages, showIndividualScores=False):
	#outputfile = open("output.txt", "w")
	finalTally = []
	for lang in languages:
		finalTally.append([0, lang])
	for j in list_of_scores.items():
		if showIndividualScores:
			#outputfile.write("________" + str(j[0]) + "________\n")
			print "________" + str(j[0]) + "________"
		for i in j[1].items():
			if showIndividualScores:
				#outputfile.write(str(i[0]) + ":" + " " * (10 - len(str(i[0]))) + str(int(i[1] * 100)) + "%\n")
				print str(i[0]) + ":" + " " * (10 - len(str(i[0]))) + str(int(i[1] * 100)) + "%"
			for k in range(len(finalTally)):
				if i[0] == finalTally[k][1]:
					finalTally[k][0] += i[1] * 100
	finalTally.sort()
	for i in range(min(len(finalTally), 5)):
		#outputfile.write(str(i+1) + ". " + str(finalTally[len(finalTally)-i-1][1]) + " - " + str(int(finalTally[len(finalTally)-i-1][0]*100)) + "\n")
		print str(i+1) + ". " + str(finalTally[len(finalTally)-i-1][1]) + " - " + str(int(finalTally[len(finalTally)-i-1][0]*100))

def stripCommentsAndStrings(source):
	result = commentIdentify.guessTokens(source)

	tokens = {}
	for start, end in result[0]:
		tokens[start] = end
	# for each line, we look to see if it begins with a comment start token
	for line in range(len(source)):
		processedLine = source[line].strip().split(" ")

		if processedLine == []:
			continue

		if tokens.has_key(processedLine[0]):
			i = line-1
			#now we look for the end token
			while i < len(source):
				i += 1
				endToken =  tokens[processedLine[0]]
				loc = source[i].find(endToken)
					
				#remove a line if the end token is not found, otherwise end the loop
				if loc == -1:
					source[i] = ""
					continue
				else:
					source[i] = source[i][loc:]
					i = len(source)
					break
				
	tokens = []
	for i in result[1]:
		tokens.append(i)
	# for each line, we look to see if it begins with a comment start token
	for line in range(len(source)):
		processedLine = source[line].strip().split(" ")
		if processedLine == []:
			continue

		for tok in tokens:
			if source[line].find(tok) != -1:		
				source[line] = source[line][:source[line].find(tok)]

	tokens = []
	for i in result[2]:
		tokens.append(i)
	# for each line, we look to see if it begins with a comment start token
	for line in range(len(source)):
		if tokens == []:
			break
		for tok in tokens:
			startLoc = source[line].find(tok)
			while startLoc != -1:
				endLoc = source[line].rfind(tok)
				#if the token is common enough to be a likely candidate, delete the string
				source[line] = source[line][:startLoc] + source[line][endLoc+1:]
				startLoc = source[line].find(tok)

	return source



def main():
	languages = getLanguages()
	source = sys.stdin.readlines()
	list_of_scores = {}
	list_of_scores["commentsAndStrings"] = identifyCommentAndString(languages, source)
	source = stripCommentsAndStrings(source)
	list_of_scores["lastCharacter"] = identifyLastCharacter(languages, source)
	list_of_scores["firstWord"] = identifyFirstWord(languages, source)
	list_of_scores["operator"] = identifyOperator(languages, source)
	list_of_scores["brackets"] = identifyBrackets(languages, source)
	list_of_scores["keywords"] = identifyKeywords(languages, source)
	list_of_scores["punctuation"] = identifyPunctuation(languages, source)
	if len(sys.argv) == 2 and sys.argv[1] == "-v":
		combineScores(list_of_scores, languages, True)
	else:
		combineScores(list_of_scores, languages)

main()
