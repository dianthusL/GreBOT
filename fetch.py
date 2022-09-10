import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils import my_click, check_town
from town import Town, Village
import time

def fetch_data(driver, DEBUG):
    my_towns_local = [] #Tutaj iniclaizujemy pustą listę używaną dalej w funkcji
    # Pobieranie informacji ze strony
    # Plan jest taki żeby na początku pobrać potrzebne informacje (ilośc wiosek, rozmieszczenie przycisków hudu itp...

    #Tutaj Pobieramy informacje o Liscie Miast
    print("Fetching started...")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "towns_overview"))                                 #czekamy 10 sec, albo do pojawienia się Overwiev
    )
    #Otwieramy okienko z Listą miast
    driver.execute_script("document.getElementById('overviews_link_hover_menu').style.display = 'block'") #rozwija pasek zarządzania
    my_click(driver,"CLASS_NAME","towns_overview")                                                        #Kliknięcie w liste wiosek
    driver.execute_script("document.getElementById('overviews_link_hover_menu').style.display = 'none'")  #Zwija pasek zarządzania
    # W Liscie miast wyszukujemy każdy element z listy i zapisujemy do town_list_elements
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "game_list.scroll_content"))                       #czekamy 10 sec, albo do pojawienia się listy Miast
    )  
    list_element = driver.find_element(By.CLASS_NAME, "game_list.scroll_content")                         #znajdujemy element który przechowuję listę, (robimy tak żeby nie szukać potem na całej stronie, tylko w tym 1 elemencie)
    town_list_elements = list_element.find_elements(By.XPATH,("//*[contains(@id, 'ov_town')]"))           #w elemencie wyszukanym powyżej szukamy każdego elementu listy
    if DEBUG:
        print("Znaleziono",len(town_list_elements) ,"miast")
    # Dla każdego znalezionego elementu tworzymy nową klasę typu town i zapisujemy do niej wszystkie informacjie odnośnie aktualnego miesta
    for each in town_list_elements:
        my_towns_local.append(Town())                                                                       #Tu deklarujemy nową klasę Typu town
        my_towns_local[-1].name = each.find_element(By.CLASS_NAME, "gp_town_link").text                     #Pobieramy nazwę wioski ze strony
        my_towns_local[-1].wood = each.find_element(By.CLASS_NAME, "wood").text                             #Pobieramy ilość drewna w wiosce ze strony
        my_towns_local[-1].stone = each.find_element(By.CLASS_NAME, "stone").text                           #Pobieramy ilość kamienia w wiosce ze strony
        my_towns_local[-1].iron = each.find_element(By.CLASS_NAME, "iron").text                             #Pobieramy ilość srebra w wiosce ze strony
        my_towns_local[-1].population = each.find_element(By.CLASS_NAME, "town_population_count").text      #Pobieramy ilość dostępnej populacji w wiosce ze strony
        my_towns_local[-1].max_storage = each.find_element(By.CLASS_NAME, "storage").text                   #Pobieramy wielkość magazynu w wiosce ze strony
    #Jeśli wszystko było OK, wypisz wszystie pobrane informacje i zmaknij kienko z miastami.
    print("Fetched Towns:")                                                                               #Wypisz komentarz
    for each in my_towns_local:                                                                           #Dla każdego elementu znalezionego wyżej
        each.state()                                                                                        #Wywoławj funkcję state() -- wypisuje wszystkie wartości z klasy Town
    my_click(driver,"CLASS_NAME","close_all")                                                             #Zamknij wszystkie otwarte okienka
                                                                      
    #Tutaj Szukamy ID Farm dla wioski
    for each_town in my_towns_local: 
        #tutaj potwierdzamy że jesteśmy aktualnie w mieście do którego chcemy przypisać wioski 
        check_town(driver, each_town.name)

        #Już wiemy że jesteśmy w dobrym mieście
        #Przechodzimy do ekranu wyspy
        print("przechodzę do widoku wyspy")
        my_click(driver,"CLASS_NAME","island_view")
        #Centrujemy widok na miasto
        print("Centruje na wyspę")
        my_click(driver,"CLASS_NAME","btn_jump_to_town.circle_button.jump_to_town")
        # tu jest problem bez delaya zassa poprzednia wioske bo mapa sie nie odswierzy :C

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "tile.islandtile")) #czekamy 10 sec, albo do pojawienia elementu wysp
        )
        time.sleep(1)
        #Szukamy wszystjuch wiosek
        village_search=driver.find_elements(By.CLASS_NAME,"owned.farm_town" )
        for each_village in village_search:
            each_town.village_list.append(Village())
            each_town.village_list[-1].id = each_village.get_attribute("ID")
            if DEBUG:
                print("Dodaję wioskę: ", each_town.village_list[-1].id," do miasta : ",each_town.name)

    my_click(driver,"CLASS_NAME","city_overview")
    
    return my_towns_local 
