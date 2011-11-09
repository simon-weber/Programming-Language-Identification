#Copyright (c) 2011 David Klein and Simon Weber
#Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php

import re
import sys

#Constants for the number of words to search for. The higher the max is, the better the results, probably. This is a complete guess.
MAX_WORDS = 20
MIN_WORDS = 2

#The types of string tokens searched for:
#triple double ("""), double double (""), single double ("), single ('), grave (`)
#It is important that these are specified in order of subsumption.
#Does exclude some cases. See here for a good list:
# http://en.wikipedia.org/wiki/Comparison_of_programming_languages_%28strings%29
#Other problems with this: 
#	lisp? Consider 'str-ing a string?
#	python: triple single quote (''') multiline strings will probably get recognized as block comments.
strTokPossible = ("\"\"\"", "\"\"", "\"", "\'", "`")


#Known bracket combos.
#http://en.wikipedia.org/wiki/Comparison_of_programming_languages_%28syntax%29#Comments
knownBlockToks = {r"/*": (r"*/", ), r"/+": (r"+/", ), r"/#": (r"#/", ), "<#": ("#>", ), "=begin": ("= cut", "=end"), "#<tag>": (r"#</tag>", ), "{-": ("-}", ), "(*": ("*)", ), "<!--": ("-->", ), "|#": ("#|", ), "%{": ("}%", ), "#|": ("|#", ), "--[[": ("]]", )}

#Common brackets used in left block tokens.
commonBlockBrackets = ("(", "{", "[", "<", "|", "/")

#Chars mapped to their "symmetric" chars.
symmetric = {"(":")", "{":"}", "[":"]", "<":">"}

#Maximum number of lines to search for a block token. Another guess.
MAX_BLOCK_LINES = 11


#Return a tuple of (block tokens, line token, string token) where
#	block tokens is a dictionary mapping a tuple of (open token, close token)
#	to a list of the line ranges the tokens cover. Line ranges are tuples of 
#	(start line, end line).
	
