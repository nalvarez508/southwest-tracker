from datetime import date, timedelta
import subprocess
import logging
import calendar
import time
import signal

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

def main():
  IATA_origin = input("Origin: ").upper()
  IATA_destination = input("Destination: ").upper()
  search_date = date.today()
  end_date = date(2021,11,5) # Southwest far booking date. To be pulled from site in future
  one_day_delta = timedelta(days=1)

  while search_date < end_date:
    URL = f"https://www.southwest.com/air/flight-schedules/results.html?departureDate={search_date}&destinationAirportCode={IATA_destination}&originationAirportCode={IATA_origin}&scheduleViewType=daily&timeOfDay=ALL_DAY"

    try:
      driver.get(URL)
      try:
        try:
          WebDriverWait(driver,5).until(EC.presence_of_element_located((By.XPATH, "//div[@class='accordion']")))
        except TimeoutException:
          pass
        
        flights = driver.find_element_by_xpath("//div[@class='accordion']")
        flight_list = flights.find_elements_by_css_selector("div.accordion-panel")

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