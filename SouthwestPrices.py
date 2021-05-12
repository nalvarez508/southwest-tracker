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

def exitHandler(signum, frame):
  exit(0)

signal.signal(signal.SIGINT, exitHandler)
chrome_options = Options()
#chrome_options.add_argument("--headless")
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument("window-size=1280,800")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36")
#chrome_options.add_argument("user-data-dir=selenium")
#chrome_options.add_argument('proxy-server=192.53.122.229:3128')

chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
driver = webdriver.Chrome(service_log_path='NULL', options=chrome_options)

driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

airports = []
weAreDone = False

def main():
  #IATA_origin = input("Origin: ").upper()
  #to_date = input("Departure date (YYYY-MM-DD): ")
  #rtn_date = input("Return date (YYYY-MM-DD): ")
  #IATA_destination = input("Destination: ").upper()
  search_date = date.today()
  data = requests.get("https://www.southwest.com/swa-ui/bootstrap/air-flight-schedules/1/data.js").text.strip().split("\n")
  last_bookable = [i for i in data if "currentLastBookableDate" in i]
  last_bookable_date = last_bookable[0].replace(" ","").replace('"currentLastBookableDate":"',"").replace('",',"").split("-")
  end_date = date(int(last_bookable_date[0]), int(last_bookable_date[1]), int(last_bookable_date[2]))
  one_day_delta = timedelta(days=1)

  # Testing
  IATA_origin = "RNO"
  to_date = "2021-06-01"
  rtn_date = "2021-06-09"

  print(f"Flight schedules can be seen up to {end_date}.\n")

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

  for airport in airports:
    time.sleep(5)
    #URL = f"https://www.southwest.com/air/low-fare-calendar/select-dates.html?adultPassengersCount=1&currencyCode=USD&departureDate={to_date}&destinationAirportCode={airport}&originationAirportCode={IATA_origin}&passengerType=ADULT&returnAirportCode=&returnDate={rtn_date}&tripType=roundtrip"
    URL = "https://www.southwest.com/air/booking/select.html?int=HOMEQBOMAIR&adultPassengersCount=1&departureDate=2021-06-01&destinationAirportCode=ALB&fareType=USD&originationAirportCode=RNO&passengerType=ADULT&returnDate=2021-06-09&tripType=roundtrip&departureTimeOfDay=ALL_DAY&reset=true&returnTimeOfDay=ALL_DAY"

    try:
      print(URL)
      driver.get(URL)
      print(driver.current_url)
      #time.sleep(10)
      #print(driver.page_source)
      try:
        try:
          WebDriverWait(driver,5).until(EC.presence_of_element_located((By.XPATH, "//div[@id='airLowFareCalendar_0']")))
        except TimeoutException:
          print("Timed out!")
        
        #flights = driver.find_element_by_xpath("//div[@class='air-low-fare-calendar-matrix-secondary']")
        to_flights = driver.find_element_by_xpath("//div[@id='airLowFareCalendar_0']").find_elements_by_css_selector("div.air-low-fare-calendar-matrix-secondary")
        rtn_flights = driver.find_element_by_xpath("//div[@id='airLowFareCalendar_1']").find_elements_by_css_selector("div.air-low-fare-calendar-matrix-secondary_last")
        #to_flights = to_flights.find_elements_by_css_selector("div.air-low-fare-calendar-matrix-secondary")

        print(f"Found flights for {airport}")
        trip = driver.find_element_by_xpath("//span[@class='air-stations-heading--origin-destination']").text
        print(f"---------{trip}---------------------")

        #while weAreDone == False:
        for flight in to_flights:
          #print("Loop!")
          try:
            day = flight.find_element_by_xpath(".//div[@class='content-cell--day']").text
            if day == to_date[-2:]:
              to_price = flight.find_element_by_xpath(".//span[@class='content-cell--fare-usd']")
            elif day == rtn_date[-2:]:
              rtn_price = flight.find_element_by_xpath(".//span[@class='content-cell--fare-usd']")
              weAreDone = True
              #print("Done!")
              break
          except:
            pass
        
        for flight in rtn_flights:
          #print("Loop!")
          try:
            day = flight.find_element_by_xpath(".//div[@class='content-cell--day']").text
            if day == rtn_date[-2:]:
              rtn_price = flight.find_element_by_xpath(".//span[@class='content-cell--fare-usd']")
              break
          except:
            pass


        print(f'{IATA_origin} > {airport}\t${to_price}\n{airport} > {IATA_origin}\t${rtn_price}\nTotal Price: ${to_price+rtn_price}')
      except:
        pass
    
    except IOError:
      pass
    
    search_date += one_day_delta

if __name__ == "__main__":
  main()