import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json


def get_user_data():
    with open("user.json") as user_file:
        user_data = json.load(user_file)
    return (user_data.values())


def login(username, password, world, driver, DEBUG=False):
    # logowanie do konta
    print("Logging in ...")
    try:
        search_login = driver.find_element(By.ID,"login_userid")    # szukamy pola do loginu
        search_login.send_keys(username)                            # wpisujemy login
        search_pass = driver.find_element(By.ID,"login_password")   # szukamy pola do hasła
        search_pass.send_keys(password)                             # wpisujemy hasło
        search_pass.send_keys(Keys.RETURN)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "worlds"))       # czekamy 10 sec albo do pojawienia się listy swiatów
        )
    except:
        print("Login failed ...")
        return 1
    finally:
        if DEBUG:
            print('search login:', search_login)
            print('search pass:', search_pass)
        print ("Logging OK!")
      
    # wybieranie świata
    print("Chosing world ...") 
    try:
        worlds = driver.find_element(By.ID, "worlds")               # wczytujemy całą liste światów
        worlds_select = worlds.find_elements(By.TAG_NAME, "LI")     # wczytujemy wszystkie elementy 
        if DEBUG:
            print("Worlds: ",worlds)
        for each in worlds_select:                                  # przeszukujemy liste czy dany świat jest naszym światem
            if each.text == world:
                print("Chosing world OK!")
                print("Waiting for game to load ...")
                each.click()                                        # jeśli aktualny świat to nasz kliknij       
                break
    except:
        print("Chosing world failed ...")
        return 1
    finally:
        print("Game loaded OK!")
    return 0
