import re
import requests
import sys
from bs4 import BeautifulSoup

def parse(linklist, searchlist):
	
	# Extracting lists into "list"
	links = [links.rstrip('\n') for links in open(linklist)]
	searchlist = [sl.rstrip('\n') for sl in open(searchlist)]

	N = len(links)

	tags = []
	journal = []
	titles = []
	links_data = []
	golden = []

	# List of keywords in combinition with keys, we believe to be very important in mechanistic modeling studies
	golden_keys = ["resistance", "sensitivity", "mechanism", "mechanistic", "insight", "mutation"]

	for index, link in enumerate(links):
		print "{} of {}: Link: {}".format(index+1, N, link)
		html = requests.get(link).text 				# Request by python to open to page (Internet connection required here)
		data = BeautifulSoup(html, 'html.parser') 		# bs will "crawl" the opened page
		for searchitem in searchlist:
			a = data.find(string=re.compile(searchitem))		
			if a == None:
				continue

			for golden_key in golden_keys:			
				if a.find_parent().find(string=re.compile(golden_key)) != None:
					b_1 = a.find_parent()						# Extract the entire article line
					golden.append(b_1.get_text().encode('utf-8'))			# Print text-only into the list "golden"
			b = a.find_parent()			
			tags.append(searchitem)			
			t = data.title
			journal.append(t.get_text())
			titles.append(b.get_text().encode('utf-8'))
			links_data.append(link)

	for i in range(len(titles)):
		print i, "#", tags[i], "#", journal[i], "#", titles[i], "#", links_data[i]

	if len(golden) > 0:
		for i in range(len(golden)):
			print i, "#", golden[i]
	else:
		print "No golden articles"


if __name__ == '__main__':
	if len(sys.argv) != 3:
		print "Usage: {} <link-list> <search-list>".format(sys.argv[0])
		# NZEC for chaining
		sys.exit(-1)

	parse(sys.argv[1], sys.argv[2])	

