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
email_input.send_keys("admin@gmail.com")
password_input = driver.find_element(By.ID, "password")
password_input.send_keys("admin")

login_button = driver.find_element(By.ID, "signin")
login_button.click()

time.sleep(1)
Alert(driver).accept()

#click on assign task
assign_task = driver.find_element(By.LINK_TEXT, "Assign Tasks")
assign_task.click()

#select developer
select_tester_dropdown = Select(driver.find_element(By.ID,"tester-select"))
select_tester_dropdown.select_by_visible_text("tester")

assign_button = driver.find_element(By.CLASS_NAME, "assign-btn")
assign_button.click()

time.sleep(1)
Alert(driver).accept()

time.sleep(5)

print("Test passed")
driver.close()