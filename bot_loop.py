from encodings import utf_8
import functions
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
from contextlib import suppress
from selenium.common.exceptions import NoSuchElementException 
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from chromedriver_py import binary_path
from prometheus_client import Gauge, start_http_server


from time import sleep

def timedelta_parse(value) -> timedelta:
    """
    convert input string to timedelta
    """
    value = re.sub(r"[^0-9:.]", "", value)
    if not value:
        raise ValueError(f'{value} not parseable')

    return timedelta(**{key:float(val)
                        for val, key in zip(value.split(":")[::-1], 
                                            ("seconds", "minutes", "hours", "days"))
               })

class GameController():
    _wd: webdriver.Chrome
    def __init__(self) -> None:
        pass

    def _set_webdriver(self, wd):
        if not hasattr(GameController, '_wd'):
            GameController._wd = wd

    def get_elements_by(self, css, by=By.CSS_SELECTOR, wait_s=10.0):
        select_method = (by, css)
        max_retries = 5
        while True:
            try:
                els = WebDriverWait(self._wd, wait_s).until(EC.visibility_of_any_elements_located(select_method))
            except StaleElementReferenceException:
                if max_retries > 0:
                    max_retries -= 1
                    continue
                else:
                    raise Exception("Too much retries")
            else:
                return els

    def does_exists(self, css):
        try:
            self._wd.find_element(By.CSS_SELECTOR, css)
        except NoSuchElementException:
            return False
        else:
            return True

    def get_element_by(self, css, by=By.CSS_SELECTOR, nth=1, wait_s=10.0):
        return self.get_elements_by(css, by, wait_s)[nth-1]

    def click_button_by(self, css, by=By.CSS_SELECTOR, nth=1, wait_s=10.0):
        for _ in range(3):
            try:
                element = self.get_element_by(css, by, nth, wait_s)
                try:
                    element.click()
                    # print("click selenium", css)
                except ElementClickInterceptedException:
                    self._wd.execute_script("arguments[0].click();", element)
                    # print("click js", css)
            except StaleElementReferenceException:
                print("Repated click due to StaleElementReference")
                continue
            except TimeoutError:
                print("Repated click due to TimeoutError", css)
                continue
            else:
                break

    def get_soup_by(self, css, by=By.CSS_SELECTOR, nth=1, wait_s=10.0):
        el_html = self.get_element_by(css, by, nth, wait_s).get_attribute('innerHTML')
        soup = BeautifulSoup(el_html, 'lxml')
        return soup

    def wait_until_loaded(self):
        WebDriverWait(self._wd, 10).until(EC.all_of(
            EC.invisibility_of_element((By.CSS_SELECTOR, 'div#ajax_loader')),
            EC.invisibility_of_element((By.CSS_SELECTOR, 'div.loading_icon')),
            lambda d: d.execute_script("return document.readyState") == "complete",
            lambda d: d.execute_script("return jQuery.active") == 0
        ))

    def close_all_windows(self):
        btn_close_all= WebDriverWait(self._wd, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.btn_close_all_windows')))
        if 'display: none;' not in btn_close_all.get_attribute('style'):
            self.click_button_by('div.btn_close_all_windows')

class Game(GameController):
    _assets = Gauge('assets', 'Gold and other coins', ['asset_name'])

    def __init__(self, wd: webdriver.Chrome) -> None:
        super().__init__()
        super()._set_webdriver(wd)
        start_http_server(8000)
        self._wd.maximize_window()
        self.login()
        self.refresh_cities_list()
        self.refresh_global_values()

    def refresh_global_values(self):
        soup = self.get_soup_by('html', By.TAG_NAME)
        self.gold = int(soup.find('div', 'gold_amount').text) # type: ignore
        self._assets.labels("gold").set(self.gold)

        self.wisdom_coins = int(soup.find('div', 'wisdom_coins_box').text) # type: ignore
        self._assets.labels("wisdom_coins").set(self.wisdom_coins)

        self.war_coins = int(soup.find('div', 'war_coins_box').text) # type: ignore
        self._assets.labels("war_coins").set(self.war_coins)

        self.grepo_score = int(soup.find('span', 'grepo_score').text) # type: ignore
        self._assets.labels("grepo_score").set(self.grepo_score)

        self.battle_points = int(soup.find('div', 'nui_battlepoints_container').text) # type: ignore
        self._assets.labels("battle_points").set(self.battle_points)

    def open_cities_menu(self):
        if self.does_exists('div#town_groups_list'):
            return
        for _ in range(3):
            self.click_button_by('div.town_groups_dropdown')
            try:
                WebDriverWait(self._wd, 1).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div#town_groups_list')))
            except TimeoutException:
                continue
            else:
                break
    
    def close_cities_menu(self):
        if not self.does_exists('div#town_groups_list'):
            return
        for _ in range(3):
            self.click_button_by('div.town_groups_dropdown')
            try:
                WebDriverWait(self._wd, 1).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div#town_groups_list')))
            except TimeoutException:
                continue
            else:
                break

    def refresh_cities_list(self):
        self.open_cities_menu()
        soup = self.get_soup_by('div#town_groups_list')
        self.close_cities_menu()
        cities = soup.find_all('span', class_='town_name')
        self.cities = [City(self, city.get_text()) for city in cities]
        

    def login(self):
        LOGIN, PASSOWRD = functions.load_config()
        GAME_URL=r"https://pl.grepolis.com/"
        self._wd.get(GAME_URL)

        select_method_login = (By.CSS_SELECTOR, f'#login_userid')
        WebDriverWait(self._wd, 10).until(EC.presence_of_element_located(select_method_login))
        self._wd.find_element(*select_method_login).send_keys(LOGIN)

        select_method_password = (By.CSS_SELECTOR, f'#login_password')
        WebDriverWait(self._wd, 10).until(EC.presence_of_element_located(select_method_password))
        self._wd.find_element(*select_method_password).send_keys(PASSOWRD)
        
        self.click_button_by('#login_Login')

        self.click_button_by('li[data-worldname="METHONI"]')


class City(GameController):
    game: Game
    villages = []
    warehouse_capacity = None
    wood = None
    stone = None
    iron = None
    _god = Gauge('god', 'God and its favor in the city', ['city', 'god'])
    _population = Gauge('population', 'Population available in the city', ['city', 'category'])
    _resource = Gauge('resource', 'Resources available in the city', ['city', 'resource'])
    _market_resource = Gauge('market_resource', 'Current gold market situation', ['city', 'resource', 'type'])
    _building_level = Gauge('building_level', 'Current building levels', ['city', 'building'])
    
    def __init__(self, game, name) -> None:
        self.game = game
        self.name = name
        self.queue = None
        self.next_queue = None
        self.refresh_current_building_levels()
        self.full_refresh_current_resources()
        self.full_refresh_current_population()
        self.refresh_gold_market()
        self.refresh_villages()
        self.refresh_current_building_queue()
        self.refresh_god()

    def _in_the_city(func): # type: ignore
        def wrapper(self, *args):
            if not self.is_current_city():
                self.select_city()
            func(self, *args) # type: ignore
        return wrapper


    def build_for_free(self):
        if (self.next_queue is None or self.next_queue is not None and (self.next_queue - datetime.now() - timedelta(minutes=5)).total_seconds() > 0):
            return

        if not self.is_current_city():
            self.select_city()
        self.switch_to_city_view()
        if self.does_exists('div.type_free.btn_time_reduction'):
            self.click_button_by('div.type_free.btn_time_reduction', wait_s=1)
        print("Build free")

    def is_current_city(self):
        el = self.get_element_by(f'div.town_groups_dropdown')
        return True if el.text == self.name else False

    def select_city(self):
        self.game.open_cities_menu()
        self.click_button_by(f'//span[text()="{self.name}"]', by=By.XPATH)
        self.wait_until_loaded()

    def jump_to_the_city(self):
        self.click_button_by('div.jump_to_town')
        self.wait_until_loaded()

    def switch_to_island_view(self):
        self.click_button_by('div.island_view')
        self.wait_until_loaded()

    def switch_to_city_view(self):
        self.click_button_by('div.city_overview')
        self.wait_until_loaded()

    def refresh_villages(self):
        if not self.is_current_city():
            self.select_city()
        
        self.switch_to_island_view()
        self.jump_to_the_city()
        soup = self.get_soup_by('div#main_area')      
        self.villages = [Village(self, village.get('id')) for village in soup.find_all('a', class_=lambda c: 'owned' in c and 'farm_town' in c)]
    
    @_in_the_city # type: ignore
    def refresh_god(self):
        soup = self.get_soup_by('div.gods_area')
        self.god = soup.find('div', class_='gods_container').get('class')[-1] # type: ignore
        self.favor = int(soup.find('div', class_='favor_amount').text or 0) # type: ignore
        self._god.labels(self.name, self.god).set(self.favor)

    @_in_the_city # type: ignore
    def full_refresh_current_population(self):
        self.close_all_windows()
        self.click_button_by('div.indicator.population')
        self.wait_until_loaded()
        soup = self.get_soup_by('div#farm_list')
        for desc, item in zip(
        ('current_population', 'max_population', 'pop_growth_on_next_level', 'population_army', 'population_buildings', 'pop_army_training', 'pop_blds_construction'),
        soup.find_all('span', class_='list_item_right')):
            value = int(item.text)
            setattr(self, desc, value)
            self._population.labels(self.name, desc).set(value)
        self.close_all_windows()

    def full_refresh_current_resources(self):
        if not self.is_current_city():
            self.select_city()

        self.close_all_windows()
        self.click_button_by('div.indicator.wood')
        self.wait_until_loaded()
        soup = self.get_soup_by('div.classic_window.storage')

        warehouse_capacity_regexp = r'\w+\s*\(\s*\d+\s*/\s*(\d+)\s*\)'
        warehouse_element = soup.find('div', class_='storage_resbar_title')
        assert warehouse_element is not None
        warehouse_capacity_html_text = warehouse_element.get_text()
        regexp_result = re.search(warehouse_capacity_regexp, warehouse_capacity_html_text)
        assert regexp_result is not None
        self.warehouse_capacity = int(regexp_result.group(1))
        self._resource.labels(self.name, 'warehouse_capacity').set(self.warehouse_capacity)

        for resource in soup.find_all('div', class_='storage_resbar_title'):
            resource_type_html = resource.find('span')
            resource_type = resource_type_html.get('class')[0].replace('_value', '')
            resource_value = int(resource_type_html.get_text().strip())
            setattr(self, resource_type, resource_value)
            self._resource.labels(self.name, resource_type).set(resource_value)
        self.close_all_windows()
        

    def click_building(self, name):
        self.click_button_by(f'area[data-building="{name}"]')
        self.wait_until_loaded()
        

    def refresh_current_building_queue(self):
        if not self.is_current_city():
            self.select_city()
        self.switch_to_city_view()

        queue = []
        soup = self.get_soup_by('div.construction_queue_order_container')
        for slot in soup.find_all('div', class_='js-queue-item'):
            building_name = slot.get('class')[-1]
            building_lvl_el = slot.find('div', class_='building_level')
            if building_lvl_el:
                building_lvl = building_lvl_el.get_text().strip()
            else:
                building_lvl = None
            countdown_el = slot.find('span', class_='countdown')
            if countdown_el:
                time_left = countdown_el.get_text().strip()
            else:
                time_left = None
            queue.append({'bld_name': building_name, 'bld_lvl': building_lvl, 'time_left': time_left})

        self.queue = queue
        if queue[0]['time_left'] is None:
            pass
        else:
            next_queue_in = timedelta_parse(queue[0]['time_left'])
            assert next_queue_in is not None
            self.next_queue = datetime.now() + next_queue_in

    def refresh_gold_market(self):
        if not self.is_current_city():
            self.select_city()
        
        self.switch_to_city_view()

        self.click_building('market')
        soup = self.get_soup_by('div.classic_window.market')
        if soup.find('div', class_='middle', text=re.compile('.*Giełda.*')):
            for resource in soup.find_all('div', class_='resource'):
                resource_type = resource.get('data-type')
                current = int(resource.find('span', class_='current').get_text())
                max = int(resource.find('span', class_='max').get_text())
                setattr(self, f'current_market_{resource_type}', current)
                self._market_resource.labels(self.name, resource_type, 'current').set(current)
                setattr(self, f'max_market_{resource_type}', max)
                self._market_resource.labels(self.name, resource_type, 'max').set(max)
        self.close_all_windows()
        

    def refresh_current_building_levels(self):
        if not self.is_current_city():
            self.select_city()
        
        self.switch_to_city_view()
        self.click_building('main')
        soup = self.get_soup_by('div[role="dialog"]')

        for building in soup.find_all('div', class_='building'):
            building_name = building.parent.get('id').replace('building_main_', '')
            building_level = building.find('span', class_='level').get_text()
            setattr(self, building_name, building_level)
            self._building_level.labels(self.name, building_name).set(building_level)
        self.close_all_windows()
    
    def start_construction(self, building):
        if not self.is_current_city():
            self.select_city()
        self.switch_to_city_view()
        self.click_building('main')
        build_button = self.get_element_by(f'div#building_main_{building} *.build_up')
        if 'build_grey' in build_button.get_attribute("class"):
            print("Build not possible")
        else:
            print("Build possible")
            build_button.click()

        
class Village(GameController):
    parent: City
    id: str
    curr_capacity: int
    max_capacity: int
    # next_recollect: datetime 

    def __init__(self, parent, id) -> None:
        self.parent = parent
        self.id = id
        self.claim_locked_until = None
    
    def go_to_village(self):
        self.close_all_windows()
        if not self.parent.is_current_city():
            self.parent.select_city()
        self.parent.jump_to_the_city()
        self.parent.switch_to_island_view()

        self.click_button_by(f'a#{self.id}')
    
    def refresh_capacity(self):
        self.go_to_village()
        soup = self.get_soup_by('div.classic_window.farm_town')
        self.curr_capacity = int(soup.select('div.window_content span.value_container span.curr')[0].get_text())
        self.max_capacity = int(soup.select('div.window_content span.value_container span.max')[0].get_text())
        

    def farm_village(self):
        if max(self.parent.wood, self.parent.stone, self.parent.iron)/self.parent.warehouse_capacity > 0.90: # type: ignore
            return
        if (self.claim_locked_until is not None and (self.claim_locked_until - datetime.now()).total_seconds() > 0):
            return

        self.go_to_village()

        for _ in range(3):
            try:
                button = self.get_element_by('div.btn_claim_resources')
                if 'disabled' not in button.get_attribute('class'):
                    button.click()
            except StaleElementReferenceException:
                continue
            else:
                break

        try:
            next_claim_in_el = self.get_element_by('div.banner span.pb_bpv_unlock_time')
        except TimeoutError as e:
            print('Could not get the next claim time - TimeoutError')
        except Exception as e:
            print(f'Could not get the next claim time {e}')
        else:         
            next_claim_in = timedelta_parse(next_claim_in_el.text)
            self.claim_locked_until = datetime.now() + next_claim_in

        self.close_all_windows()


def get_next_full_N_minutes(n):
    now = datetime.now()
    return now.replace(second=0, microsecond=0) + timedelta(minutes=n-now.minute%n if now.minute%n != 0 else 0)


service_object = Service(binary_path)
with webdriver.Chrome(service=service_object) as wdriver:
    try:
        game = Game(wdriver)
        t_1 = get_next_full_N_minutes(1)
        t_10 = get_next_full_N_minutes(10)

        while True:
            #run every full 10 minutes:
            if (t_10-datetime.now()).total_seconds() < 0:
                # run here
                print("run 10 min", datetime.now())
                # game.refresh_cities_list() # TODO do not override good cities
                game.refresh_global_values()

                for city in game.cities:
                    city.refresh_gold_market()
                    city.full_refresh_current_resources()
                    city.full_refresh_current_population()
                    city.refresh_current_building_levels()
                    city.refresh_god()
                    if city.queue[-1]['bld_name'] == 'empty_slot' and city.name == 'Miasto kroku' and int(city.academy) < 15: # type: ignore
                        city.start_construction('academy')
                    if city.queue[-1]['bld_name'] == 'empty_slot' and city.name == 'Miasto kroku' and int(city.main) < 24 : # type: ignore
                        city.start_construction('main')
                    if city.queue[-1]['bld_name'] == 'empty_slot' and city.name == 'Miasto kroku' and int(city.farm) < 20: # type: ignore
                        city.start_construction('farm')
                    if city.queue[-1]['bld_name'] == 'empty_slot' and city.name == 'Miasto sroku' and int(city.main) < 24 : # type: ignore
                        city.start_construction('main')
                    if city.queue[-1]['bld_name'] == 'empty_slot' and city.name == 'Miasto sroku' and int(city.main) < 24 : # type: ignore
                        city.start_construction('main')
                    if city.queue[-1]['bld_name'] == 'empty_slot' and city.name == 'Miasto sroku' and int(city.academy) < 13 : # type: ignore
                        city.start_construction('academy')
                    # if city.queue[-1]['bld_name'] == 'empty_slot' and city.name == 'Miasto sroku' and int(city.barracks) < 5 : # type: ignore
                    #     city.start_construction('barracks')
                    # if city.queue[-1]['bld_name'] == 'empty_slot' and city.name == 'Miasto sroku' and int(city.main) < 15 : # type: ignore
                    #     city.start_construction('main')
                    # if city.queue[-1]['bld_name'] == 'empty_slot' and city.name == 'Miasto sroku' and int(city.storage) < 15 : # type: ignore
                    #     city.start_construction('storage')
                    if city.queue[-1]['bld_name'] == 'empty_slot' and city.name == 'Miasto mroku' and int(city.ironer) < 24: # type: ignore
                        city.start_construction('ironer')
                    if city.queue[-1]['bld_name'] == 'empty_slot' and city.name == 'Miasto mroku' and int(city.stoner) < 24: # type: ignore
                        city.start_construction('stoner')
                    if city.queue[-1]['bld_name'] == 'empty_slot' and city.name == 'Miasto mroku' and int(city.lumber) < 24: # type: ignore
                        city.start_construction('lumber')
                    if city.queue[-1]['bld_name'] == 'empty_slot' and city.name == 'Miasto mroku' and int(city.farm) < 39: # type: ignore
                        city.start_construction('farm')
                    
                # untill here
                t_10 = get_next_full_N_minutes(10) + timedelta(minutes=10)

            #run every full minute:
            if (t_1-datetime.now()).total_seconds() < 0:
                print("run 1 min", datetime.now())
                # run here
                for city in game.cities:
                    city.refresh_current_building_queue()
                    city.build_for_free()
                    if city.queue[-1]['bld_name'] == 'empty_slot' and city.name == 'Miasto wzroku' and int(city.academy) < 5: # type: ignore
                        city.start_construction('academy')
                    if city.queue[-1]['bld_name'] == 'empty_slot' and city.name == 'Miasto wzroku' and int(city.temple) < 5: # type: ignore
                        city.start_construction('temple')
                    if city.queue[-1]['bld_name'] == 'empty_slot' and city.name == 'Miasto wzroku' and int(city.hide) < 5: # type: ignore
                        city.start_construction('hide')
                # untill here
                t_1 = get_next_full_N_minutes(1) + timedelta(minutes=1)

            #run with main loop
            for city in game.cities:
                for village in city.villages:
                    village.farm_village()

            sleep(5)
    except Exception as e:
        print(e)
        basename = f'{datetime.now().strftime("%Y%m%d%H%M%S")}_{e.__class__.__name__}'
        with open(f'errors/{basename}_error.txt', 'w') as f:
            import traceback
            traceback.print_exc(file=f)
        with open(f'errors/{basename}_html.txt', 'w', encoding="UTF8") as f:
            f.write(wdriver.find_element(By.TAG_NAME, "html").get_attribute('outerHTML'))
        wdriver.save_screenshot(f'errors/{basename}.png')        