import time
import argparse
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC




def test_payloads_against_params():
     # Test each payload against every parameter
    for payload in payloads:

        for parameter in parameters:
            # Construct the URL with the payload in the parameter
            test_url = f'{url}?{parameter}={payload}'
            driver.get(test_url)

            # Wait for the page to load
            time.sleep(1)

            # Check if the payload was executed by looking for the alert box
            try:
                alert = driver.switch_to.alert
                print(f'XSS vulnerability found with payload: {payload} and parameter: {parameter}')
                alert.accept()
            except:
                print(f'No XSS vulnerability found with payload: {payload} and parameter: {parameter}')

def test_payloads_against_forms():
    for payload in payloads:
    # Navigate to the target website
        driver.get(url)

        # Find all the form fields on the page
        form_fields = driver.find_elements(By.TAG_NAME, 'input')
        form_fields += driver.find_elements(By.TAG_NAME, 'textarea')
        form_fields += driver.find_elements(By.TAG_NAME, 'select')

        # Inject the payload into each form field
        for form_field in form_fields:
            try:
                form_field.send_keys(payload)
            except:
                pass
        
        # Submit the form
        form_buttons = driver.find_elements(By.TAG_NAME, 'button')
        form_buttons += driver.find_elements(By.TAG_NAME, 'input')
        form_buttons = [button for button in form_buttons if button.get_attribute('type') in ['submit', 'button']]
        try:
            print([form_button.id for form_button in form_buttons])
            for form_button in form_buttons:
                button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(form_button))
                driver.execute_script("arguments[0].scrollIntoView();", form_button)
                button.click()
        except:
            pass

        # Wait for the page to load
        time.sleep(1)

        # Check if the payload was executed by looking for the alert box
        try:
            alert = driver.switch_to.alert
            print(f'XSS vulnerability found with payload: {payload}')
            alert.accept()
        except:
            print(f'No XSS vulnerability found with payload: {payload}')

def find_link_parameter_keys(links):
  # Iterate through the links and extract the link parameter keys

    potential_keys = []

    for link in links:

        parts = link.split('?')

        if len(parts) > 1:

            link_parameters = parts[1]
            key_value_pairs = link_parameters.split('&')

            for key_value_pair in key_value_pairs:

                key_value = key_value_pair.split('=')
                if key_value[0] != '':
                    key = key_value[0] 
                #print(key)
                potential_keys.append(key)


    unique_keys = []

    for key in potential_keys:
        if key not in unique_keys:
            unique_keys.append(key)

    return unique_keys

def crawl(url):

    # Find all the links on the page
    a_links = driver.find_elements(By.TAG_NAME, 'a')
    iframe_links = driver.find_elements(By.TAG_NAME, 'iframe')


    # # Print the URLs of the links
    # for link in links:
    #     print(link.get_attribute('href'))

    links = [link.get_attribute('href') for link in a_links]
    links += [link.get_attribute('src') for link in iframe_links]

    unique_links = []

    for link in links:
        if link not in unique_links and link != None and link != '':
            unique_links.append(link)

    return unique_links

# Set up the argument parser
parser = argparse.ArgumentParser(description=('XSS scanner\n',
'Usage: python3 [filename].py [url] [payloads] [options] ...\n',
'Options: (-p|--params  [parameters]) (-f|--forms) (-i|--info)' ))
parser.add_argument('url', help='URL of the target website')
parser.add_argument('payloads', help='File containing XSS payloads')
parser.add_argument('-p', '--params', help='File containing URL parameters. This is an optional flag.')
parser.add_argument('-f', '--forms', action='store_true', help='Test payloads against all forms on the website')
parser.add_argument('-i','--info', action='store_true', help=('Collect all links leading to other endpoints', 
'in the given target\'s source code.\n Also outputs a list of URL parameters.'))

# Parse the command-line arguments
args = parser.parse_args()
url = args.url
payloads_file = args.payloads
parameters_file = args.params
test_forms = args.forms
info = args.info

# Set up a web driver
options = webdriver.ChromeOptions()
args = ['--headless', '--no-sandbox', '--disable-dev-shm-usage',
'--dns-prefetch-disable', '--single-process', '--disable-renderer-backgrounding']

for arg in args:
    options.add_argument(arg)
    
options.add_argument("window-size=1980x1080")


driver = webdriver.Chrome(options=options)



# Check if the payloads file exists
# Then read the payloads from the file
if not os.path.exists(payloads_file):
    print(f'Error: Payloads file not found: {payloads_file}')
    exit(1)

with open(payloads_file, 'r') as f:
    payloads = [line.strip() for line in f]


# Navigate to the target website
driver.get(url)

if info: 

    split_sections = '_______________________________________________'

    print(split_sections)

    links = crawl(url)

    print(f'[*]Found {len(links)} unique links:')

    for link in links:
        print(link)
    
    print(split_sections)

    parameters = find_link_parameter_keys(links)

    print(f'[*]Found {len(parameters)} unique keys:')

    for parameter in parameters:
        print(parameter)


if parameters_file:
    # Check if the parameters file was provided and exists
    if not os.path.exists(parameters_file):
        print(f'Error: Parameters file not found: {parameters_file}')
        exit(1)

    with open(parameters_file, 'r') as f:
        parameters = [line.strip() for line in f]

    print('[*]Testing against parameters')

    test_payloads_against_params()


if test_forms:

    print('[*]Testing against forms')

    test_payloads_against_forms()

