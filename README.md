# southwest-tracker

This project was originally designed to determine if there were nonstop flights between a location - specifically, Sacramento to Orlando. It's listed on the airport sites as having nonstop (seasonal) service, but I did not know when that season was.

**Update March 2022:** Southwest either blocked my IP or scraping overall. Rest in peace Southwest Tracker.

## Update

Two major updates are NOT underway.

The addition of threading has cut search times by 53%, a major improvement.

The flight schedules program now has a GUI, currently under development and testing. A few bugs in that one, for sure. Updated documentation is coming soon for that revision.

#### Dependencies

Selenium and progressbar are required to use this application. You can get them with
`pip install selenium progressbar`
assuming `pip` is in the PATH variable. On Windows, I use `py -3 -m pip install selenium progressbar`.

You will also need a webdriver for Selenium. This program is set up to use the Chrome webdriver. This can be downloaded from [Selenium's Developer Website](https://www.selenium.dev/documentation/en/webdriver/driver_requirements/#quick-reference). Your PATH variable will need to be updated with wherever you saved the executable.

### Southwest Nonstop
There are three operational modes to this but the goal is to find nonstop flights.

#### Search All
Searches for nonstop flights, both to and from, between the current date and last available booking date.

Example output:
`> python3 SouthwestNonstop.py all`
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

#### Search Interval
Searches for nonstop flights, both to and from, between the specified departure and return dates.

Example output:
`> python3 SouthwestNonstop.py interval`
```
Origin: DEN
Destination: CHS

Flight schedules can be seen up to 2021-11-05.
Departure date (YYYY-MM-DD): 2021-06-03
Return date (YYYY-MM-DD): 2021-06-05

----------------------2021-06-03----------------------
Thu     2021-06-03      DEN-CHS #1171   11:20AM 4:40PM
Thu     2021-06-03      CHS-DEN #2073   4:35PM  6:20PM
----------------------2021-06-04----------------------
Fri     2021-06-04      DEN-CHS #1171   11:20AM 4:40PM
Fri     2021-06-04      CHS-DEN #2073   4:35PM  6:20PM
----------------------2021-06-05----------------------
Sat     2021-06-05      DEN-CHS #4281   11:35AM 4:55PM
Sat     2021-06-05      DEN-CHS #5547   3:45PM  9:05PM
Sat     2021-06-05      CHS-DEN #4321   5:40PM  7:25PM
```

#### Search Trip
Searches for nonstop flights, to and then from, on the specified departure and return dates.

Example output:
`> python3 SouthwestNonstop.py`
```
Origin: SEA
Destination: OAK

Flight schedules can be seen up to 2021-11-05.
Departure date (YYYY-MM-DD): 2021-07-05
Return date (YYYY-MM-DD): 2021-08-09

----------------------2021-07-05----------------------
Mon     2021-07-05      SEA-OAK #1686   5:55AM  8:00AM
Mon     2021-07-05      SEA-OAK #1158   11:25AM 1:35PM
Mon     2021-07-05      SEA-OAK #1819   4:00PM  6:20PM
Mon     2021-07-05      SEA-OAK #1763   7:25PM  9:30PM
Mon     2021-07-05      SEA-OAK #354    10:00PM 12:10AM
----------------------2021-08-09----------------------
Mon     2021-08-09      OAK-SEA #376    6:20AM  8:30AM
Mon     2021-08-09      OAK-SEA #1157   8:20AM  10:25AM
Mon     2021-08-09      OAK-SEA #1817   1:10PM  3:15PM
Mon     2021-08-09      OAK-SEA #319    4:45PM  6:45PM
Mon     2021-08-09      OAK-SEA #1665   7:05PM  9:10PM
```

#### Direct Flights
Another argument that can be passed in is one to search for direct flights (no plane change) as well as nonstop flights. This is taken after any arguments from above.

Commands:

`> python3 SouthwestNonstop.py direct`

`> python3 SouthwestNonstop.py interval direct`

`> python3 SouthwestNonstop.py all direct`

Example output:
`> python3 SouthwestNonstop.py all direct`
```
Origin: RNO
Destination: LAX

Flight schedules can be seen up to 2021-11-05.
Departure date (YYYY-MM-DD): 2021-05-12
Return date (YYYY-MM-DD): 2021-05-13

----------------------2021-05-12----------------------
Wed     2021-05-12      RNO-LAX #2529   3:25PM  4:55PM  Nonstop
----------------------2021-05-13----------------------
Thu     2021-05-13      LAX-RNO #3693   1:45PM  3:10PM  Nonstop
Thu     2021-05-13      LAX-RNO #1847   6:15PM  9:05PM  Direct
```

#### Generalities
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

If the dates entered are either before the current date or after the last booking date, you will be prompted to enter them again.

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
