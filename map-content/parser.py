import json

# Functions
def record(string):
	print string
	log.write(string)

# Files
scraperData = open('items.txt', 'r')
output = open('output.json', 'w')
log = open('log.txt', 'w')

# validars
linesRead = 0
linesSkipped = 0

# Format json file
output.write('[')

while 1:
	# Get the line
	record('line ' + repr(linesRead) + '\n')
	record('reading line ' + repr(linesRead) + '\n')
	line = scraperData.readline()

	# To check whether it's end of scraper data
	if not line:
		record('no more lines found.\n')
		break

	searchStart = 0
	record('Searching for content.')
	while 1:
		record('searching from column ' + repr(searchStart) + '\n')
		searchIndex = line.find('<!--', searchStart)
		if searchIndex == -1: # End of that line was reached, presumably w/o finding the content
			record('last end comment tag not found. Content not found. Skipping line ' + repr(linesRead) + '\n')
			linesSkipped += 1
			break
		else:
			record('\'<!--\' found at column ' + repr(searchIndex) + '\n')
			searchStart = searchIndex + 1

			# Looking for 'content' tag in the comments
			if line.find('content', searchIndex, searchIndex+20) >= 0:
				beg = searchIndex+4 # +4 to ignore the '<!--'
				end = line.find('-->', searchIndex, len(line))
				record('content identified at column ' + repr(searchIndex) + '\n')
				record('end found at column ' + repr(end) + '\n')

				# Cleaning!
				record('Content found. Cleaning.')
				# Strip the text of things that make json unhappy
				backslashClean = line[beg:end].replace('\\','').replace('&dsh;','') # clean out backslashes for valid json
				# Clean out link HTML...
				while backslashClean.find('<a') >= 0:
					record('found <a at line ' + repr(backslashClean.find('<a')))
					aTag = backslashClean.find('<a')
					aEndTag = backslashClean.find('</a>')
					backslashClean = backslashClean[0:aTag] + backslashClean[aEndTag+4:len(backslashClean)]

				record('content is:\n')
				record(backslashClean + '\n\n')

				# Extract useful info from the json into the profile
				profileJson = json.loads(backslashClean)
				profile = {}

				# If we see a topcard, we only have limited profile access. Scrape data this way
				if profileJson['content'].get('TopCard'):

					# Make sure they actually went to Waterloo for Systems Design Engineering at some point, then find:
					# School
					# Degree
					# Field of Study
					valid = False
					pullThisEd = False
					educations = profileJson['content']['TopCard']['educationsMpr'].get('topEducations') + profileJson['content']['TopCard']['educationsMpr'].get('moreEducations')
					for education in educations:
						if (education.get('schoolName') == "University of Waterloo"): # Went to Waterloo?
							if ('degree' in education):
								if(education.get('degree').find('Systems Design Engineering') >= 0): # SYDE mention in degree?
									valid = True
									pullThisEd = True
							if('fieldOfStudy' in education):
								if(education.get('fieldOfStudy').find('Systems Design Engineering') >= 0): # SYDE mention in FoS?
									valid = True
									pullThisEd = True
							if pullThisEd:
								 profile['school'] = education['schoolName']
								 profile['degree'] = education['degree'] if ('degree' in education) else None
								 profile['fieldOfStudy'] = education['fieldOfStudy'] if ('fieldOfStudy' in education) else None
								 pullThisEd = False



					# If profile is valid, we start looking for info
					if valid:
						record('Profile is valid SYDE.')

						# Get school info...just 'cause
						# profile['school'] = educations[0]['schoolName'] if ('school' in educations[0]) else None
						# profile['degree'] = educations[0]['degree'] if ('degree' in educations[0]) else None
						# profile['fieldOfStudy'] = educations[0]['fieldOfStudy'] if ('fieldOfStudy' in educations[0]) else None

						# Name
						profile['name'] = profileJson['content']['BasicInfo']['basic_info'].get('fullname')

						# Location
						profile['location'] = profileJson['content']['BasicInfo']['basic_info'].get('location_highlight')

						# Industry
						profile['industry'] = profileJson['content']['BasicInfo']['basic_info'].get('industry_highlight')

						# Twitter
						if 'twitterAccounts' in profileJson['content']['ContactInfo']['contact_info']:
							profile['twitter'] = profileJson['content']['ContactInfo']['contact_info']['twitterAccounts'][0].get('twitterHandle')

						# Website
						if 'websites' in profileJson['content']['ContactInfo']['contact_info']:
							profile['website'] = profileJson['content']['ContactInfo']['contact_info']['websites'][0].get('URL')

						# Jobs
						# Get company name
						headline = profileJson['content']['BasicInfo']['basic_info']['headline_highlight'] # Mix of job and Company
						if ' at ' in headline:
							# We assume his title is representative of a job + place format
							profile['headlineJob'] = headline[0:headline.find(' at ')]
							profile['headlinePlace'] = headline[headline.find(' at ')+4:len(headline)]
						else:
							# We assume he's not employed and he's given some random headline
							profile['headlineJob'] = headline
							profile['headlinePlace'] = None

						# Merge the two lists containing previous jobs
						jobs = (profileJson['content']['TopCard']['positionsMpr'].get('topCurrent') if profileJson['content']['TopCard']['positionsMpr'].get('topCurrent') else []) + (profileJson['content']['TopCard']['positionsMpr'].get('topPrevious') if profileJson['content']['TopCard']['positionsMpr'].get('topPrevious') else [])
						previousEmployers = []
						for job in jobs:
							# If the job in the list isn't the same as their headline, aka their headline is madeup  or a different company, we can add these to a list of previous employers
							if job.get('companyName') is not profile.get('headlinePlace'):
								previousEmployers.append(job.get('companyName'))

					else:
						record('Profile was not valid SYDE.')

				# If there is no TopCard, we have full profile access
				else:
					profile['topcard'] = 'yes'

				record(json.dumps(profile) + '\n\n')

				if linesRead != 0: # json formatting
					output.write(',\n')
				output.write(json.dumps(profile) + '\n')
				break

			else:
				record('content not found, continuing from column ' + repr(searchStart) + '.\n')

	linesRead += 1

# Close off json array
output.write(']')

# Post-loop comments
record('\nparse completed.\n')
record('lines parsed: ' + repr(linesRead) + '.\n')
record('lines skipped: ' + repr(linesSkipped)+ '\n')

#close files
scraperData.close()
output.close()
log.close()

# TODO non-TopCard support
# TODO Duplicate entries
# Convert to utf-8
# Where the fuck are all the school names?