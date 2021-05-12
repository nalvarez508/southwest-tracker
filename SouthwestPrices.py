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
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def exitHandler(signum, frame):
  exit(0)

signal.signal(signal.SIGINT, exitHandler)
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
driver = webdriver.Chrome(service_log_path='NULL', options=chrome_options)

airports = []

def getAirportCodes(data):
  prog = re.compile(r'\bid\b')
  for iata in data:
    m = prog.search(iata)
    try:
      airports.append(m.string.replace('"id": "',"").replace('",',""))
    except AttributeError:
      pass

def main():
  IATA_origin = input("Origin: ").upper()
  #IATA_destination = input("Destination: ").upper()
  search_date = date.today()
  data = requests.get("https://www.southwest.com/swa-ui/bootstrap/air-flight-schedules/1/data.js").text.strip().split("\n")
  last_bookable = [i for i in data if "currentLastBookableDate" in i]
  last_bookable_date = last_bookable[0].replace(" ","").replace('"currentLastBookableDate":"',"").replace('",',"").split("-")
  end_date = date(int(last_bookable_date[0]), int(last_bookable_date[1]), int(last_bookable_date[2]))
  one_day_delta = timedelta(days=1)

  print(f"Flight schedules can be seen up to {end_date}.\n")

  getAirportCodes(data)

  for airport in airports:
    URL = f"https://www.southwest.com/air/low-fare-calendar/select-dates.html?adultPassengersCount=1&currencyCode=USD&departureDate={to_date}&destinationAirportCode={IATA_codes[iata]}&originationAirportCode={IATA_origin}&passengerType=ADULT&returnAirportCode=&returnDate={rtn_date}&tripType=roundtrip"

    try:
      driver.get(URL)
      try:
        try:
          WebDriverWait(driver,5).until(EC.presence_of_element_located((By.XPATH, "//div[@class='air-low-fare-calendar-matrix-secondary']")))
        except TimeoutException:
          pass
        
        flights = driver.find_element_by_xpath("//div[@class='air-low-fare-calendar-matrix-secondary']")
        flight_list = flights.find_elements_by_css_selector("div.calendar-matrix--cell-container")

        for flight in flight_list:
          #duration = flight.find_element_by_xpath(".//span[@class='flight-stops--duration-time']").text
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
    
    except IOError:
      pass
    
    search_date += one_day_delta
    print(f"----------------------{search_date}----------------------")

if __name__ == "__main__":
  main()