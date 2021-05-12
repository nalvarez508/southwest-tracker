# SWA Flight Schedule Scraper // Nick Alvarez c 2021
# Functional. They don't care about scraping flight schedules.

from datetime import date, timedelta
import subprocess
import logging
import calendar
import time
import signal
import requests

from selenium.webdriver.remote.remote_connection import LOGGER as seleniumLogger
seleniumLogger.setLevel(logging.WARNING)
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Keyboard interrupts
def exitHandler(signum, frame):
  exit(0)

# Chrome options to disable logging in terminal
signal.signal(signal.SIGINT, exitHandler)
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
driver = webdriver.Chrome(service_log_path='NULL', options=chrome_options)

def main():
  # User input for origin/destination
  IATA_origin = input("Origin: ").upper()
  IATA_destination = input("Destination: ").upper()
  search_date = date.today()

  # Find last bookable date from 'data.js'
  data = requests.get("https://www.southwest.com/swa-ui/bootstrap/air-flight-schedules/1/data.js").text.strip().split("\n")
  data = [i for i in data if "currentLastBookableDate" in i]
  last_bookable_date = data[0].replace(" ","").replace('"currentLastBookableDate":"',"").replace('",',"").split("-")
  end_date = date(int(last_bookable_date[0]), int(last_bookable_date[1]), int(last_bookable_date[2]))
  one_day_delta = timedelta(days=1)

  print(f"Flight schedules can be seen up to {end_date}.\n")

  # Checks every day until it reaches end of booking results
  while search_date < end_date:
    URL = f"https://www.southwest.com/air/flight-schedules/results.html?departureDate={search_date}&destinationAirportCode={IATA_destination}&originationAirportCode={IATA_origin}&scheduleViewType=daily&timeOfDay=ALL_DAY"

    try:
      driver.get(URL)
      try:
        try: # Makes sure page is loaded, else times out
          WebDriverWait(driver,5).until(EC.presence_of_element_located((By.XPATH, "//div[@class='accordion']")))
        except TimeoutException:
          pass
        
        # Gather list of flights
        flights = driver.find_element_by_xpath("//div[@class='accordion']")
        flight_list = flights.find_elements_by_css_selector("div.accordion-panel")

        # For each flight, check if it is nonstop (it will cause exception otherwise), gather flight info
        for flight in flight_list:
          try:
            search = flight.find_element_by_xpath(".//span[@class='flight-stops--item-description_nonstop']").text
            flight_num = flight.find_element_by_xpath(".//span[@aria-hidden='true']").text
            flight_num = flight_num.replace(" ", "")
            flight_time = flight.find_elements_by_xpath(".//span[@class='time--value']")
            print(f"{calendar.day_abbr[search_date.weekday()]}\t{search_date}\tFlight {flight_num}\t{flight_time[0].text}\t{flight_time[1].text}")
          except:
            pass
      except:
        pass
    
    # Ctrl-C
    except IOError:
      pass
    
    search_date += one_day_delta
    print(f"----------------------{search_date}----------------------")

if __name__ == "__main__":
  main()