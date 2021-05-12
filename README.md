# southwest-tracker

This project was originally designed to determine if there were nonstop flights between a location - specifically, Sacramento to Orlando. It's listed on the airport sites as having nonstop (seasonal) service, but I did not know when that season was.

#### Dependencies

Selenium is required to use this application. You can get it with
`pip install selenium`
assuming `pip` is in the PATH variable. On Windows, I use `py -3 -m pip install selenium`.

You will also need a webdriver for Selenium. This program is set up to use the Chrome webdriver. This can be downloaded from [Selenium's Developer Website](https://www.selenium.dev/documentation/en/webdriver/driver_requirements/#quick-reference). Your PATH variable will need to be updated with wherever you saved the executable.

### Southwest Nonstop
Loads daily flight schedules, checks if a nonstop flight(s) exist, and prints it out. Accepts an origin and destination in the form of IATA airport code. Roundtrip flights returned.

Example output:
```
Origin: RNO
Destination: PHX
Flight schedules can be seen up to 2021-11-05.

----------------------2021-05-12----------------------
Wed     2021-05-12      RNO-PHX #4505   6:05AM  7:50AM
Wed     2021-05-12      RNO-PHX #3880   1:45PM  3:30PM
Wed     2021-05-12      PHX-RNO #3569   8:45AM  10:35AM
Wed     2021-05-12      PHX-RNO #4739   8:50PM  10:40PM
----------------------2021-05-13----------------------
Thu     2021-05-13      RNO-PHX #1772   6:00AM  7:45AM
Thu     2021-05-13      RNO-PHX #279    11:10AM 12:55PM
Thu     2021-05-13      RNO-PHX #1246   4:45PM  6:30PM
Thu     2021-05-13      PHX-RNO #278    8:35AM  10:20AM
Thu     2021-05-13      PHX-RNO #1546   12:10PM 1:55PM
Thu     2021-05-13      PHX-RNO #2054   9:00PM  10:45PM
```
If flights are not found, there will be no output other than a reassurance indicator that the program is still searching:
```
Origin: SMF
Destination: MCO
Flight schedules can be seen up to 2021-11-05.

----------------------2021-05-12----------------------
----------------------2021-05-13----------------------
----------------------2021-05-14----------------------
----------------------2021-05-15----------------------
```

The program expects that the IATA codes entered are valid Southwest destinations. Unlike the Southwest Prices program, I did not implement the airport code scraper to perform validation. If an airport code is incorrect, you'll notice the dates will still appear but will take noticeably longer, as it is timing out looking for the accordion element.

**Future Work:** Instead of using the daily pages, check by week. Would require checking where the plane icon is in the weekday columns.

**Bugs:** Sometimes, when terminating with Ctrl-C, the program will dump the traceback.

### Southwest Prices
Check Southwest ticket prices as Google Flights does not support it. The code here is all functional, to the best of my knowledge, but Southwest detects that we are using a webscraper so it redirects us to the homepage.

Right now, the program was configured to take an origin airport, travel dates, and check the lowest price to every destination on Southwest's network. If you didn't know where to go but wanted to spend the least, this would be for you.

Example output *should* look like this, but in reality, this is all theoretical. We may never know.

```
RNO > MSY	$233	#2191/575	6:15 AM - 3:55 PM	1 stops MDW	7h 40m
MSY > RNO	$179	#5516/5040	5:50 AM - 10:55 AM	1 stops DEN	7h 5m
Total Price: $412
```
So if you can find a way to be undetected, by all means, let me know.
