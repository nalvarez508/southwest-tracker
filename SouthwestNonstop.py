# SWA Flight Schedule Scraper // Nick Alvarez c 2021
# Functional. They don't care about scraping flight schedules.

from datetime import date, timedelta
from progressbar import progressbar
import subprocess
import logging
import calendar
import time
import signal
import requests
import sys

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

# I hate global variables
search_date = date.today()
return_date = date.today()
direct_enabled = False

def main():
  global search_date, return_date

  # User input for origin/destination
  IATA_origin = input("Origin: ").upper()
  IATA_destination = input("Destination: ").upper()

  # Find last bookable date from 'data.js'
  data = requests.get("https://www.southwest.com/swa-ui/bootstrap/air-flight-schedules/1/data.js").text.strip().split("\n")
  data = [i for i in data if "currentLastBookableDate" in i]
  last_bookable_date = data[0].replace(" ","").replace('"currentLastBookableDate":"',"").replace('",',"").split("-")
  end_date = date(int(last_bookable_date[0]), int(last_bookable_date[1]), int(last_bookable_date[2]))
  one_day_delta = timedelta(days=1)
  return_date = end_date

  print(f"\nFlight schedules can be seen up to {end_date}.")

  # User input for travel dates if not in 'all' mode
  def datesInput():
    global search_date, return_date
    search_date = input("Departure date (YYYY-MM-DD): ")
    return_date = input("Return date (YYYY-MM-DD): ")
    search_date = date(int(search_date.split("-")[0]), int(search_date.split("-")[1]), int(search_date.split("-")[2]))
    return_date = date(int(return_date.split("-")[0]), int(return_date.split("-")[1]), int(return_date.split("-")[2]))

    while (return_date > end_date) or (search_date < date.today()):
      print(f"Error! Impossible schedule. Flight schedules can be seen up to {end_date}.")
      datesInput()

    print()
  
  # Checks for nonstop flights from origin to destination
  def roundtrip(orig, dest):
    URL = f"https://www.southwest.com/air/flight-schedules/results.html?departureDate={search_date}&destinationAirportCode={dest}&originationAirportCode={orig}&scheduleViewType=daily&timeOfDay=ALL_DAY"
    global direct_enabled

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

        #def gatherInfo(flight_num, flight_time):
        #  flight_num = flight.find_element_by_xpath(".//span[@aria-hidden='true']").text
        #  flight_num = flight_num.replace(" ", "")
        #  flight_time = flight.find_elements_by_xpath(".//span[@class='time--value']")

        # For each flight, check if it is nonstop (it will cause exception otherwise), gather flight info
        for flight in flight_list:
          flight_num = ""
          flight_time= []
          try:
            if direct_enabled:
              try:
                if "no plane change" == flight.find_element_by_xpath(".//span[@class='flight-stops--item-description flight-stops--item-description_one-stop']").text.lower():
                  search = "Direct"
                  flight_num = flight.find_element_by_xpath(".//span[@aria-hidden='true']").text
                  flight_num = flight_num.replace(" ", "")
                  flight_time = flight.find_elements_by_xpath(".//span[@class='time--value']")
              except:
                search = flight.find_element_by_xpath(".//span[@class='flight-stops--item-description_nonstop']").text
                flight_num = flight.find_element_by_xpath(".//span[@aria-hidden='true']").text
                flight_num = flight_num.replace(" ", "")
                flight_time = flight.find_elements_by_xpath(".//span[@class='time--value']")
            else:
              search = flight.find_element_by_xpath(".//span[@class='flight-stops--item-description_nonstop']").text
              flight_num = flight.find_element_by_xpath(".//span[@aria-hidden='true']").text
              flight_num = flight_num.replace(" ", "")
              flight_time = flight.find_elements_by_xpath(".//span[@class='time--value']")
            response = f"{calendar.day_abbr[search_date.weekday()]}\t{search_date}\t{orig}-{dest}\t{flight_num}\t{flight_time[0].text}\t{flight_time[1].text}"
            if direct_enabled:
              response += f"\t{search}"
            print(response)
          except:
            pass
      except:
        pass
    
    # Ctrl-C
    except IOError:
      pass
  
  # Checks every day until it reaches end of booking results
  def searchAndPrint(count=2):
    global search_date, return_date
    print(f"----------------------{search_date}----------------------")
    if (count == 2) or (count == 0):
      roundtrip(IATA_origin, IATA_destination)
    if (count == 2) or (count == 1):
      roundtrip(IATA_destination, IATA_origin)

    # If we are not in 'all' or 'interval' mode, do not increment the day, go to the return date
    try:
      if mode != None:
        search_date += one_day_delta
    except NameError:
      search_date = return_date
  
  # Checking for command line arguments
  try:
    global direct_enabled
    try:
      for arg in sys.argv:
        if 'direct' == arg:
          direct_enabled = True
        continue
    except IndexError:
      pass
    mode = sys.argv[1]
    if mode == 'all':
      # Up to last booking day
      days = end_date-search_date
      for i in progressbar(range(days.days), redirect_stdout=True):
        searchAndPrint()
    elif mode == 'interval':
      datesInput()
      days = return_date-search_date
      # Up to return day
      for i in progressbar(range(days.days), redirect_stdout=True):
        searchAndPrint()
    elif mode == 'direct':
      datesInput()
      for d in progressbar(range(0,2), redirect_stdout=True): # Only two days
        searchAndPrint(d)
  except IndexError:
    datesInput()
    for d in progressbar(range(0,2), redirect_stdout=True): # Only two days
      searchAndPrint(d)

if __name__ == "__main__":
  main()