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

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import requests
import sys
from bs4 import BeautifulSoup

caps = "([A-Z])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov)"
digits = "([0-9])"


def split_into_sentences(text):
    text = " " + text + "  "
    text = text.replace("\n"," ")
    text = re.sub(prefixes,"\\1<prd>",text)
    text = re.sub(websites,"<prd>\\1",text)
    if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
    text = re.sub("\s" + caps + "[.] "," \\1<prd> ",text)
    text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
    text = re.sub(caps + "[.]" + caps + "[.]" + caps + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
    text = re.sub(caps + "[.]" + caps + "[.]","\\1<prd>\\2<prd>",text)
    text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
    text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
    text = re.sub(" " + caps + "[.]"," \\1<prd>",text)
    text = re.sub(digits + "[.]" + digits,"\\1<prd>\\2",text)
    if "”" in text: text = text.replace(".”","”.")
    if "\"" in text: text = text.replace(".\"","\".")
    if "!" in text: text = text.replace("!\"","\"!")
    if "?" in text: text = text.replace("?\"","\"?")
    text = text.replace(".",".<stop>")
    text = text.replace("?","?<stop>")
    text = text.replace("!","!<stop>")
    text = text.replace("<prd>",".")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    return sentences

objectives = ["to prove", "to test", "tested", "to show"]
visualizing_behaviours = ["interacted with", "interacts", "activates", "activated", "binds with", "bound", "inhibit", "inhibited", "promoter binding", "to promoter", "directly", "is not direct", "not directly"] 
biochemical_behaviours = ["phosphorylation", "acetyation", "de-acetylation", "product formation", "methylation", "transfer", "translocation", "recruitment to the"]
action_biochemical_behaviours = ["phosphorylate", "acetylate", "bind", "form complex", "suppresses", "dimerizes", "tetramerizes", "translocate", "interact", "interacted"]
oncoterms = ["upregulated in", "downregulated in", "mutated in", "mutation of", "increased survival", "proliferation", "associated with", "co-relate"]
assertions = ["levels of", "levels increased", "levels decreased", "increase in", "decrease in"]
conclusive_markers = ["we conclude", "in conclusion", "we showed that", "we show", "potential", "results", "proves", "was determined", "impact"]


def split_data_into_components(datafile):

	with open(datafile, 'r') as myfile:
    		data = myfile.read()
	sentence_load = split_into_sentences(data)
	return sentence_load

def get_objectives(load):
	objective_statements = []
	for sentence in load:
		for keyword in objectives:
			if keyword in sentence:
				objective_statements.append(sentence)
	return objective_statements


def get_behaviours(load):
	visualized_behaviours = []
	for sentence in load:
		for keyword in visualizing_behaviours:
			if keyword in sentence:
				visualized_behaviours.append(sentence)
	return visualized_behaviours

def get_biochemical_behaviours(load):
	biochemical_behaviours_seen = []
	for sentence in load:
		for keyword in biochemical_behaviours:
			if keyword in sentence:
				biochemical_behaviours_seen.append(sentence)
	return biochemical_behaviours_seen

def get_action_biochemical_behaviours(load):
	action_biochemical_behaviours_seen = []
	for sentence in load:
		for keyword in action_biochemical_behaviours:
			if keyword in sentence:
				action_biochemical_behaviours_seen.append(sentence)
	return action_biochemical_behaviours_seen

def get_oncoterms(load):
	oncoterms_seen = []
	for sentence in load:
		for keyword in oncoterms:
			if keyword in sentence:
				oncoterms_seen.append(sentence)
	return oncoterms_seen

def get_assertions(load):
	asserted = []
	for sentence in load:
		for keyword in assertions:
			if keyword in sentence:
				asserted.append(sentence)
	return asserted

def get_conclusions(load):
	conclusions = []
	for sentence in load:
		for keyword in conclusive_markers:
			if keyword in sentence:
				conclusions.append(sentence)
	return conclusions
	

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print "Usage: {} <link-list>".format(sys.argv[0])
		# NZEC for chaining
		sys.exit(-1)

	y = split_data_into_components(sys.argv[1])

	objectives = get_objectives(y)
	print "OBJECTIVES", objectives
	behaviours = get_behaviours(y)
	biochemical_behaviours = get_biochemical_behaviours(y)
	action_biochemical_behaviours = get_action_biochemical_behaviours(y)
	print "MECHANISTIC BEHAVIOURS", behaviours, biochemical_behaviours, action_biochemical_behaviours
	assertions = get_assertions(y)
	print "ASSERTIONS", assertions
	oncoterms = get_oncoterms(y)
	print "ONCOTERMS", oncoterms
	conclusions = get_conclusions(y)
	print "CONCLUSIONS", conclusions
