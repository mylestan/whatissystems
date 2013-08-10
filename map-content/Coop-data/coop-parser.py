# imports
import simplejson as json
from urllib2 import urlopen
import csv

# methods
# logging function that writes to a log file and optionally to console
def rec(msg, printInConsole = False):
	log.write(msg)
	if printInConsole:
		print msg

# function which handles map requests for the given string, and returns the object
def mapsRequest(string):
	rec('gmaps request for string: ' + string + '\n')
	request = url % searchString.replace(' ', '+')
	rec('request string: ' + request + '\n')
	response = urlopen(request)
	return json.load(response)


# vars
url = 'https://maps.googleapis.com/maps/api/place/textsearch/json?query=%s&sensor=false&key=AIzaSyB0Ov2yUS0UKwn1gZZQHpkqCMh4n_iRhtk'

# Open all of the co-op data files
fileNames = []
fileNames.append("Systems Design Class of 2014 - Employment - Winter 2010 (1A).csv")
fileNames.append("Systems Design Class of 2014 - Employment - Fall 2010 (1B).csv")
fileNames.append("Systems Design Class of 2014 - Employment - Summer 2011 (2A).csv")
fileNames.append("Systems Design Class of 2014 - Employment - Winter 2012 (2B).csv")
fileNames.append("Systems Design Class of 2014 - Employment - Fall 2012 (3A).csv")
fileNames.append("Systems Design Class of 2014 - Employment - Summer 2013 (3B).csv")

# Open others
log = open("log.txt", 'w')

# Open our end result data file
pf = open('coop-profiles.txt', 'r')

# Read the result data into an object
with open('coop-profiles.txt') as pf:
	profiles = json.loads(pf.read())
	if not profiles:
		profiles = {}

# Iterate through the co-op data files
for f in range(len(fileNames)):
	rec('reading file: ' + fileNames[f] + '\n', True)
	with open(fileNames[f]) as csvFile:
		fileReader = csv.reader(csvFile)
		# Read first line, and print to confirm that these match:
		cols = ['name', 'termNumber', 'isWorking', 'title', 'employer', 'jobPrevious', 'employerPrevious', 'latlng', 'city', 'province', 'country']
		fileCols = fileReader.next()
		# rec('file columns: ' + fileCols + '\n')
		# fileColsArray = fileCols.split(',')

		helperCols = fileReader.next()
		# rec('helper columns: ' + helperCols + '\n')
		# helperColsArray = helperCols.split(',')

		rec('Ensuring that our info lines up. If the following dont align, theres an issue:\n')
		for i in range(len(cols)):
			rec(cols[i])
			rec('\t')
			rec(fileCols[i])
			rec('\t')
			rec(helperCols[i])
			rec('\n')

		# Iterate through every line in the data file
		for infoArray in fileReader:
			rec('reading a new line\n', True)

			# Turn the CSV line into an array
			name = infoArray[0]
			termNo = infoArray[1]
			working = True if infoArray[2] == 'Yes' else False
			title = infoArray[3]
			employer = infoArray[4]
			jobPrevious = infoArray[5]
			companyPrevious = infoArray[6]
			city = infoArray[8]
			prov = infoArray[9]
			country = infoArray[10]

			# if name doesn't exist, make it
			if not name in profiles:
				profiles[name] = {}

			# Create an object for the term they are in
			if not termNo in profiles[name]:
				profiles[name][termNo] = {}

			# Add the info. Overwrite in this case
			profiles[name][termNo]['woring'] = working
			profiles[name][termNo]['title'] = title
			profiles[name][termNo]['employer'] = employer
			profiles[name][termNo]['jobPrevious'] = jobPrevious
			profiles[name][termNo]['companyPrevious'] = companyPrevious
			profiles[name][termNo]['city'] = city
			profiles[name][termNo]['province'] = prov
			profiles[name][termNo]['country'] = country

			# if map-location doesn't exist, write it
			if not 'map-location' in profiles[name][termNo]:

				searchString = (employer + ', ' + ', '.join([city, prov, country]))
				responseObject = mapsRequest(searchString)
				status = responseObject['status']
				if status == 'OK':
					rec('gmaps request successful.\n')
					# Make the map location object
					profiles[name][termNo]['mapLocation'] = {}

					# Take the first one. FAITH IN THE GOOGLES!
					first = responseObject['results'][0]
					profiles[name][termNo]['mapLocation']['name'] = first['name']
					profiles[name][termNo]['mapLocation']['address'] = first['formatted_address']
					profiles[name][termNo]['mapLocation']['lat'] = first['geometry']['location']['lat']
					profiles[name][termNo]['mapLocation']['lng'] = first['geometry']['location']['lng']
				elif status == 'ZERO_RESULTS':
					# The company wasn't found. So we just look at the location

				else:
					rec('gmaps request failed. reason: \n' + status)
				# End of Status elif chain
			# End of if map-location
		# End of infoArray in fileReader
	# End of with statement for csv
# End of file loop


# Report some figures
# Open result data file, write, Close
pf = open('coop-profiles.txt', 'w')
pf.write(json.dumps(profiles))
pf.close()

log.close()

# ???
# PROFIT

# TODO
# use csv.reader....I don't think it's recognizing null csv spaces
# What if no results are returned? Can we just search location in that situation?
# make a function that encapsulates the smarts of the maps request. RECURSION LIKE ITS HOT