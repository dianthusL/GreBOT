#Funkcja Login#
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def login(Driver,User,Pass,World):
  DEBUG = False
  #Logowanie Do konta#
  print("Logging in ...")
  try:
    SearchLogin = Driver.find_element(By.ID,"login_userid")               	#szukamy pola do loginu
    SearchLogin.send_keys(User)                                       		#wpisujemy login
    SearchPass = Driver.find_element(By.ID,"login_password")              	#szukamy pola do hasła
    SearchPass.send_keys(Pass)                                       		#wpisujemy hasło
    SearchPass.send_keys(Keys.RETURN)                                     	#Enter :D
    WebDriverWait(Driver, 10).until(
      EC.presence_of_element_located((By.ID, "worlds"))                 	#czekamy 10 sec, albo do pojawienia się listy swiatów
    )
  except:
    print("Loggin Failed...")
    return(1)
  finally:
    if DEBUG:
      print('search login:', SearchLogin)
      print('search Pass:', SearchPass)
  print ("Logging OK!")
  #Koniec Logowania#
  
  #Wybór Swiata# 
  print("Chosing world ...") 
  try:
    Worlds = Driver.find_element(By.ID, "worlds")                       	#Wczytujemy całą liste światów)
    WorldsSelect = Worlds.find_elements(By.TAG_NAME, "LI")              	#Wczytujemy wszystkie Elementy 
    if DEBUG:
      print("Worlds:",Worlds)
    for each in WorldsSelect:                                         		#Przeszukujemy liste czy Dany świat jest naszym Światem
      if(each.text == World):
        print("Chosing world OK!")
        print("Waiting for game to load...")
        each.click()                                                 		#Jeśli aktualny świat to nasz świat kliknij       
        break;
  except:
    print("Chosing World Failed...")
    return(1)
  finally:
    print("Game Loaded OK!")
  return(0)
  #Koniec Wyboru Swiata#   
#Koniec Funkcji Login#