#	line token and string token are dictionaries mapping token to number of occurences.
def guessTokens(source):
	
	#Precompile the regexs we're going to use.
	#Stored in max -> min order.
	#These will match a certain number of words seperated by spaces and ending with either a space or a newline.
	filters = list()
	for i in xrange(MAX_WORDS, MIN_WORDS - 1, -1):
		filters.append(re.compile(r"[a-zA-Z]+( [a-zA-Z]+){" + str(i) + r"," + str(i) + r"}[ \n]"))
	
	#Most general filter: will match the union of all above filters.
	hasWords = re.compile(r"[a-zA-Z]+( [a-zA-Z]+){" + str(MIN_WORDS) + r"," + str(MAX_WORDS) + r"}[ \n]")
		
		
	#Stores the line numbers we find in the initial filtering, along with a tuple of the span of the match.
	candidates = list()
	
	#Currently only considering one match per line, the one that has the most words.
	#DO: filter identical contents? may help in java-like programs where "public static void" will probably be seen a few times and added all times. Based on the logic that contents for user defined things will generally be unique (otherwise they would just reuse it).
	for lineNum in xrange(len(source)):
		for filter in filters:
			result = filter.search(source[lineNum])
			if result:
				#print "consider",str(lineNum) + ":"
				#print result.group()
				#print
				candidates.append((lineNum, result.span()))
				break;
	
	#Search these candidates for possible tokens and map token candidates to their occurances.
	#DO: reconsider this for multi matching within lines:
	#When a line is matched for a certain token, it is removed from consideration from further tokens. So, order is imporant. Planning to search for string, block, line, since they are less restrictive as we go on.
	
	#------------------------
	#Check for string tokens.
	#------------------------
	#DO: also make a special check for strings: [sTok][single alpha word][sTok]. Would be a single regex.
	stringToks = dict()
	
	#List of elements to remove.
	#Inefficient, possible improvement opportunity later.
	toRemove = list()
	
	for lineNum, span in candidates:
		line = source[lineNum]
		
		left = span[0]
		right = span[1]
		
		#Search left for a token, then if found search right for the same token.
		#Terminates after the first token is found.
		for searchTok in strTokPossible:
			#Search left for token.
			lIndex = line.rfind(searchTok, 0, left)
			if not lIndex == -1:
				#We found the token. Search right for a matching one.
				rIndex = line.find(searchTok, right)
				if not rIndex == -1:
					#Found two matching tokens. Increment the count for this token and stop searching.
					if not stringToks.has_key(searchTok):
						stringToks[searchTok] = 1
					else:
						stringToks[searchTok] += 1
					
					toRemove.append((lineNum, span))
					
					break
	
	#Remove the elements used in string matching.
	for el in toRemove:
		candidates.remove(el)
	
	#Strip string tokens of whitespace.
	for stringTok in stringToks.copy():
		if not stringTok == stringTok.strip(): 
			stringToks[stringTok.strip()] = stringToks[stringTok]
			del stringToks[stringTok]
			
			
			
	#------------------------------
	#Check for block comment tokens
	#------------------------------
	
	#Build a dictionary of the potential block tokens searching left from startLoc.
	#Assume that tokens are their own words. DO: extend to searching subwords?
	#map left tok -> list of lines found on
	
	potentialBToks = dict()
	
	#Search technique:
	#	Given a candidate line, search left and up, adding potential tokens.
	#	Search upwards until the line no longer has the "words" property, or we search a maximum number of lines.
	#	We give the search one more line after it is exhausted, since many people put comments one line above the start.
	#DO: change the search strategy. we should only allow a set number of lines to break the words property (2?).
	
	for startLineNum, span in candidates:
		lineNum = startLineNum
		left = span[0]
		right = span[1]
		searchedLines = 0
		
		extraLine = False
		done = False

		for i in range(2):
			if i == 1:
				extraLine = True
				
			while lineNum >= 0 and (not done) and (extraLine or (searchedLines <= MAX_BLOCK_LINES or hasWords.search(source[lineNum]))):
				if extraLine:
					extraLine = False
					done = True
					
				#Make sure that when searching on the same line to search left
				if lineNum == startLineNum:
					lineCont = source[lineNum][0:left]
				else:
					lineCont = source[lineNum]
					
				stripLine = lineCont.strip()
				
				if not stripLine == "":
					words = stripLine.split()
					
					for index in xrange(len(words)):
						word = words[index]
						score = blockTokenScore(word)
						
						#Switch to the uncommented if statement to run it generally instead of hardcoded.
						if score == 10:
						#if score > 0:
							if not potentialBToks.has_key(word):
								potentialBToks[word] = list()
							potentialBToks[word].append(lineNum)
						
				lineNum -= 1
				searchedLines += 1
	
	
	#Now we have all the potential tokens built from searching left.
	#For each one, search right in the same fashion looking for the likely end token.
	#Store in a dictionary indexed by tok pairs and mapping to tuples of lines they start/end on.
	blockToks = dict()
	
	#DO: this should really concern tokens and positions on the line, not lines themselves:
	#A line cannot count more than once for a single potential tok.
	#Map potential toks to lines they use.
	usedLines = dict()
	
	
	for pot in potentialBToks:
		for startLine in potentialBToks[pot]:
			lineNum = startLine
			searchedLines = 0
			endToks = getLikelyEndToks(pot)
			
			extraLine = False
			done = False
			
			for i in range(2):
				if i == 1:
					extraLine = True
			
				while lineNum < len(source) and (not done) and (extraLine or (searchedLines <= MAX_BLOCK_LINES or hasWords.search(source[lineNum]))):
					if extraLine:
						extraLine = False
						done = True
					
					#Search right if searching on the same line.
					if lineNum == startLine:
						lineCont = source[lineNum]
						lineCont = lineCont[lineCont.find(pot) + len(pot):]
					else:
						lineCont = source[lineNum]
						
					stripLine = lineCont.strip()
						
					if not (usedLines.has_key(pot) and lineNum in usedLines[pot]) and (not stripLine == ""):	
						words = stripLine.split()
						
						for endTok in endToks:
							if endTok in words:
								if not blockToks.has_key((pot, endTok)):
									blockToks[(pot, endTok)] = list()
									blockToks[(pot, endTok)].append((startLine, lineNum))
								else:
									blockToks[(pot, endTok)].append((startLine, lineNum))
								
								if not usedLines.has_key(pot):
									usedLines[pot] = set()
								
								usedLines[pot].add(lineNum)
							
					lineNum += 1
					searchedLines += 1

	#DO: probably could use strict heuristics here again, worked well in line tok searching.
	#DO: kill comments with empty contents?
	#DO: kill comments that have stuff after the end token?
	#DO: kill comments that don't hold "well" to the words property?
	#	kind of a more general version of the words property, including common punctuation and stuff.
	
	#Remove nested comments, keeping the outer one. Generally, this only happens with bad matches, so it will reduce their occurance.
	for bTok in blockToks.copy():
		for a in blockToks[bTok]:
			for b in blockToks[bTok]:
				if a == b:
					continue
				
				if a[0] <= b[0] and a[1] >= b[1]:
					blockToks[bTok].remove(b)
	#DO: it would be best if this searched left/right in a line too.
	#Check for subsumption among different types of comments. Remove the subsumed.
	clone = blockToks.copy()
	for tokA in clone:
		for tokB in clone:
			if tokA == tokB:
				continue
			for ocA in clone[tokA]:
				for ocB in clone[tokB]:
					if ocA[0] <= ocB[0] and ocA[1] >= ocB[1]:
						blockToks[tokB].remove(ocB)
			
			
			
	#DO: remove candidate lines that were used in block matching.
	
	#-----------------------------
	#Check for line comment tokens
	#-----------------------------
	
	#Currently, these are assumed to be multichar non alphanumeric token on left of line, not counting whitespace.
	#DO: Should change this to search left from match.
	lineToks = dict()
	
	for lineNum, span in candidates:
		line = source[lineNum]
		stripLine = line.strip()
		
		if stripLine == '':
			continue
			
		loc = 0
		while loc < len(stripLine):
			if stripLine[loc].isalnum():
				break
			loc += 1
				
		tok = stripLine[:loc]
		
		if tok == '':
			continue
			
		if not lineToks.has_key(tok):
			lineToks[tok] = 1
		else:
			lineToks[tok] += 1
	
	#Strip lineToks of whitespace.
	for lineTok in lineToks.copy():
		if not lineTok == lineTok.strip(): 
			lineToks[lineTok.strip()] = lineToks[lineTok]
			del lineToks[lineTok]
	
	#Combine similar lineToks into shortest possible token.
	#For example, toks ";;", ";(", and ";" will combine to just ";"
	#a and b will combine to b iff: 
	#	a == overwrite first len(b) chars in a with b
	#when a and b are combined, d[b] += d[a] and d[a] := 0.
	for a in lineToks:
		for b in lineToks:
			if a == b:
				continue
				
			if len(b) < len(a) and a == b + a[len(b) : ]:
				lineToks[b] += lineToks[a]
				lineToks[a] = 0
	
	#Remove tokens which were combined away.
	for lineTok in lineToks.copy():
		if lineToks[lineTok] == 0:
			del lineToks[lineTok]
	

	#Prune line tokens with string tokens.
	#DO: extend this to pruning all?
	for lineTok in lineToks.copy():
		if lineTok in stringToks:
			del lineToks[lineTok]
			
	#Prune line tokens with left block tokens.
	for lineTok in lineToks.copy():
		for blockTok in blockToks:
			if lineTok == blockTok[0]:
				del lineToks[lineTok]
	
	
	return (blockToks, lineToks, stringToks)

