# Parser - takes the csv from the Google spreadsheet and spits out a js file which can be loaded into the application

# Imports
import simplejson as json
from urllib2 import urlopen
import csv

# vars
url = 'https://maps.googleapis.com/maps/api/place/textsearch/json?query=%s&sensor=false&key=AIzaSyB0Ov2yUS0UKwn1gZZQHpkqCMh4n_iRhtk'

# Log
log = open('log.txt', 'w')

# Bring in existing profiles
f = open('profiles.txt', 'r')
profiles = json.loads(unicode(f.read()))
if not profiles:
	profiles = {}
f.close()


with open('Systems Design Exchange Locations (Responses) - Form Responses.csv') as file:
	reader = csv.reader(file)

	header = reader.next()
	# Timestamp,What is your name?,What year are you?,What School Did you go to?,What country was the school in?,What term did you go in?
	print 'These should align:\n'
	print 'timestamp:\t' + header[0] + '\n'
	print 'name\t' + header[1] + '\n'
	print 'year\t' + header[2] + '\n'
	print 'school\t' + header[3] + '\n'
	print 'country\t' + header[4] + '\n'
	print 'term\t' + header[5] + '\n'

	for line in reader:
		name = line[1]
		if not name in profiles:
			profile = {}
			profile['school'] = line[3]
			profile['country'] = line[4]
			profile['year'] = unicodeline[2]
			profile['term'] = line[5]

			profiles[name] = profile
		else:
			profile = profiles[name]

		if not 'mapLocation' in profiles[name]:
			string = (profile['school'] + ' ' + profile['country']).replace(' ','+').encode('utf-8')
			request = url % string
			response = json.load(urlopen(request))
			if response['status'] == 'OK':
				first = response['results'][0]
				location = {}
				location['name'] = first['name']
				location['address'] = first['formatted_address']
				location['lat'] = first['geometry']['location']['lat']
				location['lng'] = first['geometry']['location']['lng']
				profile[name]['mapLocation'] = location

			elif response['status'] == 'OVER_QUERY_LIMIT':
				print 'over query limit :('
	# End for lines in reader

# End of open data file
log.close()


# Write the profiles to file
pfile = open('profiles.txt', 'w')
pfile.write(json.dumps(profiles))
pfile.close()

