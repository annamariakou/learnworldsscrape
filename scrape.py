import time
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Load environment variables from .env file
load_dotenv()

def login_and_scrape(url, output_file):
    # Retrieve environment variables
    login_url = os.getenv('LOGIN_URL')
    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')
    chromedriver_path = os.getenv('CHROMEDRIVER_PATH')

    # Set up Selenium with ChromeOptions and Service
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run headless if needed
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Adjust path to your ChromeDriver executable
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(login_url)

    # Wait until the "Sign In" button is clickable and then click it
    sign_in_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.ID, 'menuItem5'))  # Replace with the actual ID
    )
    sign_in_button.click()

    # Wait until the login form is visible
    WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.CLASS_NAME, 'js-signin-input'))
    )

    # Log in
    username_field = driver.find_element(By.CLASS_NAME, '-email-input')
    password_field = driver.find_element(By.CLASS_NAME, '-pass-input')
    login_button = driver.find_element(By.CLASS_NAME, '-login-but')

    username_field.send_keys(username)
    password_field.send_keys(password)
    login_button.click()

    # Wait for the page to load after login
    time.sleep(5)  # Adjust the sleep time as needed


    # Navigate to the target page after logging in
    driver.get(url)
    time.sleep(20)  # Wait for the page to load

    iframe = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, 'iframe'))
    )
    driver.switch_to.frame(iframe)

    iframe_source = driver.page_source

    # Get the page source
    page_source = driver.page_source

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(iframe_source, 'html.parser')

     # Extract target content (example: extracting all paragraphs)
    # content = '\n'.join(p.text for p in soup.find_all('p'))

    content = soup.prettify()
    # Extract all elements individually with tag names and attributes
    elements = []
    for element in soup.find_all(True):  # True finds all tags
        tag_name = element.name
        attributes = element.attrs
        inner_text = element.get_text(strip=True)
        elements.append({
            "tag": tag_name,
            "attributes": attributes,
            "text": inner_text
        })

# Convert each element to a string format and join them
    content = '\n'.join([f"<{el['tag']} {el['attributes']}>{el['text']}</{el['tag']}>" for el in elements])

    # Extract the CSRF token from the meta tag within the head
    csrf_meta = soup.find('meta', {'name': 'csrf-token'})
    if csrf_meta:
        csrf_token = csrf_meta['content']
    else:
        raise ValueError("CSRF token not found")

    
   # Convert to Markdown (simple example)
    markdown_content = f"## Extracted Content\n\n{content}"

    # Save to an MDX file with front matter
    with open(output_file, 'w', encoding='utf-8') as mdx_file:
        mdx_file.write('---\n')
        mdx_file.write('title: "Extracted Content"\n')
        mdx_file.write('---\n\n')
        mdx_file.write(markdown_content)

    # Optional: Save prettified HTML to a file for debugging
    with open('pretty_output.html', 'w', encoding='utf-8') as html_file:
        html_file.write(soup.prettify())

    #close Selenium
    driver.quit()

    print("Content extracted and saved to output.mdx")

# Usage
login_and_scrape(
    'https://learn.schoolofcode.co.uk/path-player?courseid=lrn-achievements&unit=667536b302a6de374f0187f9Unit', 
    'output.mdx'  
)