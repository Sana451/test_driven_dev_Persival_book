import time

from selenium import webdriver

# browser = webdriver.Firefox()
browser = webdriver.Chrome()
browser.get('http://localhost:8000')
# browser.get("https://pypi.org/project/selenium/")

assert "The install worked successfully! Congratulations!" in browser.title

