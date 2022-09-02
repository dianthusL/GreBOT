import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os 

from login import login
from town import Town
from fetch import fetchdata

###################################################################################################################
#const var#
PATH= (os.getcwd()+"\Chromedriver.EXE")                                             #Scieżka do sterownika od Chroma
Driver = webdriver.Chrome(PATH)                                         #Inicjalizacja sterownika
Username = "DUPA"                                                   #Login
Password = "DUPA"                                                   #Hasło
World = "METHONI"                                                       #Swiat na który chcesz się zalogować
MyTowns = []                                                              #Pusta lista miast --- tu będą przechowywane Struktury danych dla każdego miasta
DEBUG = True                                                            #pomocnicza zmienna do wyświetlania błędów :D
#end const var#
###################################################################################################################



###################################################################################################################
#Klasy i Funkcje poniżej#

#Klasa DataStruct#
class DataStruct(object):                      #Klasa do trzymania StrukturDanych :)
    def __init__(self, **kwds):
      self.__dict__.update(kwds)
#Koniec Klasy DataStruct#

#Funkcja ResUpdate#     
def ResUpdate(index):
  WoodAmm = ResBar.find_element(By.CLASS_NAME, "indicator.wood").get_attribute("innerText")
  print(WoodAmm)
#Koniec funkcji ResUpdate#


#Koniec Funkcji Login#

#Funkcja FetchData#

#Koniec Funkcji FetchData
  
#Koniec Klass i Funkcji#
###################################################################################################################



###################################################################################################################

#main program here#

Driver.get("https://pl.grepolis.com/")  #Właczenie Przeglądarki

if login(Driver,Username,Password,World):      #Jeśli logowanie zwróci 1 (Bład) zamknij przeglądarke
  Driver.quit()
  print("coś poszło nie tak... zamykam")
  raise SystemExit(1)

#Najważniejsze elementy huda - przyda się potem bo ten element jest statyczny :D
StrategicMapButton= Driver.find_element(By.CLASS_NAME, "strategic_map")   #Zapisanie przycisku do MapyStrategicznej
IslandMapButton= Driver.find_element(By.CLASS_NAME, "island_view")        #Zapisanie przycisku do Podglądu wyspy
TownButton= Driver.find_element(By.CLASS_NAME, "city_overview")           #Zapisanie przycisku do Podglądu Miast
ResBar = Driver.find_element(By.CLASS_NAME, "ui_resources_bar")           #Zapisanie pozycji Paska surowców (do użycia w funkcji do odsiweżania ilości surowców)

MyTowns = fetchdata(Driver,DEBUG)                   #Pobieranie Informacji z gry :D
if MyTowns == 1:                        #Jeśli zrówci 1 (Bład) zamknij przeglądarke.
  Driver.quit()
  print("coś poszło nie tak... zamykam")
  raise SystemExit(1)    


try:
  print("Bot Running!")
  
   
except KeyboardInterrupt:
  print("Ending Program")
  pass

            
print("done for now :P")
###################################################################################################################









