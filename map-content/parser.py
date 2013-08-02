import json
import simplejson
from googlemaps import GoogleMaps
from urllib2 import urlopen
import HTMLParser
htmlparser = HTMLParser.HTMLParser()

# Functions
def record(string):
	print string
	log.write(string)

# Files
scraperData = open('items.txt', 'r')
output = open('output.js', 'w')
log = open('log.txt', 'w')
idListFile = open('recorded.txt', 'r')
listString = json.loads(idListFile.read())

# vars
url = 'https://maps.googleapis.com/maps/api/place/textsearch/json?query=%s&sensor=false&key=AIzaSyB0Ov2yUS0UKwn1gZZQHpkqCMh4n_iRhtk'
key = 'AIzaSyB0Ov2yUS0UKwn1gZZQHpkqCMh4n_iRhtk'

linesRead = 0
linesValid = 0
fullProfiles = 0

hasNoTop = 0
hasBothTop = 0

# Format json file
output.write('var profiles = [')

while 1 and linesRead < 50:
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
			break
		else:
			record('\'<!--\' found at column ' + repr(searchIndex) + '\n')
			searchStart = searchIndex + 1

			# Looking for 'content' tag in the comments
			if line.find('content', searchIndex, searchIndex+20) >= 0:
				linesValid += 1
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
					record('found <a at line ' + repr(backslashClean.find('<a')) + '\n')
					aTag = backslashClean.find('<a')
					aEndTag = backslashClean.find('</a>')
					backslashClean = backslashClean[0:aTag] + backslashClean[aEndTag+4:len(backslashClean)]

				record('content is:\n')
				record(backslashClean + '\n\n')

				# Extract useful info from the json into the profile
				profileJson = json.loads(backslashClean)
				profile = {}

				if 'TopCard' in profileJson['content']:
					# We only have basic info format
					record('Basic profile.\n')
					fullProfiles += 1
					fullProfile = False
					personId = profileJson['content']['profile_v2_megaphone_articles']['basic_info'].get('memberID')
				else:
					# We have full profile format
					record('Full profile.\n')
					fullProfile = True
					personId = profileJson['content']['RightTop']['discovery'].get('vieweeId')

				# Check to see if this record is a duplicate of one already recorded
				if personId in idList:
					record('Profile is already recorded.\n')
					newProfile = False
				else:
					record('New profile.\n')
					newProfile = True
					idList.append(personId)
					idListFile.write(personId)

				# Make sure they actually went to Waterloo for Systems Design Engineering at some point, then find:School, Degree, Field of Study
				isSYDE = False
				pullThisEd = False
				educations = profileJson['content']['Education']['educationsMpr'].get('educations') if fullProfile else (profileJson['content']['TopCard']['educationsMpr'].get('topEducations') + profileJson['content']['TopCard']['educationsMpr'].get('moreEducations'))
				for education in educations:
					if (education.get('schoolName') == "University of Waterloo"): # Went to Waterloo?
						if ('degree' in education):
							if(education.get('degree').find('Systems Design Engineering') >= 0): # SYDE mention in degree?
								isSYDE = True
								pullThisEd = True
						if('fieldOfStudy' in education):
							if(education.get('fieldOfStudy').find('Systems Design Engineering') >= 0): # SYDE mention in FoS?
								isSYDE = True
								pullThisEd = True
						if pullThisEd:
							 profile['school'] = education['schoolName']
							 profile['degree'] = education['degree'] if ('degree' in education) else None
							 profile['fieldOfStudy'] = education['fieldOfStudy'] if ('fieldOfStudy' in education) else None
							 pullThisEd = False

				# Now, if they are a new profile AND it is valid:
				if newProfile and isSYDE:
					if fullProfile:
						asdf = 1
						# Name
						# profile['name'] = profileJson['content']['RightTop']['discovery']['viewee'].get('firstName') + ' ' + profileJson['content']['RightTop']['discovery']['viewee'].get('lastName')
						#industry

						#website
						#twitter
						#jobs
						#location
					else: # AKA We only have limited profile
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
						profile['headline'] = profileJson['content']['BasicInfo']['basic_info']['headline_highlight'] # Mix of job and Company
						if ' at ' in profile['headline']:
							profile['title'] = profile['headline'][0:profile['headline'].find(' at ')]
							profile['employer'] = profile['headline'][profile['headline'].find(' at ')+4:len(profile['headline'])]
						# if ' at ' in headline:
							# We assume his title is representative of a job + place format
						# 	profile['headlineJob'] = headline[0:headline.find(' at ')]
						# 	profile['headlinePlace'] = headline[headline.find(' at ')+4:len(headline)]
						# else:
						# 	# We assume he's not employed and he's given some random headline
						# 	profile['headlineJob'] = headline
						# 	profile['headlinePlace'] = None

						# Extract position and title out of headline, if possible
						# if 'firstTopCurrentPosition' in profileJson['content']['TopCard']['positionsMpr']:
						# 	if profile['headline'].find(' at ' + profileJson['content']['TopCard']['positionsMpr']['firstTopCurrentPosition'].get('companyName')) >= 0:
						# 		profile['headTitle'] = profile['headline'][0:profile['headline'].find(' at ' + profileJson['content']['TopCard']['positionsMpr']['firstTopCurrentPosition'].get('companyName'))]
						# 	else:
						# 		profile['headTitle'] = profile['headline']
						# 	profile['headCompany'] = profileJson['content']['TopCard']['positionsMpr']['firstTopCurrentPosition'].get('companyName')

						# if 'topCurrent' in profileJson['content']['TopCard']['positionsMpr']:
						# 	for position in profileJson['content']['TopCard']['positionsMpr']['topCurrent']:
						# 		if profile['headline'].find(' at ' + position.get('companyName')) >= 0:
						# 			profile['headTitle'] = profile['headline'][0:profile['headline'].find(' at ' + position.get('companyName'))]
						# 			profile['headCompany'] = position.get('companyName')
						# 		else:
						# 			profile['headTitle'] = profile['headline']

						searchString = (profile['employer'] + ' near ' + profile['location']) if ('employer' in profile) else (profile['location'])
						record('Search for: ' + searchString + '\n')

						cleanSearchString = htmlparser.unescape(htmlparser.unescape(searchString)).encode('utf-8')
						addrString = cleanSearchString.replace(' ', '+')
						request = url % (addrString)
						record('Request string: ' + request + '\n')

						response = urlopen(request)
						responseobj = simplejson.load(response)
						record('Response:\n' + simplejson.dumps(responseobj) + '\n')

						if responseobj['status'] != 'OK':
							record('Response not OK\n')
							record('status: ' + responseobj['status'] + '\n')
						else:
							if 'results' in responseobj:
								mainResult = responseobj['results'][0]
								record('Main Result:\n' +  simplejson.dumps(responseobj['results'][0]) + '\n')
								profile['mapLocation'] = {}
								profile['mapLocation']['name'] = mainResult['name']
								profile['mapLocation']['address'] = mainResult['formatted_address']
								profile['mapLocation']['lat'] = mainResult['geometry']['location']['lat']
								profile['mapLocation']['lng'] = mainResult['geometry']['location']['lng']

						if 'topPrevious' in profileJson['content']['TopCard']['positionsMpr']:
							jobs = profileJson['content']['TopCard']['positionsMpr'].get('topPrevious')
							profile['previousEmployers'] = []
							first = True
							for job in jobs:
								profile['previousEmployers'].append(job.get('companyName'))

						# Write it to output
						record(json.dumps(profile) + '\n\n')
						if linesRead != 0: # json formatting
							output.write(',\n')
						output.write(json.dumps(profile) + '\n')

				# End of 'if newProfile'
				break

			else:
				record('content not found, continuing from column ' + repr(searchStart) + '.\n')

	linesRead += 1

# Close off json array
output.write(']')

# Post-loop comments
record('\nparse completed.\n')
record('lines parsed: ' + repr(linesRead) + '.\n')
record('lines valid: ' + repr(linesValid)+ '\n')
record('Unique profiles: ' + repr(len(idList)) + '\n')

record('has no top: ' + repr(hasNoTop)+ '\n')

#close files
scraperData.close()
output.close()
log.close()

# TODO non-TopCard support
# TODO Duplicate entries
# Convert to utf-8
# Where the fuck are all the school names?