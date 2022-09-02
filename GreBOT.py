import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os 

from login import get_user_data, login
from town import Town
from fetch import fetch_data

###################################################################################################################
#const var#
PATH= (os.getcwd()+"\Chromedriver.EXE")         # ścieżka do sterownika od Chroma
Driver = webdriver.Chrome(PATH)                 # inicjalizacja sterownika
MyTowns = []                                    # pusta lista miast - tu będą przechowywane struktury danych dla każdego miasta
DEBUG = True                                    # pomocnicza zmienna do wyświetlania błędów :D
#end const var#
###################################################################################################################

#main program here#

if __name__ == "__main__":
    Driver.get("https://pl.grepolis.com/") # właczenie przeglądarki

    Username, Password, World = get_user_data()
    if login(Username, Password, World, Driver): # jeśli logowanie zwróci 1 (Bład) zamknij przeglądarke
        Driver.quit()
        print("Coś poszło nie tak... zamykam")
        raise SystemExit(1)

    #Najważniejsze elementy huda - przyda się potem bo ten element jest statyczny :D
    StrategicMapButton= Driver.find_element(By.CLASS_NAME, "strategic_map")   #Zapisanie przycisku do MapyStrategicznej
    IslandMapButton= Driver.find_element(By.CLASS_NAME, "island_view")        #Zapisanie przycisku do Podglądu wyspy
    TownButton= Driver.find_element(By.CLASS_NAME, "city_overview")           #Zapisanie przycisku do Podglądu Miast
    ResBar = Driver.find_element(By.CLASS_NAME, "ui_resources_bar")           #Zapisanie pozycji Paska surowców (do użycia w funkcji do odsiweżania ilości surowców)

    MyTowns = fetch_data(Driver,DEBUG)                   #Pobieranie Informacji z gry :D
    if MyTowns == 1:                        #Jeśli zrówci 1 (Bład) zamknij przeglądarke.
        Driver.quit()
        print("coś poszło nie tak... zamykam")
        raise SystemExit(1)    

    try:
        print("Bot running!")
    
    except KeyboardInterrupt:
        print("Ending program")
        pass
              
    print("Done for now :P")
  ###################################################################################################################









