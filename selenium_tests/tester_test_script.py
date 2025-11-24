from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import Select
import time
import os

driver = webdriver.Chrome()
driver.get("http://127.0.0.1:8000")

#login as developer
email_input = driver.find_element(By.ID, "email")
email_input.send_keys("tester@mail.com")
password_input = driver.find_element(By.ID, "password")
password_input.send_keys("password")

login_button = driver.find_element(By.ID, "signin")
login_button.click()

time.sleep(1)
Alert(driver).accept()

#go to assigned tasks
assigned_tasks = driver.find_element(By.LINK_TEXT, "Assigned Tasks")
assigned_tasks.click()

#click on accept task
try:
    accept_task = driver.find_element(By.CLASS_NAME, "accept-btn")
    accept_task.click()
    
    time.sleep(1)
    Alert(driver).accept()
except:
    print("No tasks to accept")
    
#time.sleep(1)
#Alert(driver).accept()

#test the last script
test_btns = driver.find_elements(By.CLASS_NAME, "test-btn")
test_btns[-1].click()

time.sleep(5)

print("Test passed")
driver.close()