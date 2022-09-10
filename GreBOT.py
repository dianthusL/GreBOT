import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os 

from utils import my_click,check_town
from login import get_user_data, login
from town import Town
from fetch import fetch_data

###################################################################################################################
#const var#
PATH= (os.getcwd()+"\Chromedriver.EXE")         # ścieżka do sterownika od Chroma
driver = webdriver.Chrome(PATH)                 # inicjalizacja sterownika
MyTowns = []                                    # pusta lista miast - tu będą przechowywane struktury danych dla każdego miasta
DEBUG = True                                    # pomocnicza zmienna do wyświetlania błędów :D
#end const var#
###################################################################################################################

#main program here#

if __name__ == "__main__":

    driver.get("https://pl.grepolis.com/") # właczenie przeglądarki
    Username, Password, World = get_user_data()
    if login(Username,Password,World, driver): # jeśli logowanie zwróci 1 (Bład) zamknij przeglądarke
        driver.quit()
        print("Coś poszło nie tak... zamykam")
        raise SystemExit(1)
#    my_click(driver,"CLASS_NAME","strategic_map")
#    time.sleep(1)
#    my_click(driver,"CLASS_NAME","island_view")
#    time.sleep(1)
#    my_click(driver,"CLASS_NAME","city_overview")
#    time.sleep(1)
    MyTowns = fetch_data(driver,DEBUG)                   #Pobieranie Informacji z gry :D
    if MyTowns == 1:                        #Jeśli zrówci 1 (Bład) zamknij przeglądarke.
        driver.quit()
        print("coś poszło nie tak... zamykam")
        raise SystemExit(1)

    #Najważniejsze elementy huda - przyda się potem bo ten element jest statyczny :D

    wait = WebDriverWait(driver, 10)
    try:
        print("Bot running!")
        while True:
            #buttons[0] - Podglad wyspy
            #buttons[1] - Podglad miasta
            #buttons[2] - Wyśrodkuj miasta
            #buttons[3] - Następne miasto
            #buttons[4] - Poprzednie miasto 
          print("Rozpoczynam farmienie")
          for each_town in MyTowns:
            check_town(driver,each_town.name)
            my_click(driver,"CLASS_NAME","island_view")
            my_click(driver,"CLASS_NAME","btn_jump_to_town.circle_button.jump_to_town")
            for each_village in each_town.village_list:
                each_village.farm(driver)
            my_click(driver,"CLASS_NAME","city_overview")
          time.sleep(60*10)     
    except KeyboardInterrupt:
        print("Ending program")
        pass
              
    print("Done for now :P")
  ###################################################################################################################



