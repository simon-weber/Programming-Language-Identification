#Copyright (c) 2011 David Klein and Simon Weber
#Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php

import sys
import os
from traits import *

from commentIdentify import *

#checks to see if a directory exists and if it does not, it creates it
def checkDir(directory):
	d = os.path.dirname("./database/" + str(directory) + "/")
	if not os.path.exists(d):
		os.makedirs(d)

#finds which language the user want to use and returns it as a string
def getLanguage():

	#open file
	try:
		language_file = open('languagesknown.txt', 'r+')
	except:
		language_file = open('languagesknown.txt', 'w')
		language_file.close()
		language_file = open('languagesknown.txt', 'r+')

	#read all known languages into array
	languages = []
	s = language_file.readline()
	while s != '':
		if s.strip() != '':
			languages.append(s.strip())
		s = language_file.readline()

	#check for command line argument
	for i in range(len(sys.argv)):
		if sys.argv[i] == '-l':
			for j in languages:
				if sys.argv[i+1] == j:
					language_file.close()
					checkDir(j)
					return j
			language_file.seek(0, 2)
			language_file.write(str(sys.argv[i+1]) + "\n")
			language_file.close()
			checkDir(sys.argv[i+1])
			return sys.argv[i+1]
			
	
	language_file.close()
	print "Please type -l <language> as a command line argument."
	sys.exit()



#parses through the source for every trait that we are looking for
def addToDatabase(language, source):
	#commentIdentify.run(language, source)
	source = commentIdentify.stripCommentsAndStrings(language, source)
	#addLastCharacter(language, source)
	#addFirstWord(language, source)
	#addOperator(language, source)
	#addBrackets(language, source)
	addKeywords(language, source)
	addPunctuation(language, source)


def main():
	source = sys.stdin.readlines()
	language = getLanguage()
	addToDatabase(language, source)

main()
