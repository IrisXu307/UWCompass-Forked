from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def extract_course(url):
    print("Done!")
    driver.get(url)
    footer = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "footer"))
    )

    html_before_footer = driver.execute_script(
        """
    var footer = arguments[0];
    var html = '';
    var elem = document.body.firstChild;
    while(elem && elem !== footer){
        html += elem.outerHTML;
        elem = elem.nextSibling;
    }
    return html;
    """,
        footer,
    )
    return html_before_footer


def extract_courses_link(driver):
    browser = driver

    url = (
        "https://uwaterloo.ca/academic-calendar/undergraduate-studies/catalog#/courses"
    )
    browser.get(url)

    wait = WebDriverWait(browser, 5)
    all_courses = []

    last_height = browser.execute_script("return document.body.scrollHeight")

    # scroll all the way down to check the page is loaded
    while True:
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        try:
            wait.until(
                lambda d: d.execute_script("return document.body.scrollHeight")
                > last_height
            )
            new_height = browser.execute_script("return document.body.scrollHeight")
        except:
            break

        if new_height == last_height:
            break
        last_height = new_height

    # find all subject modules
    modules = browser.find_elements(
        By.CSS_SELECTOR, "div.style__collapsibleBox___DBqEP"
    )

    for i in range(len(modules)):
        modules = browser.find_elements(
            By.CSS_SELECTOR, "div.style__collapsibleBox___DBqEP"
        )
        module = modules[i]

        title = module.find_element(By.TAG_NAME, "h2").text.strip()

        # expand modules
        try:
            btn = module.find_element(By.CSS_SELECTOR, "button[aria-label^='show']")
            if btn.get_attribute("aria-expanded") == "false":
                browser.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});", btn
                )
                browser.execute_script("arguments[0].click();", btn)

                wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, './/a[starts-with(@href, "#/courses/")]')
                    )
                )
        except:
            print("No button or already expanded")

        modules = browser.find_elements(
            By.CSS_SELECTOR, "div.style__collapsibleBox___DBqEP"
        )
        module = modules[i]

        course_links = module.find_elements(
            By.XPATH, './/a[starts-with(@href, "#/courses/")]'
        )

        print(f"  Course number: {len(course_links)}")

        for link in course_links:
            href = link.get_attribute("href")

            text = link.text.strip()
            if not text:
                continue

            if " - " in text:
                code, name = text.split(" - ", 1)
            else:
                code, name = text, ""

            all_courses.append(
                {"module": title, "number": code, "name": name, "link": href}
            )
            print(f"  {title} - {code} - {name} - {href}")

    print("\nDone! Total course number:", len(all_courses))
    return all_courses


if __name__ == "__main__":
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)

    # AFM 101 url as an example
    # url = "https://uwaterloo.ca/academic-calendar/undergraduate-studies/catalog#/courses/HJ5IYNmYn?bc=true&bcCurrent=AFM101%20-%20Introduction%20to%20Financial%20Accounting&bcGroup=Accounting%20and%20Financial%20Management%20(AFM)&bcItemType=courses"
    # html = extract_course(url)

    links = extract_courses_link(driver)
    ind = 0
    for link in links[:10]:
        page = extract_course(link["link"])
        with open(f"page{ind}.html", "w", encoding="utf-8") as f:
            f.write(page)
        ind += 1

    driver.quit()
