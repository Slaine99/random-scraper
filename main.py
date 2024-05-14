from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import re
import usaddress
import os
import json
import pymongo


def save_to_mongodb(data):
    # Connect to MongoDB
    try:
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        # Access or create the database
        db = client["probolsky"]
        # Access or create the collection
        collection = db["centralized_data_houz"]
        # Insert the data into the collection
        collection.insert_one(data)
        print("Data saved to MongoDB successfully.")

    except Exception as e:
        print(f"Error saving to MongoDB: {str(e)}")
def get_all_popular_states(driver):
    driver.get("https://www.houzz.com/professionals/interior-designer")
    time.sleep(2)
    
    click_state = driver.find_element(By.XPATH, '//input[contains(concat(" ",normalize-space(@class)," ")," pro-location-autosuggest__input ")]').click()
    time.sleep(1)
    states = driver.find_elements(By.XPATH, '//li[@role="option"][@data-section-index="2"]//a[contains(concat(" ",normalize-space(@class)," ")," sc-1qppj2g-0 ")]')
    all_state_href = []
    for state in states:
        print(state.text)
        state_href = state.get_attribute('href')
        all_state_href.append({"href": state_href, "state": state.text.strip()})

    #Save all to text file
    with open('houz_states.txt', 'w') as f:
        for state in all_state_href:
            f.write("%s\n" % state)
    return all_state_href


def parse_data(business_data, url):
    info_dict = {}
    lines = business_data.split('\n')
    categories = ["Business Name", "Phone Number", "Website", "Address", "Typical Job Cost", "Followers"]
    current_category = None
    multiline_fields = ["Address", "Typical Job Cost", "Followers"]

    for line in lines:
        if line.strip().replace("\n", "") in categories:
            # Start a new single-line field
            current_category = line.strip()
        elif current_category:
            if current_category.replace("\n", "") in multiline_fields:
                # Append to the current multiline field
                if current_category.replace("\n", "") not in info_dict:
                    info_dict[current_category.replace("\n", "")] = []
                info_dict[current_category.replace("\n", "")].append(line.strip())
            else:
                # Save single-line fields directly
                info_dict[current_category.replace("\n", "")] = line.strip()

    # Join the lines in multiline fields
    for field in multiline_fields:
        if field in info_dict:
            info_dict[field.strip()] = ' '.join(info_dict[field])

    return info_dict, url


def login_houz(driver, url):
    driver.get(url)
    time.sleep(5)
    username_str = "shumnmitsuebaby143@gmail.com"
    password_str = "Firiyuu77!"
    user_name = driver.find_element(By.XPATH, '//input[contains(concat(" ",normalize-space(@class)," ")," authFlowInput ")][contains(concat(" ",normalize-space(@class)," ")," form-control ")]')
    user_name.send_keys(username_str)
    password = driver.find_element(By.XPATH, '//input[@id="password"][contains(concat(" ",normalize-space(@class)," ")," authFlowInput ")]')
    password.send_keys(password_str)

    login_button = driver.find_element(By.XPATH, '//input[@id="signIn"][contains(concat(" ",normalize-space(@class)," ")," btn ")]')
    login_button.click()
    time.sleep(5)


def search_houz(driver):
    time.sleep(3)
    try:
        driver.find_element(By.XPATH, '//div[@id="hui-select-menu-2"]').click()
        time.sleep(1)
        driver.find_element(By.XPATH, '//button[@tabindex="-1"][@id="hui-menu-1-item-3"]').click()
        time.sleep(1)
    except Exception as e:
        pass


    visited_urls = set()  # Using a set to keep track of visited URLs

    while True:
        #Log collected urls
        print("Visited URLs: ", len(visited_urls))

        # Find all the hrefs on the current page
        hrefs = driver.find_elements(By.XPATH, '//li[contains(concat(" ",normalize-space(@class)," ")," hz-pro-search-results__item ")]')
        for href in hrefs:
            try:
                url = href.find_element(By.TAG_NAME, "a").get_attribute('href')
                if url not in visited_urls:
                    visited_urls.add(url)
                    # Here you can perform whatever actions you need on the visited page
            except Exception as e:
                print("Error occurred while processing URL:", href)
                pass


        next_button = None
        # Look for the "Next" button and extract its href
        try:
            next_button = driver.find_element(By.XPATH,
                                          '//div[@data-container="Pro Results"]//a[contains(concat(" ",normalize-space(@class)," ")," hz-pagination-link ")][contains(concat(" ",normalize-space(@class)," ")," hz-pagination-link--next ")]')
        except:
            break

        if not next_button:
            break

        if next_button:
            next_href = next_button.get_attribute('href')
            if next_href:
                # Visit the URL extracted from the "Next" button
                driver.get(next_href)
                time.sleep(2)  # Adjust sleep time as needed

            else:
                # If "Next" href is not found, exit the loop
                break
        else:
            # If "Next" button is not found, exit the loop
            break
    return list(visited_urls)


