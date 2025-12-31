import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

start_url = "https://cs.uwaterloo.ca/current/programs/require/bd/depthAndBreadth"
start_resp = requests.get(start_url) 

start_page = BeautifulSoup(start_resp.text, "html.parser")
alist = start_page.find("table").find_all("a")

def crawler(url):
  with requests.get(url) as resp:
    page = BeautifulSoup(resp.text, "html.parser")
    print(resp.text[:20]) # Show we get the data




for a in alist:
    #crawler(a.get("href"))
    print(a)

start_resp.close()




