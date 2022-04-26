from selenium import webdriver
import time

browser_driver = webdriver.Chrome('chromedriver')  # Optional argument, if not specified will search path.

browser_driver.get('https://outlook.office365.us/calendar/view/day');
#page_source = str(browser_driver.page_source.encode('utf-8'))

# wait until the first log in
current_url = browser_driver.current_url
while current_url == 'https://outlook.office365.us/calendar/view/day': 
   time.sleep(1)
   current_url = browser_driver.current_url
while current_url != 'https://outlook.office365.us/calendar/view/day':
   current_url = browser_driver.current_url
   print('============ URL:' , current_url)
   time.sleep(1)
 
search_cal = browser_driver.find_element_by_class_name('root-138')
print("============================", search_cal.get_attribute('title'))
#browser_driver.refresh()