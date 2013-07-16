scraperData = open('items.txt', 'r')
json = open('output.json', 'w')
log = open('log.txt', 'w')

linesRead = 0
linesSkipped = 0

# Format json file
json.write('[')

while 1:
	# Get the line
	print 'line ' + repr(linesRead)
	log.write('reading line ' + repr(linesRead) + '\n')
	line = scraperData.readline()

	# To check whether it's end of scraper data
	if not line:
		log.write('no more lines found.\n')
		break

	searchStart = 0
	while 1:
		log.write('searching from column ' + repr(searchStart) + '\n')
		searchIndex = line.find('<!--', searchStart)
		if searchIndex == -1: # End of that line was reached, presumably w/o finding the content
			log.write('last end comment tag not found. Content not found. Skipping line.\n')
			break
		else:
			log.write('\'<!--\' found at column ' + repr(searchIndex) + '\n')
			searchStart = searchIndex + 1
			# Looking for 'content' tag in the comments
			if line.find('content', searchIndex, searchIndex+20) >= 0:
				beg = searchIndex+4 # +4 to ignore the '<!--'
				end = line.find('-->', searchIndex, len(line))
				log.write('content identified at column ' + repr(searchIndex) + '\n')
				log.write('end found at column ' + repr(end) + '\n')
				log.write('content is:\n')
				backslashClean = line[beg:end].replace('\\','') # clean out backslashes for valid json
				log.write(backslashClean)
				if linesRead != 0: # json formatting
					json.write(',\n')
				json.write(backslashClean + '\n')
				break
			else:
				log.write('content not found, continuing from column ' + repr(searchStart) + '.\n')

	linesRead += 1

# Close off json array
json.write(']')

# Post-loop comments
log.write('\nparse completed.\n')
log.write('lines parsed: ' + repr(linesRead) + '.\n')
log.write('lines skipped: ' + repr(linesSkipped)+ '\n')

#close files
scraperData.close()
json.close()
log.close()