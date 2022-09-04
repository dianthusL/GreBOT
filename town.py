import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time


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
		farm_button = WebDriverWait(driver, 10).until(
          	EC.element_to_be_clickable((By.ID, self.id))
        )
		ac = ActionChains(driver)
		ac.move_to_element(farm_button).move_by_offset(0, 0).click().perform()
		time.sleep(1)

		collect_buttons = driver.find_elements(By.CLASS_NAME, "card_click_area")
		ac.move_to_element(collect_buttons[0]).move_by_offset(0, 0).click().perform()
		driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
		print("sfarmilem wioske:", self.id)
		time.sleep(1)
