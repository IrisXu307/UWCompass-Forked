from bs4 import BeautifulSoup
import re
from lxml import html
import pandas as pd
import json
import course_info as cc

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def extract_grade_or_level(rule: str):
    grade_match = re.search(r'(\d+)%', rule)
    if grade_match:
        return int(grade_match.group(1))
    
    level_match = re.search(r'\b[1-4][AB]\b', rule)
    if level_match:
        return level_match.group(0)
    
    # If nothing found
    print("line 16: " + rule) # test 1
    raise ValueError("No grade or level identified")

def check_logic_type(rule):
    if "not" in rule:
        return "NOT"
    elif any(phrase in rule for phrase in [
        "all of",
        "each of",
        "complete:",
        "completed:",
        "complete the following",
        "completed the following",
        "enroll in the following",
        "enrolled in the following"]):
        return "AND"
    elif any(phrase in rule for phrase in [
        "at least", "1 of", "enroll in", "enrolled in"]):
        return "OR"
    
    return None


def check_level(rule):
    res = { "type": "LEVEL", "level": "", "op": "=" }
    if "level" in rule:
        res["level"] = extract_grade_or_level(rule)
        if "or higher" in rule:
            res["op"] = ">="
        return res

    return None


        

def link_to_course_or_program(code, link, grade = None):
    if "/courses/view" in link and grade:
        return { "type": "GRADE", "code":  code, "grade": grade }
    elif "/courses/view" in link:
        return { "type": "COURSE", "code": code }
    elif "/programs/view" in link:
        return { "type": "PROGRAM", "code": code }
    
    raise ValueError("Unidentified link")



def extract_course_or_program(text, grade=None):

    after_colon = text.split(":", 1)[1]
    parts = re.split(r'[,.]', after_colon)
    items = [p.strip() for p in parts if p.strip()]
    courses_or_programs = []

    # If ANY digit appears after the colon, treat as a course rule
    if re.search(r'\d', after_colon) and grade:
        for item in items:
            courses_or_programs.append( {"type": "COURSE", "code": item, "grade": grade} )
    elif re.search(r'\d', after_colon):
        for item in items:
            courses_or_programs.append( {"type": "COURSE", "code": item} )
    else:
        for item in items:
            courses_or_programs.append( {"type": "PROGRAM", "code": item} )
    
    return courses_or_programs
    

def extract_rule(html_text: str) -> str:
    tree = html.fromstring(html_text)

    nodes = tree.xpath('//div[@data-test]/node()[not(self::div)]')

    # Convert nodes to string
    parts = []
    for node in nodes:
        if isinstance(node, html.HtmlElement):
            # get only the text inside span (not the tags)
            parts.append(node.text_content())
        else:
            parts.append(str(node))

    # Join everything and clean up whitespace → make it a sentence
    sentence = " ".join(parts)
    sentence = re.sub(r"\s+", " ", sentence).strip()

    return sentence

def parse_datatest(child, class_name):
    rule = extract_rule(str(child))

    if not rule: #<div data-test="..."><div> Not completely nor concurrently enrolled in: MATH125
        # consider if ":" not in text:
        # if so, e.g. enrolled in honors math programs
        text = child.get_text(strip=True)
        if not text: return None

        if ":" not in text:
            with open("special_rules.txt", "a", encoding="utf-8") as f:
                print(text)
                f.write(class_name + ": " + text + '\n')
        else:
            logic_type = check_logic_type(text.lower())

            if not logic_type: 
                print("line 113: " + text)
                raise ValueError("invalid logic type1")
            
            grade = None
            if "grade" in rule:
                grade = extract_grade_or_level(rule)

            return {"type": logic_type, "items": extract_course_or_program(text, grade)}


    else:
        courses_or_programs = []
        logic_type = check_logic_type(rule.lower())
        level = check_level(rule)

        if level: 
            return level

        # check invalid logic_type
        if not logic_type: 
            with open("special_rules.txt", "a", encoding="utf-8") as f:
                print(rule)
                f.write(class_name + ": " + rule + '\n')
            return None

        grade = None
        if "grade" in rule:
            grade = extract_grade_or_level(rule)

        links = child.find_all("a", href = True)
        for a in links:
            code = a.get_text(strip=True)
            link = a.get("href", "")
            courses_or_programs.append(link_to_course_or_program(code, link, grade))

        return { "type": logic_type, "items": courses_or_programs}




# return [n.Node]
def parse_req(ul, class_name):
    children = ul.find_all(recursive=False)
    res = []

    for child in children:

        if child.name == "li" and child.has_attr("data-test"):
            result = parse_datatest(child, class_name)
            if result: res.append(result)

        else: # child.name == "li" or <div><span></span>

            if child.name == "div": 
                child = child.find("li")
                if not child:
                    raise ValueError("no li in div")
                
            first_child = next((child for child in child.children if child.name is not None), None)
            if child.has_attr("data-test"):
                result = parse_datatest(child, class_name)
                if result: res.append(result)

            elif first_child and first_child.name == "span":
                rule = first_child.get_text(strip=True)
                logic_type = check_logic_type(rule.lower())
                inner_ul = child.find("ul")
    
                if not inner_ul: raise ValueError("No ul inside li")
                res.append( {"type": logic_type, "items": parse_req(inner_ul, class_name)} )
                # rule = inner_li.find("span").get_text(strip=True)
                # logic_type = check_logic_type(rule)
                # inner_ul = inner_li.find("ul")
                # res.append( { "type": logic_type, "items": parse_prereq(inner_ul)} )

            else:
                print( "line 180: " + child.get_text(strip=True))
                raise ValueError("li isn't followed by span")
            
    return res


def find_req(html_text, class_name):
    res = { "Prerequisites": "",
            "Antirequisites": "", 
            "Corequisites": "" } 
    soup = BeautifulSoup(html_text, "html.parser")
    h3_tags = soup.select('h3[class^="course-view__label"]')
    for tag in h3_tags:
        if tag.get_text(strip=True) in ["Prerequisites", "Antirequisites", "Corequisites"]:
            ul = tag.parent.find("ul")
            if ul: 
                parse = parse_req(ul, class_name)
                if parse: res[tag.get_text(strip=True)] = parse[0]
    return res


if __name__ == "__main__":
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)

    df = pd.read_csv("courses_info.csv")
    num_to_link = dict(zip(df["code"], df["link"]))
    # open("special_rules.txt", "w", encoding="utf-8").close()

    x = 1265
    for code, link in list(num_to_link.items())[1265:2000]:
        print(code + " " + str(x) + "\n")
        x += 1
        html_text = cc.extract_course(link, driver)
        data = find_req(html_text, code)
        with open(f"Courses/{code}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)