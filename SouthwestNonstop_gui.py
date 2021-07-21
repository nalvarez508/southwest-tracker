import base64, gc
from datetime import datetime, date
import sys
from io import BytesIO
import PIL.Image, PIL.ImageTk, PIL.ImageFile
import requests
from threading import Thread
from threading import Event as ev
import time

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from tkinter.ttk import Progressbar
from tkinter import *
from tkcalendar import Calendar
import SouthwestNonstop_helper as swa

class GUI_Elements:
  def __init__(self):
    self.title = "Southwest Flight Schedules"
    self.airports = []
    self.origin = None
    self.destination = None

    self.searchTypes = [("All Flights", "all"), ("Date Interval", "interval"), ("Roundtrip", "")]

    self.height = 10
    self.width = 35
    self.searchBarLength = 250
    self.photo_city1 = None
    self.photo_city2 = None
  
  def setCityPhoto(self, cityNo, data):
    if cityNo == 1:
      #self.photo_city1 = PhotoImage(file="test11.png").subsample(2,2)
      self.photo_city1 = data
    elif cityNo == 2:
      #self.photo_city2 = PhotoImage(file="test22.PNG").subsample(2,2)
      self.photo_city2 = data
  def getCityPhoto(self, cityNo):
    if cityNo == 1:
      #return PhotoImage(file="test11.png").subsample(2,2)
      return self.photo_city1
    elif cityNo == 2:
      #return PhotoImage(file="test22.PNG").subsample(2,2)
      return self.photo_city2

  def setAirports(self, d):
    self.airports = d
  def getAirports(self):
    return self.airports
  def setOrigin(self, o):
    self.origin = o
  def setDestination(self, d):
    self.destination = d
  def getOrigin(self):
    return self.origin
  def getDestination(self):
    return self.destination
  def getAirportCode(self, c):
    return self.airports[c]

