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
	request = url % string.replace(' ', '+')
	rec('request string: ' + request + '\n')
	response = urlopen(request)
	return json.load(response)

# function to return the map-location object for a co-op term, given the company and the location. keep this logic out of the main loop
def getLocation(city, prov, country, company = None):
	rec('getting map location\n')
	if company:
		rec('\tcompany: ' + company + '\n')
	rec ('\tlocation: ' + ', '.join([city,prov,country]) + '\n')

	# First we try to locate the company in the area
	reqString = ', '.join([company, city, prov, country]) if company else ', '.join([city, prov, country])
	response = mapsRequest(reqString)

	status = response['status']
	if status == 'OK':
		rec('\tresponse OK\n')
		# Take the first one. FAITH IN THE GOOGLES!
		first = response['results'][0]
		location = {}
		location['name'] = first['name']
		location['address'] = first['formatted_address']
		location['lat'] = first['geometry']['location']['lat']
		location['lng'] = first['geometry']['location']['lng']
		return location
	elif status == "ZERO_RESULTS":
		rec('\tresponse no results, trying again for location\n')
		return getLocation(city, prov, country)
	else:
		return None
		rec('\tresponse error: ' + status + '\n')




# vars
url = 'https://maps.googleapis.com/maps/api/place/textsearch/json?query=%s&sensor=false&key=AIzaSyB0Ov2yUS0UKwn1gZZQHpkqCMh4n_iRhtk'

fileNames = []
fileNames.append("Systems Design Class of 2014 - Employment - Winter 2010 (1A).csv")
fileNames.append("Systems Design Class of 2014 - Employment - Fall 2010 (1B).csv")
fileNames.append("Systems Design Class of 2014 - Employment - Summer 2011 (2A).csv")
fileNames.append("Systems Design Class of 2014 - Employment - Winter 2012 (2B).csv")
fileNames.append("Systems Design Class of 2014 - Employment - Fall 2012 (3A).csv")
fileNames.append("Systems Design Class of 2014 - Employment - Summer 2013 (3B).csv")



# Open log
log = open("log.txt", 'w')

# Read the result data into an object
with open('coop-profiles.txt') as pf:
	profiles = json.loads(pf.read())
	if not profiles:
		profiles = {}



# THE FUN BEGINS HERE!!!
# Iterate through the co-op data files
for f in range(len(fileNames)):
	rec('reading file: ' + fileNames[f] + '\n', True)
	with open(fileNames[f]) as csvFile:
		fileReader = csv.reader(csvFile)
		# Read first line, and print to confirm that these match:
		cols = ['name', 'termNumber', 'isWorking', 'title', 'employer', 'jobPrevious', 'employerPrevious', 'latlng', 'city', 'province', 'country', 'typeOfWork', 'industry', 'sector']
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
			rec('reading a new line\n')

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
			profiles[name][termNo]['working'] = working
			profiles[name][termNo]['title'] = title
			profiles[name][termNo]['employer'] = employer
			profiles[name][termNo]['jobPrevious'] = jobPrevious
			profiles[name][termNo]['companyPrevious'] = companyPrevious
			profiles[name][termNo]['city'] = city
			profiles[name][termNo]['province'] = prov
			profiles[name][termNo]['country'] = country

			# if map-location doesn't exist, write it
			if not 'map-location' in profiles[name][termNo]:
				location = getLocation(city, prov, country, employer)
				if location:
					profiles[name][termNo]['mapLocation'] = location

			# End of if map-location
		# End of infoArray in fileReader
	# End of with statement for csv
# End of file loop


# Report some figures
# Open result data file, write, Close
with open('coop-profiles.txt', 'w') as pf:
	pf.write(json.dumps(profiles))

log.close()

# ???
# PROFIT

# TODO