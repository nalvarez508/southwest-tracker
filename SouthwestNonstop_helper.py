# SWA Flight Schedule Scraper // Nick Alvarez c 2021
# Functional. They don't care about scraping flight schedules.

from datetime import date, datetime, timedelta
from os import abort
from progressbar import progressbar
import queue
import base64
import subprocess
import logging
import calendar
import time
import signal
from python_utils.converters import to_float
import requests
import sys
import threading
import urllib.parse
from urllib import *

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

class Schedule:
  def __init__(self):
    # Chrome options to disable logging in terminal
    #signal.signal(signal.SIGINT, exitHandler)
    self.chrome_options = Options()
    self.chrome_options.add_argument("--headless")
    self.chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    self.to_driver = webdriver.Chrome(service_log_path='NULL', options=self.chrome_options)
    self.rtn_driver = webdriver.Chrome(service_log_path='NULL', options=self.chrome_options)

    self.direct_enabled = False
    self.search_type = "roundtrip"

    self.airportInfo = {}
    self.IATA_origin = ""
    self.IATA_destination = ""
    self.last_bookable_date = date.today()
    self.end_date = None
    self.return_date = date.today()
    self.search_date = date.today()

    self.getAirportInfo()
    self.getLastBookableDate()

  #global search_date, return_date

  # User input for origin/destination
  #IATA_origin = input("Origin: ").upper()
  #IATA_destination = input("Destination: ").upper()

  # Find last bookable date from 'data.js'

  def getAirportInfo(self):
    self.to_driver.get("https://www.southwest.com/flight/routemap_dyn.html")
    airports = self.to_driver.find_elements_by_xpath(".//span[@class='swa-component-city-list--button-title js-accordion-button-label']")
    #self.airportInfo = {}
    for airport in airports:
      button_title = (airport.get_attribute('innerHTML'))
      self.airportInfo[button_title[:-6]] = button_title[-3:]
  def returnAirportInfo(self):
    return self.airportInfo
  
  # Add find code by airport, vice/versa
  # Return list?

  def getLastBookableDate(self):
    data = requests.get("https://www.southwest.com/swa-ui/bootstrap/air-flight-schedules/1/data.js").text.strip().split("\n")
    data = [i for i in data if "currentLastBookableDate" in i]
    self.last_bookable_date = data[0].replace(" ","").replace('"currentLastBookableDate":"',"").replace('",',"").split("-")
    self.end_date = date(int(self.last_bookable_date[0]), int(self.last_bookable_date[1]), int(self.last_bookable_date[2]))
    self.return_date = self.end_date
  def returnLastBookableDate(self):
    return self.end_date
  def setSearchDate(self, d):
    self.search_date = d
  def getSearchDate(self):
    return self.search_date
  def setReturnDate(self, d):
    self.return_date = d
  def getReturnDate(self):
    return self.return_date

  def setDirectEnabled(self, e):
    self.direct_enabled = e
  def setSearchType(self, t):
    self.search_type = t
  def returnDirectEnabled(self):
    return self.direct_enabled
  def returnSearchType(self):
    return self.search_type
  
  def setOrigin(self, o):
    self.IATA_origin = o
  def setDestination(self, d):
    self.IATA_destination = d

  def returnCityPhoto(self, c):
    URL = f"https://www.google.com/search?tbm=isch&q={urllib.parse.quote(c)}"
    self.to_driver.get(URL)
    image = WebDriverWait(self.to_driver,5).until(EC.presence_of_element_located((By.XPATH, "//img[@class='rg_i Q4LuWd']")))
    #self.to_driver.find_element_by_xpath("//div[@class='islrc']")

    def checkIfB64(src):
      header = src.split(',')[0]
      if header.startswith('data') and ';base64' in header:
        imgType = header.replace('data:image/', '').replace(';base64', '')
        return imgType
      return None
    
    s = image.get_attribute('src')
    if s is not None:
      if checkIfB64(s):
        #print(s.split(';base64,')[1])
        return (s.split(';base64,')[1])
      else:
        return None
    else:
      return None
    #imageURL = image.find_element_by_xpath(".//img[@class='rg_i Q4LuWd']")

  #airports = to_driver.find_element_by_xpath("//div[@id='departure-accordion-tablist-container']")
  #airportDisplayNames = airports.find_elements_by_xpath(".//div[@class='swa-component-city-list--holder swa-component-accordion-tab js-accordion-tab']")


  #print(airportDisplayNames.text)
  #airportDisplayNames = to_driver

  #print(f"\nFlight schedules can be seen up to {end_date}.")

  # User input for travel dates if not in 'all' mode
  def datesInput(self):
    #global search_date, return_date
    self.search_date = input("Departure date (YYYY-MM-DD): ")
    self.return_date = input("Return date (YYYY-MM-DD): ")
    self.search_date = date(int(self.search_date.split("-")[0]), int(self.search_date.split("-")[1]), int(self.search_date.split("-")[2]))
    self.return_date = date(int(self.return_date.split("-")[0]), int(self.return_date.split("-")[1]), int(self.return_date.split("-")[2]))

    while (self.return_date > self.end_date) or (search_date < date.today()):
      print(f"Error! Impossible schedule. Flight schedules can be seen up to {self.end_date}.")
      self.datesInput()

    print()

  # Checks for nonstop flights from origin to destination
  def roundtrip(self, orig, dest, driver):
    URL = f"https://www.southwest.com/air/flight-schedules/results.html?departureDate={self.search_date}&destinationAirportCode={dest}&originationAirportCode={orig}&scheduleViewType=daily&timeOfDay=ALL_DAY"
    #global direct_enabled
    finalAnswer = ""

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
            if self.direct_enabled:
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
            #response = f"{calendar.day_abbr[self.search_date.weekday()]}\t{self.search_date}\t{orig}-{dest}\t{flight_num}\t{flight_time[0].text}\t{flight_time[1].text}"
            response = f"{calendar.day_abbr[self.search_date.weekday()]} {self.search_date.strftime('%m/%d')} {flight_num}\t{flight_time[0].text}-{flight_time[1].text}"
            if self.direct_enabled:
              #response += f"\t{search}"
              if search == "Direct":
                response += " (D)"
            finalAnswer += f'{response}\n'
          except:
            pass
      except:
        pass

      return finalAnswer
    # Ctrl-C
    except IOError:
      pass

  # Checks every day until it reaches end of booking results
  def searchAndPrint(self, count=2):
    #global search_date, return_date
    #print(f"----------------------{self.search_date}----------------------")

    def goingToFlights(q):
      if (count == 2) or (count == 0):
        t = self.roundtrip(self.IATA_origin, self.IATA_destination, self.to_driver)
        q.put(t)
        event_t1.set()

    def comingFromFlights(q):
      if (count == 2) or (count == 1):
        r = self.roundtrip(self.IATA_destination, self.IATA_origin, self.rtn_driver)
        q.put(r)
        event_t2.set()

    q1 = queue.Queue()
    q2 = queue.Queue()
    t1 = threading.Thread(target=goingToFlights, args=[q1])
    t2 = threading.Thread(target=comingFromFlights, args=[q2])
    t1.daemon = True
    t2.daemon = True
    event_t1 = threading.Event()
    event_t2 = threading.Event()
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    event_t1.wait()
    event_t2.wait()
    goingTo = q1.get()
    comingFrom = q2.get()
    #print(f'{goingTo}{comingFrom}')

    # If we are not in 'all' or 'interval' mode, do not increment the day, go to the return date
    try:
      if self.search_type != None:
        self.search_date += timedelta(days=1)
    except NameError:
      self.search_date = self.return_date
    if (goingTo or comingFrom) is not None:
      return [goingTo, comingFrom]


'''
# Checking for command line arguments
try:
  #global direct_enabled
  try:
    for arg in sys.argv:
      if 'direct' == arg:
        direct_enabled = True
      continue
  except IndexError:
    pass
  mode = sys.argv[1]
  if mode == 'all':
    #while search_date < end_date: # Up to last booking day
    days = end_date-search_date
    for i in progressbar(range(days.days), redirect_stdout=True):
      searchAndPrint()
  elif mode == 'interval':
    datesInput()
    days = return_date-search_date
    #while search_date <= return_date: # Up to return day
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
'''