def main():
  PIL.ImageFile.LOAD_TRUNCATED_IMAGES = True
  schedule = None
  elements = None

  ## Loading splash screen
  loading = Tk()
  loading.attributes("-disabled", True)
  Label(loading, text="Loading...", font=('', 12, 'normal')).grid(padx=12, pady=8)
  
  ## Run our grueling tasks in a thread with progress bar
  def startup():
    notDone = True
    def loadingProgress():
      while notDone:
        for i in range(10):#200
          loading.update_idletasks()
          pb1['value'] += 1.5#0.5
          #time.sleep(0.023)
          time.sleep(0.01)
      loading.destroy()
    def classInit():
      nonlocal schedule, elements, notDone
      schedule = swa.Schedule()
      elements = GUI_Elements()
      elements.setAirports(schedule.returnAirportInfo())
      notDone = False
    t1 = Thread(target=classInit)
    t1.start()
    loadingProgress()
    t1.join()
  
  pb1 = Progressbar(loading, orient=HORIZONTAL, length=100, mode='indeterminate')
  pb1.grid(padx=12, pady=4)
  loading.after(200, startup)
  loading.mainloop()
  del loading
  gc.collect()

  # Simplified grid setup, for rows and columns
  def gridConfigure(obj, rowList=[], columnList=[]):
    for row in rowList:
      obj.grid_rowconfigure(row, weight=1)
    for column in columnList:
      obj.grid_columnconfigure(column, weight=1)
  
  # Changes image and label, for thread usage
  def updateImageAndLabel(e, p, no):
    loadImage(e.widget.get(), no)
    p.configure(image=elements.getCityPhoto(no))

  # Gathers image from Google and creates PhotoImage object
  def loadImage(c, no):
    try:
      fh = BytesIO(base64.b64decode(schedule.returnCityPhoto(c)))
      img = PIL.Image.open(fh, mode='r')
      img.thumbnail((250,150), PIL.Image.ANTIALIAS)
      render = PIL.ImageTk.PhotoImage(image=img)
      elements.setCityPhoto(no, render)
    except TclError:
      pass
  
  # These may not be necessary since we call them anyways in beginSearch()
  def callSearchFunc():
    schedule.setSearchType(searchType_.get())
  def callDirectFunc():
    schedule.setDirectEnabled(direct_.get())

  def callbackOrigin(eventObject):
    elements.setOrigin(eventObject.widget.get())
    #loadImage(eventObject.widget.get(), 1)
    t1 = Thread(target=updateImageAndLabel, args=[eventObject, pic_origin, 1])
    t1.start()
    rightResultsTitle.configure(text=f"Flights to {elements.getOrigin()}")
    clearList()
  def callbackDestination(eventObject):
    elements.setDestination(eventObject.widget.get())
    #loadImage(eventObject.widget.get(), 2)
    t2 = Thread(target=updateImageAndLabel, args=[eventObject, pic_destination, 2])
    t2.start()
    leftResultsTitle.configure(text=f"Flights to {elements.getDestination()}")
    clearList()
  
  # For anything but 'all flights' we must gather date range
  def datesInput():
    today = datetime.today()
    todayList = [int(today.strftime('%Y')), int(today.strftime('%m')), int(today.strftime('%d'))]

    # Checking if dates make sense
    def dateValidate():
      departDate = datetime.strptime(toCal.get_date(), '%m/%d/%y')
      returnDate = datetime.strptime(fromCal.get_date(), '%m/%d/%y')

      if departDate > returnDate:
        messagebox.showerror(title="Date Validation Error", message="The return date must be after the departure date.")
        calRoot.lift()
      elif (departDate < today) or (returnDate < today):
        messagebox.showerror(title="Date Validation Error", message="The selected dates cannot be in the past!")
        calRoot.lift()
      elif departDate <= returnDate:
        schedule.setSearchDate(departDate.date())
        schedule.setReturnDate(returnDate.date())
        calRoot.destroy()
      else:
        pass
    
    def onClose():
      calRoot.destroy()
      return False

    ## Window Creation
    calRoot = Tk()
    calRoot.title("Southwest Flight Schedules")
    calCalFrame = Frame(calRoot)
    calTitleFrame = Frame(calRoot)
    calButtonFrame = Frame(calRoot)
    gridConfigure(calRoot, [0,1,2], [0])

    ## Title
    calTitleFrame.grid(row=0,column=0,sticky='ew')
    gridConfigure(calTitleFrame, [0,1], [0,1])
    Label(calTitleFrame, text="Date Selection", font=('', 18, 'bold')).grid(row=0, column=0, pady=4, columnspan=2)
    Label(calTitleFrame, text="Departing").grid(row=1, column=0, padx=4, columnspan=1, sticky='ew')
    Label(calTitleFrame, text="Returning").grid(row=1, column=1, padx=4, columnspan=1, sticky='ew')

    ## Two Calendars
    calCalFrame.grid(row=1,column=0,sticky='ew')
    gridConfigure(calCalFrame, [0], [0,1])
    toCal = Calendar(calCalFrame, selectmode = 'day', year = todayList[0], month = todayList[1], day = todayList[2])
    toCal.grid(row=0, column=0, padx=4)
    fromCal = Calendar(calCalFrame, selectmode = 'day', year = todayList[0], month = todayList[1], day = todayList[2]+1)
    fromCal.grid(row=0, column=1, padx=4)

    ## Submit Button
    calButtonFrame.grid(row=2, column=0, sticky='ew')
    gridConfigure(calButtonFrame, [0], [0])
    Button(calButtonFrame, text="Submit", command=dateValidate).grid(row=2,column=0,pady=4, columnspan=1)

    calRoot.lift()
    calRoot.protocol("WM_WINDOW_DESTROY", onClose)
    calRoot.mainloop()
    del calRoot
    gc.collect()

  def listUpdate(f):
    leftResults.insert('end', f[0])
    rightResults.insert('end', f[1])
    root.update_idletasks()
  def clearList():
    leftResults.delete(1.0, tk.END)
    rightResults.delete(1.0, tk.END)

  # Search function when button is pressed
  def beginSearch():
    nonlocal searchButton
    def stopIt():
      stopTheSearch.set()
      searchButton.configure(text="Search", command=beginSearch)
    def checkStop():
      if stopTheSearch.is_set():
        return 1

    # Sending data to Class schedule and creating progressbar
    # Thread issue caused by datesInput()
    schedule.setDirectEnabled(direct_.get())
    schedule.setSearchType(searchType_.get())
    schedule.setOrigin(elements.getAirportCode(IATA_origin.get()))
    schedule.setDestination(elements.getAirportCode(IATA_destination.get()))
    '''if searchType_.get() == ('interval' or None):
      if datesInput():
        pass
      else:
        pass'''
    
    root.update()
    searchButton.configure(text="Stop", command=stopIt, fg='red')
    root.update_idletasks()
    pb2 = Progressbar(root, orient=HORIZONTAL, length=elements.searchBarLength, mode='determinate')
    pb2.grid(row=7, column=0, pady=2)
    clearList()

    def addSearchProgress(p):
      pb2['value'] += (p/(float(elements.searchBarLength/100)))
      root.update_idletasks()

    # Beginning the search. Runs until stop button is hit or it finishes.
    def getResults():
      # Gather relevant data
      # Execute correct commands
      # Should be able to use everything in try block.
      if schedule.returnSearchType() == 'all':
        daysToSearch = (schedule.getReturnDate()-schedule.getSearchDate()).days
        progressIncrement = float(elements.searchBarLength/daysToSearch)
        while schedule.getSearchDate() < schedule.getReturnDate():
          result = schedule.searchAndPrint()
          addSearchProgress(progressIncrement)
          listUpdate(result)
          if checkStop(): break
      elif schedule.returnSearchType() == 'interval':
        root.after(500, datesInput)
        daysToSearch = (schedule.getReturnDate()-schedule.getSearchDate()).days
        progressIncrement = float(elements.searchBarLength/daysToSearch)
        while schedule.getSearchDate() <= schedule.getReturnDate():
          result = schedule.searchAndPrint()
          addSearchProgress(progressIncrement)
          listUpdate(result)
          if checkStop(): break
      else:
        root.after(500, datesInput)
        for i in range(0,2):
          result = schedule.searchAndPrint(i)
          addSearchProgress(elements.searchBarLength/2)
          listUpdate(result)
          if checkStop: break

      # Reverts to original GUI
      stopTheSearch.set()
      searchButton.configure(text="Search", command=beginSearch, fg='black')
      pb2.destroy()

    # Starting our search thread so we can still use GUI
    searchThread = Thread(target=getResults)
    searchThread.daemon = True
    stopTheSearch = ev()
    stopTheSearch.clear()
    searchThread.start()
    root.update()
    gc.collect()
  
  ## Window Setup
  root = Tk()
  searchType_ = StringVar()
  searchType_.set('all')
  direct_ = BooleanVar()
  direct_.set(False)
  titleFrame = Frame(root)
  comboBoxFrame = Frame(root)
  picturesFrame = Frame(root)
  buttonsFrame = Frame(root, bg="lightgray")
  resultsFrame = Frame(root)
  root.title('Southwest Flight Schedules')
  gridConfigure(root, [0], [0])

  ## Title/Label
  titleFrame.grid(row=0,column=0,sticky='EW')
  gridConfigure(titleFrame, [0,1], [0])
  Label(titleFrame, text="Southwest Nonstop Flight Schedules", font=('', 24, 'bold')).grid(row=0, column=0)
  Label(titleFrame, text=f"Flights can be seen up until {schedule.returnLastBookableDate().strftime('%B %d, %Y')}.").grid(row=1,column=0, pady=2)
  
  ## Comboboxes for Airports, Search Button
  comboBoxFrame.grid(row=2,column=0,sticky='ew')
  gridConfigure(comboBoxFrame, [0], [0,1,2])
  IATA_origin = ttk.Combobox(comboBoxFrame, values=list(elements.getAirports().keys()))
  IATA_origin.grid(row=0, column=0, padx=4)
  IATA_origin.current(0)
  IATA_origin.bind("<<ComboboxSelected>>", callbackOrigin)
  elements.setOrigin(IATA_origin.get())

  IATA_destination = ttk.Combobox(comboBoxFrame, values=list(elements.getAirports().keys()))
  IATA_destination.grid(row=0, column=2, padx=4)
  IATA_destination.current(0)
  IATA_destination.bind("<<ComboboxSelected>>", callbackDestination)
  elements.setDestination(IATA_destination.get())

  searchButton = Button(comboBoxFrame, text="Search", command=lambda: root.after(200, beginSearch))
  searchButton.grid(row=0, column=1, padx=4)
  
  ## Photos of Cities
  loadImage(IATA_origin.get(), 1)
  loadImage(IATA_destination.get(), 2)
  picturesFrame.grid(row=1, column=0, sticky='nsew')
  gridConfigure(picturesFrame, [0], [0,1])
  pic_origin = Label(picturesFrame, image=elements.getCityPhoto(1), width=250, height=150)
  pic_origin.grid(row=0, column=0, padx=4, pady=16)

  pic_destination = Label(picturesFrame, image=elements.getCityPhoto(2), width=250, height=150)
  pic_destination.grid(row=0, column=1, padx=4, pady=16)

  ## Search Options
  root.grid_rowconfigure(3, minsize=30)
  buttonsFrame.grid(row=4, column=0)
  gridConfigure(buttonsFrame, [0,1], [0,1,2,3,4])
  buttonsFrame.grid_columnconfigure(3, minsize=100)
  Label(buttonsFrame, text="Search Options", font=('', 16, 'bold'), bg='lightgray').grid(row=0, column=0, columnspan=3)
  Label(buttonsFrame, text="Flight Type", font=('', 16, 'bold'), bg='lightgray').grid(row=0, column=4, columnspan=1)

  for displayName, val in elements.searchTypes:
    Radiobutton(buttonsFrame, text=displayName, padx=10, variable=searchType_, command=callSearchFunc, value=val, bg='lightgray').grid(row=1, column=[y[0] for y in elements.searchTypes].index(displayName), padx=4)
  Checkbutton(buttonsFrame, text="Include direct flights?", padx=10, variable=direct_, command=callDirectFunc, bg='lightgray').grid(row=1, column=4, padx=4)

  ## Search Results
  root.grid_rowconfigure(5, minsize=10)
  resultsFrame.grid(row=6, column=0, sticky='ew')
  gridConfigure(resultsFrame, [0,1], [0,1,2])
  resultsFrame.grid_columnconfigure(1, minsize=4)
  leftResultsTitle = Label(resultsFrame, text=f"Flights to {elements.getDestination()}", font=('', 12, 'bold'))
  leftResultsTitle.grid(row=0,column=0, columnspan=1)
  rightResultsTitle = Label(resultsFrame, text=f"Flights to {elements.getOrigin()}", font=('', 12, 'bold'))
  rightResultsTitle.grid(row=0,column=2, columnspan=1)

  leftResults = scrolledtext.ScrolledText(resultsFrame, width=elements.width, height=elements.height)
  leftResults.grid(row=1,column=0,pady=4)
  rightResults = scrolledtext.ScrolledText(resultsFrame, width=elements.width, height=elements.height)
  rightResults.grid(row=1,column=2,pady=4)

  ## Widget Management
  titleFrame.tkraise()

  def onExit():
    root.destroy()
    sys.exit()

  root.protocol('WM_WINDOW_DELETE', onExit)
  root.lift()
  root.mainloop()

if __name__ == "__main__":
  try:
    main()
  except ConnectionResetError:
    exit()