import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import csv
from csv import QUOTE_ALL

start_url = "https://cs.uwaterloo.ca/current/programs/require/bd/depthAndBreadth"
start_resp = requests.get(start_url) 

start_page = BeautifulSoup(start_resp.text, "html.parser")
alist = start_page.find("table").find_all("a")

courses = []

def crawler(url):
  resp = requests.get(url)
  page = BeautifulSoup(resp.text, "html.parser")
  resp.close()

  for table in page.find_all("table"):
      tds = table.find_all("td")

      #Make sure it's a table about course
      if len(tds) < 3:
          continue
      
      #course name 
      code_b = tds[0].find("b")
      if not code_b:
          continue
      code_text = code_b.get_text(strip=True)

      #course id
      course_id_text = tds[1].get_text(strip=True).replace("Course ID: ", "")

      name_b = tds[2].find("b")
      name_text = name_b.get_text(strip=True) if name_b else ""

      description_text = tds[3].get_text(strip=True) if len(tds) > 3 else ""

      prereq_text = coreq_text = antireq_text = crosslist_text = ""
      for td in tds[4:]:
          i_tag = td.find("i")
          if i_tag:
              text = i_tag.get_text(strip=True)
              if text.startswith("Prereq:"):
                  prereq_text = text.replace("Prereq:", "").strip()
              elif text.startswith("Coreq:"):
                  coreq_text = text.replace("Coreq:", "").strip()
              elif text.startswith("Antireq:"):
                  antireq_text = text.replace("Antireq:", "").strip()
              elif "Cross-listed" in text:
                  crosslist_text = text.replace("(", "").replace(")", "").strip()

      courses.append({
          "code": code_text,
          "course_id": course_id_text,
          "name": name_text,
          "description": description_text,
          "prereq": prereq_text,
          "coreq": coreq_text,
          "antireq": antireq_text,
          "crosslist": crosslist_text
      })

for a in alist:
    crawler(a.get("href"))

start_resp.close()

headers = ["code", "course_id", "name", "description", "prereq", "coreq", "antireq", "crosslist"]

with open("courses.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=headers, quoting= QUOTE_ALL)
    writer.writeheader()
    writer.writerows(courses)