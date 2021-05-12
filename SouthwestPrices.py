# SWA Fare Scraper // Nick Alvarez c 2021
# Detected by their site. Not functional currently. But the code should be correct - if the site were to work.

from datetime import date, timedelta
import subprocess
import logging
import calendar
import time
import signal
import requests
import re

from selenium.webdriver.remote.remote_connection import LOGGER as seleniumLogger
seleniumLogger.setLevel(logging.WARNING)
from selenium import webdriver
#import undetected_chromedriver as webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

class Flight:
  def __init__(self, f, p):
    self.price = p
    self.depart = f.find_element_by_xpath(".//span[@data-test='select-detail--origination-time']").text
    self.arrive = f.find_element_by_xpath(".//span[@data-test='select-detail--destination-time']").text
    self.flight_num = f.find_element_by_xpath(".//div[@class='flyout-trigger flight-numbers--trigger']").find_element_by_xpath(".//span[@class='actionable--text']").text.strip(" ")
    self.duration = f.find_element_by_xpath(".//div[@class='select-detail--flight-duration']").text
    self.stops = ""
    self.stops_in = ""
    self.stops(f)
  
  def stops(self, f):
    try:
      self.stops = f.find_element_by_xpath(".//div[@class='flight-stops-badge select-detail--flight-stops-badge']").text
      self.stops_in = f.find_element_by_xpath(".//div[@class='select-detail--change-planes']").text
    except NoSuchElementException:
      self.stops = f.find_element_by_xpath(".//div[@class='flight-stops-badge flight-stops-badge_nonstop select-detail--flight-stops-badge']").text
      self.stops_in = ""


# Keyboard interrupts
def exitHandler(signum, frame):
  exit(0)

# Chrome options to be "undetectable" - did not work
signal.signal(signal.SIGINT, exitHandler)
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument("window-size=1280,800")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36")
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

# Creating our webdriver
driver = webdriver.Chrome(service_log_path='NULL', options=chrome_options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

# Airport IATA codes
airports = []

def main():
  # User input for origin and dates of travel
  IATA_origin = input("Origin: ").upper()
  to_date = input("Departure date (YYYY-MM-DD): ")
  rtn_date = input("Return date (YYYY-MM-DD): ")

  # Finding last bookable date
  search_date = date.today()
  data = requests.get("https://www.southwest.com/swa-ui/bootstrap/air-flight-schedules/1/data.js").text.strip().split("\n")
  last_bookable = [i for i in data if "currentLastBookableDate" in i]
  last_bookable_date = last_bookable[0].replace(" ","").replace('"currentLastBookableDate":"',"").replace('",',"").split("-")
  end_date = date(int(last_bookable_date[0]), int(last_bookable_date[1]), int(last_bookable_date[2]))

  # Testing
  # IATA_origin = "RNO"
  # to_date = "2021-06-01"
  # rtn_date = "2021-06-09"

  print(f"Flight schedules can be seen up to {end_date}.\n")

  # Retrieves data from SW "data.js" and finds all airport codes
  def getAirportCodes():
    prog = re.compile(r'\bid\b')
    for iata in data:
      m = prog.search(iata)
      try:
        code = (m.string.replace('"id": "',"").replace('",',"").strip(" "))
        if code != IATA_origin:
          airports.append(code)
      except AttributeError:
        pass

  getAirportCodes()

  print(f"Searching for roundtrip flights from {IATA_origin} from {to_date} to {rtn_date}...")

  # Checks every airport
  for airport in airports:
    # Maximizes price, since we want to find the least
    # Iterators for flight items set to zero
    to_price = 2147483647
    rtn_price = 2147483647
    to_flight_i = 0
    rtn_flight_i = 0
    
    URL = f"https://www.southwest.com/air/booking/select.html?int=HOMEQBOMAIR&adultPassengersCount=1&departureDate={to_date}&destinationAirportCode={airport}&fareType=USD&originationAirportCode={IATA_origin}&passengerType=ADULT&returnDate={rtn_date}&tripType=roundtrip&departureTimeOfDay=ALL_DAY&reset=true&returnTimeOfDay=ALL_DAY"

    try:
      driver.get(URL)
      #print(driver.current_url)
      try:
        try:  #Making sure the page has loaded, else it times out and checks next airport
          WebDriverWait(driver,8).until(EC.presence_of_element_located((By.XPATH, "//span[@class='transition-content price-matrix--details-area']")))
        except TimeoutException:
          pass
        
        # Finding sections for departure and return flights
        to_flights = driver.find_element_by_xpath("//section[@id='air-booking-product-0']").find_elements_by_css_selector("div.air-booking-select-detail")
        rtn_flights = driver.find_element_by_xpath("//section[@id='air-booking-product-1']").find_elements_by_css_selector("div.air-booking-select-detail")

        # Trip name, example: Reno, NV to Los Angeles, CA
        trip = driver.find_element_by_xpath("//div[@class='price-matrix--stations']").text
        print(f"---------{trip}---------------------")

        # Flights to destination, finding lowest price and saving index from 'flight' object
        for flight, i in enumerate(to_flights):
          to_flight_price = int(flight.find_element_by_xpath(".//div[@data-test='fare-button--wanna-get-away®']").find_element_by_xpath(".//span[@class='swa-g-screen-reader-only']").text)
          if (to_flight_price < to_price):
            to_flight_i = i
        
        # Flights to origin, finding lowest price and saving index from 'flight' object
        for flight, i in enumerate(rtn_flights):
          rtn_flight_price = int(flight.find_element_by_xpath(".//div[@data-test='fare-button--wanna-get-away®']").find_element_by_xpath(".//span[@class='swa-g-screen-reader-only']").text)
          if (rtn_flight_price < to_price):
            rtn_flight_i = i
        
        # Initializes Flight objects for departure and return, which finds data about individual flight
        to_flight = Flight(to_flight_price, to_flights[to_flight_i])
        rtn_flight = Flight(rtn_flight_price, rtn_flights[rtn_flight_i])

        # Results
        print(f'''{IATA_origin} > {airport}\t${to_flight.price}\t{to_flight.flight_num}\t{to_flight.depart} - {to_flight.arrive}\t{to_flight.stops} stops {to_flight.stops_in}\t{to_flight.duration}
              \n{airport} > {IATA_origin}\t${to_flight.price}\t{to_flight.flight_num}\t{to_flight.depart} - {to_flight.arrive}\t{to_flight.stops} stops {to_flight.stops_in}\t{to_flight.duration}
              \nTotal Price: ${to_price+rtn_price}''')
      except:
        pass
    
    except IOError:
      pass

if __name__ == "__main__":
  main()