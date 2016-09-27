import re
import requests
from sys import argv
from bs4 import BeautifulSoup

# Input argument 1: List of links to websites 2: List of key searchs
script, linklist, searchlist = argv

# Extracting lists into "list"
links = [links.rstrip('\n') for links in open(linklist)]
sl = [sl.rstrip('\n') for sl in open(searchlist)]

tags = []
journal = []
titles = []
links_data = []
golden = []

# List of keywords in combinition with keys, we believe to be very important in mechanistic modeling studies
golden_keys = ["resistance", "sensitivity", "mechanism", "mechanistic", "insight", "mutation"]


for i in range(len(links)): 					
	link = links[i] 					
	html = requests.get(link).text 				# Request by python to open to page (Internet connection required here)
	data = BeautifulSoup(html, 'html.parser') 		# bs will "crawl" the opened page
	for j in range(len(sl)): 				
		a = data.find(string=re.compile(sl[j]))		
		if a != None:
			for x in range(len(golden_keys)):	
				if a.find_parent().find(string=re.compile(golden_keys[x])) != None:
					b_1 = a.find_parent()						# Extract the entire article line
					golden.append(b_1.get_text().encode('utf-8'))			# Print text-only into the list "golden"
			b = a.find_parent()			
			tags.append(sl[j])			
			t = data.title
			journal.append(t.get_text())
			titles.append(b.get_text().encode('utf-8'))
			links_data.append(links[i])

for i in range(len(titles)):
	print i, "#", tags[i], "#", journal[i], "#", titles[i], "#", links_data[i]

if len(golden) > 0:
	for i in range(len(golden)):
		print i, "#", golden[i]
else:
	print "No golden articles"
