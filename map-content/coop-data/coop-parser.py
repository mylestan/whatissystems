# imports
import simplejson as json
from urllib2 import urlopen, URLError
from datetime import datetime
import csv
import hashlib

# Open log
log = open("log.txt", 'w')

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

	try:
		response = urlopen(request)
	except URLError, e:
		rec('URL request failed. Reason: ' + e.reason)
	else:
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
		if company:
			rec('\tresponse no results, trying again for location\n')
			return getLocation(city, prov, country)
		else:
			rec('\tresponse no results, and no company provided. returning none. Review this entry.\n')
			return None
	else:
		rec('\tresponse error: ' + status + '\n')
		return None



# vars
url = 'https://maps.googleapis.com/maps/api/place/textsearch/json?query=%s&sensor=false&key=AIzaSyB0Ov2yUS0UKwn1gZZQHpkqCMh4n_iRhtk'

fileNames = []

# 2014
fileNames.append("Systems Design Engineering Class of 2014 - Employment - Winter 2010 (1A).csv")
fileNames.append("Systems Design Engineering Class of 2014 - Employment - Fall 2012 (3A).csv")
fileNames.append("Systems Design Engineering Class of 2014 - Employment - Summer 2011 (2A).csv")
fileNames.append("Systems Design Engineering Class of 2014 - Employment - Summer 2013 (3B).csv")
fileNames.append("Systems Design Engineering Class of 2014 - Employment - Winter 2010 (1A).csv")
fileNames.append("Systems Design Engineering Class of 2014 - Employment - Winter 2012 (2B).csv")

# 2015
fileNames.append("Systems Design Engineering Class of 2015 - Employment - %231 (1A, Winter 2011).csv")
fileNames.append("Systems Design Engineering Class of 2015 - Employment - %232 (1B, Fall 2011).csv")
fileNames.append("Systems Design Engineering Class of 2015 - Employment - %233 (2A, Summer 2012).csv")
fileNames.append("Systems Design Engineering Class of 2015 - Employment - %234 (2B, Winter 2013).csv")
fileNames.append("Systems Design Engineering Class of 2015 - Employment - %235 (3A, Fall 2013).csv")

# 2016
fileNames.append("Systems Design Engineering Class of 2016 - Employment - %231 (1A, Winter 2012).csv")
fileNames.append("Systems Design Engineering Class of 2016 - Employment - %232 (1B, Fall 2012).csv")
fileNames.append("Systems Design Engineering Class of 2016 - Employment - %233 (2A, Summer 2013).csv")
fileNames.append("Systems Design Engineering Class of 2016 - Employment - %234 (2B, Winter 2014).csv")

# 2017
fileNames.append("Systems Design Engineering Class of 2017 - Employment - %231 (1A, Winter 2013).csv")
fileNames.append("Systems Design Engineering Class of 2017 - Employment - %232 (1B, Fall 2013).csv")

# 2018
fileNames.append("Systems Design Engineering Class of 2018 - Employment - %231 (1A, Winter 2014).csv")

# Read the result data into an object
with open('coop-profiles.txt') as pf:
	profiles = json.loads(pf.read())
	if not profiles:
		profiles = {}

# Create a csv writer for putting the data into a csv
pfcsv = open("coop-profiles.csv", "wb")
pfwriter = csv.writer(pfcsv, delimiter = ",", quotechar = '"', quoting = csv.QUOTE_MINIMAL)

# THE FUN BEGINS HERE!!!
# Iterate through the co-op data files
for f in range(len(fileNames)):
	rec('reading file: ' + fileNames[f] + '\n', True)
	with open(fileNames[f]) as csvFile:
		fileReader = csv.reader(csvFile)
		# Read first line, and print to confirm that these match:
		#cols = ['name', 'termNumber', 'isWorking', 'title', 'employer', 'jobPrevious', 'employerPrevious', 'latlng', 'city', 'province', 'country', 'typeOfWork', 'industry', 'sector']

		fileCols = fileReader.next() # First row is the titles: ignore
		propertyCols = fileReader.next() # second row is the technical property names: use this to build the properties!
		helperCols = fileReader.next() # Third row is the helper text: ignore

		# Iterate through every line in the data file
		for infoArray in fileReader:
			rec('reading a new line\n')

			# Read the row into a dict
			row={}
			for colIndex in range(len(propertyCols)):
				row[propertyCols[colIndex]] = infoArray[colIndex] # For each column in the sheet, we make a property for the 'row' with the appropriate property name.

			# We assume that the row has these properties. They are necessary for creating the JSON structure
			name = row['name']
			year = row['year']
			term = row['term']
			termNumber = row['termNumber']

			nameHash = hashlib.sha224(name).digest().encode("hex") # hash the name
			termHash = hashlib.sha224(year + term).digest().encode("hex") # Hash the time of the term

			if not nameHash in profiles: # if name doesn't exist, make it
				profiles[nameHash] = {}

			if not termHash in profiles[nameHash]: # If term doesn't exist, make it
				profiles[nameHash][termHash] = {}

			# Write all the properties into an object.
			for propertyKey in row: # Create or update all of the properties in the term
				if propertyKey is not 'name': # We do not add their name to the list. PRIVACY!
					profiles[nameHash][termHash][propertyKey] = row[propertyKey]

			if not 'mapLocation' in profiles[nameHash][termHash]: # if map-location doesn't exist, write it
				location = getLocation(row['city'], row['province'], row['country'], row['employer'])
				if location:
					profiles[nameHash][termHash]['mapLocation'] = location
				else:
					rec('no location could be found for ' + row['name'] + '. Please resolve this row.\n')

			if 'mapLocation' in profiles[nameHash][termHash]:
				# write all of the important into into a the csv file as well - this is for trasferring into a database if you wanted.
				p = profiles[nameHash][termHash] # for ease
				# calculate the iso date time format
				if p['term'] == 'winter':
					m = 1
				elif p['term'] == 'summer':
					m = 5
				else:
					m = 9
				isoDateTime = datetime(int(p['year']), m, 1).isoformat("T") + "+00:00"
				pString = [nameHash, termHash, p['classYear'], isoDateTime, p['termNumber'], p['mapLocation']['lat'], p['mapLocation']['lng'], p['title'], p['employer'], p['employerUrl'], p['city'], p['province'], p['country'], p['industry'], p['description']]
				pfwriter.writerow(pString)

		# End of infoArray in fileReader
	# End of with statement for csv
# End of file loop


# Report some figures
# Open result data file, write, Close
pf = open('coop-profiles.txt', 'w')
pf.write(json.dumps(profiles))
pf.close()

# close the csv
pfcsv.close()

log.close()
