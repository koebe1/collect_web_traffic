from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import os
import os.path
import re
import argparse
import time
import yaml

scripts = os.path.dirname(__file__)
dataset = os.path.dirname(scripts)

# specify the argument to call the python skript with --> -f "path to file"
parser = argparse.ArgumentParser()
parser.add_argument(
    '-f', help='specify a file with a list of urls in the format https://www.abc.com')
args = parser.parse_args()

#  open file with websites, extract urls and push them to array "websites"
with open(args.f) as file:
    text = file.read()
    websites = re.findall(r'(https?://[^\s]+)', text)

with open(os.path.join(dataset, 'config.yml')) as f:
    config = yaml.safe_load(f)
    num = config["num"]


def callWebsites():
    driver = webdriver.Remote('http://127.0.0.1:4444',
                              DesiredCapabilities.CHROME)

    for website in websites:
        driver.get(website)
        # specify time between website loads
        time.sleep(num)

    driver.delete_all_cookies()
    driver.close()
    driver.quit()


callWebsites()
