# _*_ coding: utf-8

import re
import requests
import sys
from bs4 import BeautifulSoup
from selenium import webdriver
import xlsxwriter

class Article(object):
  def __init__(self):
    self.tag = None
    self.journal = None
    self.title = None
    self.link = None

def save_list_to_xlsx(file_name, titles_list, relevant_titles_list, tags, journal, titles, links_data):
  with xlsxwriter.Workbook(file_name) as workbook:
    titles_ws = workbook.add_worksheet("Data")
    
    for colNum, h in enumerate(["Tag", "Journal", "Title", "Link"]):
      titles_ws.write(0, colNum, h)

    for index in xrange(len(titles_list)):
      titles_ws.write(index + 1, 0, tags[index])    
      titles_ws.write(index + 1, 1, journal[index])   
      titles_ws.write(index + 1, 2, titles[index])    
      titles_ws.write(index + 1, 3, links_data[index])

    #for index, article in enumerate(articles):
    # titles_ws.write(index + 1, 0, article.tag)
    # titles_ws.write(index + 1, 1, article.journal)
    # titles_ws.write(index + 1, 2, article.title)
    # titles_ws.write(index + 1, 3, article.link)


def parse(linklist, searchlist, file_name):
  driver = None
  try:
    driver = webdriver.Chrome("./chromedriver")

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
      driver.get(link)
      html = unicode(driver.page_source.encode("utf-8"), "utf-8")
      data = BeautifulSoup(html, 'html.parser')     # bs will "crawl" the opened page
      for searchitem in searchlist:
        a = data.find(string=re.compile(searchitem))    
        if a == None:
          continue

        for golden_key in golden_keys:      
          if a.find_parent().find(string=re.compile(golden_key)) != None:
            b_1 = a.find_parent()           # Extract the entire article line
            golden.append(b_1.get_text())     # Print text-only into the list "golden"
        
        #article = Article()
        #article.tag = searchitem
        #article.journal = t.get_text()
        #article.title = b.get_text().encode('utf-8')
        #article.link = link
        #articles.append(article)
        b = a.find_parent()     
        tags.append(searchitem)     
        t = data.title
        journal.append(t.get_text())
        titles.append(b.get_text())
        links_data.append(link)

    save_list_to_xlsx(file_name, titles, golden, tags, journal, titles, links_data)

  finally:
    if driver != None:
      driver.close()


if __name__ == '__main__':  
  if len(sys.argv) != 4:
    print "Usage: {} <link-list> <search-list> <data.xlsx>".format(sys.argv[0])
    # NZEC for chaining
    sys.exit(-1)

  parse(sys.argv[1], sys.argv[2], sys.argv[3])