driver = webdriver.Chrome()  # or webdriver.Firefox(), webdriver.Edge(), etc.
driver.maximize_window()
url = "https://www.houzz.com/houzz-login"
login_houz(driver, url)

# all_states_urls = get_all_popular_states(driver)
# Get professional URLs===============================================
all_counties = json.loads(open('counties.json', 'r').read())
#Start at specific county
all_counties = all_counties[::-1]
all_counties = all_counties[all_counties.index({"county": "Nantucket County, Massachusetts", "postcode": "02554"}):]

for county in all_counties:
    driver.get("https://www.houzz.com/professionals/interior-designer")
    time.sleep(2)
    #wait for element to load
    WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH, '//input[contains(concat(" ",normalize-space(@class)," ")," pro-location-autosuggest__input ")]')))
    WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.XPATH, '//input[contains(concat(" ",normalize-space(@class)," ")," pro-location-autosuggest__input ")]')))
    driver.find_element(By.XPATH, '//input[contains(concat(" ",normalize-space(@class)," ")," pro-location-autosuggest__input ")]').click()
    driver.find_element(By.XPATH, '//input[contains(concat(" ",normalize-space(@class)," ")," pro-location-autosuggest__input ")]').send_keys(county["postcode"])
    #press enter
    driver.find_element(By.XPATH, '//input[contains(concat(" ",normalize-space(@class)," ")," pro-location-autosuggest__input ")]').send_keys(u'\ue007')
    time.sleep(2)


    urls_filename = f'houz_urls-county-{county["county"]}.txt'
    data_directory = f'houz-data-county/houz_data-{county["county"]}.csv'

    if os.path.exists(urls_filename) and os.path.exists(data_directory):
        print(f"Data for {county['county']} already exists. Skipping processing.")
        continue

    if os.path.exists(urls_filename):
        with open(urls_filename, 'r') as f:
            urls = f.readlines()
        urls = [url.strip() for url in urls]
        print("Urls already collected for", county['county'])
    else:
        urls = search_houz(driver)
        # Save the URLs to a text file
        with open(urls_filename, 'w') as f:
            for url in urls:
                f.write("%s\n" % url)

    list_of_data = []
    #Start from certain url
    # starting_url = "https://www.houzz.com/pro/naomi-lestrad/nl-home-designs"
    # urls = urls[urls.index(starting_url):]

    for url in urls:
        try:
            driver.get(url)
            # Wait for the business section to load
            WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, '//section[@id="business"]')))
            business_data = driver.find_element(By.XPATH, '//section[@id="business"]')
            parsed_data, url = parse_data(business_data.text, url)
            parsed_data['URL'] = url
            parsed_data["State"] = county['county']


            address_components = dict(usaddress.tag(parsed_data["Address"])[0])

            # Extract address components
            parsed_data["City"] = address_components.get("PlaceName", "")
            parsed_data["State"] = address_components.get("StateName", "")
            parsed_data["Country"] = address_components.get("CountryName", "")
            parsed_data["Zip Code"] = address_components.get("ZipCode", "")
            #Get current driver url
            parsed_data["URL"] = driver.current_url
            #save_to_mongodb(parsed_data)
            print("Saved")
            print(parsed_data)
            list_of_data.append(parsed_data)



        except Exception as e:
            print("Error occurred while processing URL:", url)
            continue

    # Save to csv
    df = pd.DataFrame(list_of_data)
    df.to_csv(data_directory, index=False)