#Get the likely end tokens for the given block token.
#Hardcoded for common tokens, heuristic based for misses.
#DO: make this not stupid and generally more accepting.
def getLikelyEndToks(tok):
	if knownBlockToks.has_key(tok):
		return knownBlockToks[tok]
	
	#Simple heuristic: block tokens tend to be symettric.
	#DO: don't reverse alpha chars.
	endTok = list()
		
	for index in xrange(len(tok) - 1, -1, -1):
		endTok.append(getSymmetric(tok[index]))
	
	toReturn = ''.join(endTok)
	return (toReturn, )
	
#Get the "symmetric" character for a given char.
def getSymmetric(char):
	if symmetric.has_key(char):
		return symmetric[char]
	
	return char
	
#Get an arbitrary int score, based on how likely it is to be one.
#Above zero is good?
def blockTokenScore(tok):
	if knownBlockToks.has_key(tok):
		return 10
	
	if len(tok) == 0:
		return -10
	
	
	score = 0
	
	if "*" in tok:
		score += 2
		
	if "#" in tok:
		score += 2
	
	if len(tok) == 1:
		score -= 1.5
	
	#Brackets only counted once.
	for bracket in commonBlockBrackets:
		if bracket in tok:
			score += 2
			break
	
	
	#alphanum less common than non-alphanum
	for char in tok:
		if char.isalnum():
			score -= 1
		else:
			score += 1
	
	return score


#
# FILE I/O for adding to database
#
def getBlockDataFromFile(language, filename):
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
			data[temp.split(" ")[0]] = {}
			data[temp.split(" ")[0]][temp.split(" ")[1]] = int(temp.split(" ")[2])
			temp = textfile.readline().strip()
		textfile.close()
	return data

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
			data[temp.split(" ")[0]] = int(temp.split(" ")[-1])
			temp = textfile.readline().strip()
		textfile.close()
	return data


