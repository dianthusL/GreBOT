import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
from utils import my_click


class Town():
	def __init__(self):
		self.name = ""
		self.wood = ""
		self.stone = ""
		self.iron = ""
		self.population = ""
		self.max_storage = ""
		self.village_list = []
		
	def state(self):
		print("Nazwa wioski:", self.name
			,"; Drewno: ", self.wood
			,"; Kamien: ", self.stone
			,"; Srebro: ", self.iron
			,"; Populacja: ", self.population
			,"; Magazyn: ", self.max_storage
			)

class Village():
	def __init__(self):
		self.id =""

	def farm(self, driver):
		i = 0
		while i < 3:
			try:
				my_click(driver,"ID",self.id)
				card_area = driver.find_elements(By.CLASS_NAME, "card_click_area")
				ac = ActionChains(driver)
				ac.move_to_element(card_area[0]).move_by_offset(0, 0).click().perform()
				driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
				print("sfarmilem wioske:", self.id)
				break
			except:
				i = i + 1
				print("wyjebałęm się klikając podczas farmienia:",self.id )
				time.sleep(1)


