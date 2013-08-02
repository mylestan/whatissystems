import simplejson as json
from googlemaps import GoogleMaps
from urllib2 import urlopen
import HTMLParser
htmlparser = HTMLParser.HTMLParser()

# Functions
def record(string):
	print string
	logFile.write(string)

# Files
dataFile = open('items.txt', 'r')
profilesFile = open('profiles.js', 'r')
logFile = open('log.txt', 'w')

# get profiles, put them in an object. if DNE create
profiles = json.loads(profilesFile.read())
if not profiles:
	profiles = {}
profilesFile.close() # open it up for writing later

# vars
url = 'https://maps.googleapis.com/maps/api/place/textsearch/json?query=%s&sensor=false&key=AIzaSyB0Ov2yUS0UKwn1gZZQHpkqCMh4n_iRhtk'
key = 'AIzaSyB0Ov2yUS0UKwn1gZZQHpkqCMh4n_iRhtk'

 # Counting vars
linesRead = 0
linesValid = 0
validProfiles = 0
basicProfiles = 0
fullProfiles = 0
mapRequestsMade = 0
mapRequestsSuccessful = 0

requestMax = 50
requestCount = 0

# Loop through each record/line in the scraper data
for line in dataFile:
	linesRead += 1
	contentFound = False
	record('line ' + repr(linesRead) + '\n')
	record('reading line ' + repr(linesRead) + '\n')

	# Search for the comment section that contains all the goodies
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

				content = json.loads(backslashClean)['content']
				contentFound = True
				linesValid += 1

				break


	# If there was valid content, we check to see if it was basic or full profile
	if contentFound is True:
		# check type so you can check the education
		if 'TopCard' in content:
			# We only have basic info format
			record('Basic profile.\n')
			fullProfiles += 1
			fullProfile = False
			personId = repr(content['profile_v2_megaphone_articles']['basic_info'].get('memberID'))
		else:
			# We have full profile format
			record('Full profile.\n')
			fullProfile = True
			personId = repr(content['RightTop']['discovery'].get('vieweeId'))

	# Check to see if their education is correct
	isSYDE = False
	educations = content['Education']['educationsMpr'].get('educations') if fullProfile else (content['TopCard']['educationsMpr'].get('topEducations') + content['TopCard']['educationsMpr'].get('moreEducations'))
	for education in educations:
		if (education.get('schoolName') == "University of Waterloo"): # Went to Waterloo?
			if ('degree' in education):
				if(education.get('degree').find('Systems Design Engineering') >= 0): # SYDE mention in degree?
					isSYDE = True
					validProfiles += 1
			if('fieldOfStudy' in education):
				if(education.get('fieldOfStudy').find('Systems Design Engineering') >= 0): # SYDE mention in FoS?
					isSYDE = True
					validProfiles += 1

	# Now if content is found and it's valid, we check to see if we create a new ID or add to an existing one
	if contentFound and isSYDE:
		# We create a new profile if it doesn't already exist
		if personId not in profiles:
			profiles[personId] = {}
			profiles[personId]['hasFullProfile'] = False
			profiles[personId]['hasBasicProfile'] = False

		# If this is a full profile, we pull different information
		if fullProfile:
			fullProfiles += 1
			profiles[personId]['hasFullProfile'] = True
		# If not, it's a simple profile, and we pull other inormation
		else:
			basicProfiles += 1
			profiles[personId]['hasBasicProfile'] = True
			# Name
			profiles[personId]['name'] = content['BasicInfo']['basic_info'].get('fullname')
			# Location
			profiles[personId]['location'] = content['BasicInfo']['basic_info'].get('location_highlight')
			# Industry
			profiles[personId]['industry'] = content['BasicInfo']['basic_info'].get('industry_highlight')
			# Twitter
			if 'twitterAccounts' in content['ContactInfo']['contact_info']:
				profiles[personId]['twitter'] = content['ContactInfo']['contact_info']['twitterAccounts'][0].get('twitterHandle')

			profiles[personId]['headline'] = content['BasicInfo']['basic_info']['headline_highlight'] # Mix of job and Company
			if ' at ' in profiles[personId]['headline']:
				profiles[personId]['title'] = profiles[personId]['headline'][0:profiles[personId]['headline'].find(' at ')]
				profiles[personId]['employer'] = profiles[personId]['headline'][profiles[personId]['headline'].find(' at ')+4:len(profiles[personId]['headline'])]

			# Now, for Map request part!
			if ('mapLocation' not in profiles[personId]):
				mapRequestsMade += 1
				searchString = (profiles[personId]['employer'] + ' near ' + profiles[personId]['location']) if ('employer' in profiles[personId]) else (profiles[personId]['location'])
				record('Search for: ' + searchString + '\n')

				cleanSearchString = htmlparser.unescape(htmlparser.unescape(searchString)).encode('utf-8')
				addrString = cleanSearchString.replace(' ', '+')
				request = url % (addrString)
				record('Request string: ' + request + '\n')

				response = urlopen(request)
				responseobj = json.load(response)
				record('Response:\n' + json.dumps(responseobj) + '\n')

				if responseobj['status'] != 'OK':
					record('Response not OK\n')
					record('status: ' + responseobj['status'] + '\n')
				else:
					mapRequestsSuccessful += 1
					if 'results' in responseobj:
						mainResult = responseobj['results'][0] # Use the first one. Trust mother Google
						record('Main Result:\n' +  json.dumps(responseobj['results'][0]) + '\n')
						profiles[personId]['mapLocation'] = {}
						profiles[personId]['mapLocation']['name'] = mainResult['name']
						profiles[personId]['mapLocation']['address'] = mainResult['formatted_address']
						profiles[personId]['mapLocation']['lat'] = mainResult['geometry']['location']['lat']
						profiles[personId]['mapLocation']['lng'] = mainResult['geometry']['location']['lng']

record('Lines Read: ' + repr(linesRead))
record('Lines Valid: ' + repr(linesValid))
record('Valid Profiles: ' + repr(validProfiles))
record('Basic Profiles: ' + repr(basicProfiles))
record('Full Profiles: ' + repr(fullProfiles))
record('Map Requests Made: ' + repr(mapRequestsMade))
record('Map Requests Successful: ' + repr(mapRequestsSuccessful))

profilesFile = open('profiles.js', 'w')
profilesFile.write(json.dumps(profiles))
profilesFile.close()

dataFile.close()
logFile.close()

