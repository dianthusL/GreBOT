import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def get_buttons(driver,DEBUG):
	#buttons[0] - Podglad wyspy
	#buttons[1] - Podglad miasta
	#buttons[2] - Wyśrodkuj miasta
	#buttons[3] - Następne miasto
	#buttons[4] - Poprzednie miasto	
	buttons =[]
	buttons.append(driver.find_element(By.CLASS_NAME, "island_view"))											#Zapisanie przycisku do Podglądu Wyspy
	buttons.append(driver.find_element(By.CLASS_NAME, "city_overview"))											#Zapisanie przycisku do Podglądu do Miasta
	buttons.append(driver.find_element(By.CLASS_NAME, "btn_jump_to_town.circle_button.jump_to_town"))
	buttons.append(driver.find_element(By.CLASS_NAME, "btn_next_town.button_arrow.right"))                		#Zapisanie przycisku do Następnego Miasta
	buttons.append(driver.find_element(By.CLASS_NAME, "btn_prev_town.button_arrow.left"))               		#Zapisanie przycisku do Poprzedniego Miasta                         
	return(buttons)

def my_click(driver,by,dest):
	i = 0
	while i < 3:
		try:
			wait = WebDriverWait(driver, 10)
			if by == "CLASS_NAME":
				wait.until(EC.visibility_of_element_located((By.CLASS_NAME, dest)))
				wait.until(EC.element_to_be_clickable((By.CLASS_NAME, dest))).click()
			if by == "ID":
				wait.until(EC.visibility_of_element_located((By.ID, dest)))
				wait.until(EC.element_to_be_clickable((By.ID, dest))).click()
			if by == "XPATH":
				wait.until(EC.visibility_of_element_located((By.XPATH, dest)))
				wait.until(EC.element_to_be_clickable((By.XPATH, dest))).click()
			break				
		except:
			i = i + 1
			print("wyjebałęm się klikając w :",dest) 
			time.sleep(1) 
                  

def check_town(driver, town_name):
	#Funkcja sprawdza czy jesteśmy w odpowiednim mieście
	print("Sprawdzam czy jestem w miescie:",town_name)
	i = 0
	while i < 3 :
		try:
			WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "caption.js-viewport")))		#czekamy 10 sec, albo do pojawienia się elmentu trzymającego aktualną nazwę wioski
			while town_name != (driver.find_element(By.CLASS_NAME, "caption.js-viewport").text):
				print("miasto nie ok, zmieniam miasto")																	#wypisz komentarz  
				my_click(driver,"CLASS_NAME","btn_next_town.button_arrow.right")										#kliknij w przycisk następne miasto
			print("miasto ok")
			break
		except:
			i = i + 1
			print("wyjebałęm się klikając podczas zmiany miasta" )
			time.sleep(1)