def stripCommentsAndStrings(language, source):
	#if less than this fraction of the total number comment tokens 
	#found are any specific comment token, then that comment token
	#will not be processed
	commentCutoff = 0.05


	#read in tokens
	commentFile = open("./database/" + str(language) + "/blockComments.txt", "r")

	tokens = {}
	temp = commentFile.readline().strip()
	while temp != '':
		tokens[temp.split(" ")[0]] = {}
		tokens[temp.split(" ")[0]][temp.split(" ")[1]] = int(temp.split(" ")[-1])
		temp = commentFile.readline().strip()
	commentFile.close()
	
	tokenSum = 0.0
	for start in tokens:
		for end in tokens[start]:
			tokenSum += tokens[start][end]

	# for each line, we look to see if it begins with a comment start token
	for line in range(len(source)):
		processedLine = source[line].strip().split(" ")

		if processedLine == []:
			continue

		if tokens.has_key(processedLine[0]):
			i = line
			#now we look for the end token
			while i < len(source):
				for endToken in tokens[processedLine[0]].keys():

					#quit if the block quote is too rare to likely be correct
					if tokens[processedLine[0]][endToken]/float(tokenSum) < commentCutoff:
						continue
					loc = source[i].find(endToken)
					
					#remove a line if the end token is not found, otherwise end the loop
					if loc == -1:
						source[i] = ""
						continue
					else:
						source[i] = source[i][loc:]
						i = len(source)
						break
				i += 1
	#read in tokens
	commentFile = open("./database/" + str(language) + "/lineComments.txt", "r")

	tokens = {}
	temp = commentFile.readline().strip()
	while temp != '':
		tokens[temp.split(" ")[0]] = int(temp.split(" ")[-1])
		temp = commentFile.readline().strip()
	commentFile.close()

	tokenSum = 0.0
	for tok in tokens:
		tokenSum += tokens[tok]
	
	# for each line, we look to see if it begins with a comment start token
	for line in range(len(source)):
		processedLine = source[line].strip().split(" ")
		if processedLine == []:
			continue

		for tok in tokens.keys():
			if source[line].find(tok) != -1:
				#if the token is common enough to be a likely candidate, delete the rest of the line
				if tokens[tok]/float(tokenSum) >= commentCutoff:
					source[line] = source[line][:source[line].find(tok)]

	#read in tokens
	commentFile = open("./database/" + str(language) + "/strings.txt", "r")

	tokens = {}
	temp = commentFile.readline().strip()
	while temp != '':
		tokens[temp.split(" ")[0]] = int(temp.split(" ")[-1])
		temp = commentFile.readline().strip()
	commentFile.close()

	tokenSum = 0.0
	for tok in tokens:
		tokenSum += tokens[tok]
	
	# for each line, we look to see if it begins with a comment start token
	for line in range(len(source)):
		if tokens == {}:
			break
		for tok in tokens.keys():
			if tokens[tok]/float(tokenSum) < commentCutoff:
				continue
			startLoc = source[line].find(tok)
			while startLoc != -1:
				endLoc = source[line].rfind(tok)
				#if the token is common enough to be a likely candidate, delete the string
				source[line] = source[line][:startLoc] + source[line][endLoc+1:]
				startLoc = source[line].find(tok)

	return source



	
def run(language, source):
	result = guessTokens(source)
	
	blockComments = getBlockDataFromFile(language, 'blockComments.txt')
	for startTok, endTok in result[0]:
		if blockComments.has_key(startTok):
			if blockComments[startTok].has_key(endTok):
				blockComments[startTok][endTok] += len(result[0][(startTok, endTok)])
			else:
				blockComments[startTok][endTok] = len(result[0][(startTok, endTok)])
		else:
			blockComments[startTok] = {}
			blockComments[startTok][endTok] = len(result[0][(startTok, endTok)])
	
	#write database back to file	
	writefile = open('./database/'+str(language)+'/blockComments.txt', 'w')
	for first in blockComments:
		for second in blockComments[first]:		
			writefile.write(str(first) + ' ' + str(second) + ' ' + str(blockComments[first][second]) + '\n')
	writefile.close()

	lineComments = getDataFromFile(language, 'lineComments.txt')
	for token in result[1]:
		if lineComments.has_key(token):
			lineComments[token] += result[1][token]
		else:
			lineComments[token] = result[1][token]
	
	#write database back to file	
	writefile = open('./database/'+str(language)+'/lineComments.txt', 'w')
	for token in lineComments:
		writefile.write(str(token) + ' ' + str(lineComments[token]) +  '\n')
	writefile.close()

	strings = getDataFromFile(language, 'strings.txt')
	for token in result[2]:
		if strings.has_key(token):
			strings[token] += result[2][token]
		else:
			strings[token] = result[2][token]
	
	#write database back to file	
	writefile = open('./database/'+str(language)+'/strings.txt', 'w')
	for token in strings:
		writefile.write(str(token) + ' ' + str(strings[token]) +  '\n')
	writefile.close()