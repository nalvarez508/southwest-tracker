from datetime import date, timedelta
import subprocess
import logging
import calendar
import time
from selenium.webdriver.remote.remote_connection import LOGGER as seleniumLogger
seleniumLogger.setLevel(logging.WARNING)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
driver = webdriver.Chrome(service_log_path='NULL', chrome_options=chrome_options)

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
      #print("Begin sleep")
      time.sleep(1)
      #print("End sleep")
      flights = driver.find_element_by_xpath("//div[@class='accordion']")
      flight_list = flights.find_elements_by_css_selector("div.accordion-panel")

      for flight in flight_list:
        #duration = flight.find_element_by_xpath(".//span[@class='flight-stops--duration-time']").text
        try:
          search = flight.find_element_by_xpath(".//span[@class='flight-stops--item-description_nonstop']").text
          #times = flight.find_elements_by_css_selector("div.air-operations-time-status")
          flight_num = flight.find_element_by_xpath(".//span[@aria-hidden='true']").text
          flight_num = flight_num.replace(" ", "")
          #print(len(times))
          #flight_time = [None]
          x=0
          #try:
          #  for time in times:
          #    flight_time[x] = time.find_element_by_xpath(".//span[@class='time--value']").text
          #    print("Got a flight time!")
          #    x+=1
              #flight_time[1] = time.find_element_by_xpath(".//span[@class='time--value']").text
          #except IndexError:
          #  print("Looped it up.")
          #print(f"{calendar.day_abbr[search_date.weekday()]}\t{search_date}\tFlight {flight_num}\t{flight_time[0]}\t{flight_time[0]}")
          print(f"{calendar.day_abbr[search_date.weekday()]}\t{search_date}\tFlight {flight_num}")
          #print(search.text)
        except:
          pass
    except:
      pass
  
  except KeyboardInterrupt:
    exit()
  
  search_date += one_day_delta
  print(f"----------------------{search_date}----------------------")