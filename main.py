import sqlite3
import os
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as tkMessageBox
import datetime

from tkintertable import TableCanvas

#define GUI properties.
window = tk.Tk()
window.title("Airline Database Simulator")
window.configure(bg="lightgray")

#get screen width and height.
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

#set window properties.
window.geometry(f"{screen_width}x{screen_height}")
window.configure(bg="grey32")


def connectDatabase():
  global conn, cursor

  conn = sqlite3.connect('AIRLINE_SIM_DATA.db')
  cursor = conn.cursor()


def closeDatabase():
  conn.close()


#Resets the data when the simulator is run.
def resetData():
  if os.path.exists('AIRLINE_SIM_DATA.db'):
    os.remove('AIRLINE_SIM_DATA.db')

  # Connect to a new SQLite database (main.db in this case)
  connectDatabase()

  # Read the SQL script file and execute it
  with open('public/sqlite_script.sql', 'r', encoding='utf-16') as script_file:
    sql_script = script_file.read()
    cursor.executescript(sql_script)

  closeDatabase()


def fetchDepartures():
  connectDatabase()

  cursor.execute(f"""SELECT 
	strftime('%Y-%m-%d %H:%M', D.SCH_DEPR_DATETIME) AS Scheduled_Departure_DateTime,
	AA.AIRPORT_NAME AS Destination,
	AC.AIRCRAFT_NAME AS Aircraft,
	F.FLIGHT_ID AS Flight_No,
	A.ARR_TERMINAL AS Terminal
  FROM DB_FLIGHTS AS F
  LEFT JOIN DB_DEPARTURES D ON F.DEPARTURE_ID = D.DEPARTURE_ID
  LEFT JOIN DB_ARRIVALS A ON F.ARRIVAL_ID = A.ARRIVAL_ID
  LEFT JOIN DB_AIRPORTS AA ON A.ARR_AIRPORT_ID = AA.AIRPORT_ID
  LEFT JOIN DB_AIRCRAFT AC ON F.AIRCRAFT_ID = AC.AIRCRAFT_ID""")

  data = cursor.fetchall()
  column_names = [description[0] for description in cursor.description]
  closeDatabase()
  return (data, column_names)


def fetchArrivals():
  connectDatabase()

  cursor.execute(f"""SELECT 
	strftime('%Y-%m-%d %H:%M', A.SCH_ARR_DATETIME) AS Scheduled_Arrival_DateTime,
	AA.AIRPORT_NAME AS Origin,
	AC.AIRCRAFT_NAME AS Aircraft,
	F.FLIGHT_ID AS Flight_No,
	A.ARR_TERMINAL AS Terminal
  FROM DB_FLIGHTS AS F
  LEFT JOIN DB_DEPARTURES D ON F.DEPARTURE_ID = D.DEPARTURE_ID
  LEFT JOIN DB_ARRIVALS A ON F.ARRIVAL_ID = A.ARRIVAL_ID
  LEFT JOIN DB_AIRPORTS AA ON D.DEP_AIRPORT_ID = AA.AIRPORT_ID
  LEFT JOIN DB_AIRCRAFT AC ON F.AIRCRAFT_ID = AC.AIRCRAFT_ID""")

  data = cursor.fetchall()
  column_names = [description[0] for description in cursor.description]
  closeDatabase()

  return (data, column_names)


def fetchFlightsDashboard():
  connectDatabase()

  cursor.execute(f"""
  SELECT 
      F.FLIGHT_ID AS Flight_No,
      AC.AIRCRAFT_TYPE AS Flight_Type,
      AC.PASSENGER_CAPACITY AS Flight_Capacity,
      strftime('%Y-%m-%d %H:%M', D.SCH_DEPR_DATETIME) AS Departure_DateTime,
      strftime('%Y-%m-%d %H:%M', A.SCH_ARR_DATETIME) AS Arrival_DateTime,
      (strftime('%s', A.SCH_ARR_DATETIME) - strftime('%s', D.SCH_DEPR_DATETIME)) / 60 AS Sched_Flight_Minutes,
      DD.AIRPORT_NAME AS Departure_Airport,
      DD.AIRPORT_COUNTRY || ', ' || DD.AIRPORT_CITY AS Departure_Location,
      D.DEP_TERMINAL AS Departure_Terminal,
      DA.AIRPORT_NAME AS Arrival_Airport,
      DA.AIRPORT_COUNTRY || ', ' || DA.AIRPORT_CITY AS Arrival_Location,
      A.ARR_TERMINAL AS Arrival_Terminal
  FROM DB_FLIGHTS AS F
  JOIN DB_DEPARTURES AS D ON F.DEPARTURE_ID = D.DEPARTURE_ID
  JOIN DB_ARRIVALS AS A ON F.ARRIVAL_ID = A.ARRIVAL_ID
  JOIN DB_AIRPORTS AS DD ON D.DEP_AIRPORT_ID = DD.AIRPORT_ID
  JOIN DB_AIRPORTS AS DA ON A.ARR_AIRPORT_ID = DA.AIRPORT_ID
  JOIN DB_AIRCRAFT AS AC ON F.AIRCRAFT_ID = AC.AIRCRAFT_ID
  """)

  data = cursor.fetchall()
  column_names = [description[0] for description in cursor.description]
  closeDatabase()

  return (data, column_names)


def fetchEmployee():
  connectDatabase()

  cursor.execute(f"""SELECT * FROM DB_EMPLOYEE""")

  data = cursor.fetchall()
  column_names = [description[0] for description in cursor.description]
  closeDatabase()

  return (data, column_names)


def fetchPilots():
  connectDatabase()

  cursor.execute(f"""SELECT * FROM DB_PILOTS""")

  data = cursor.fetchall()
  column_names = [description[0] for description in cursor.description]
  closeDatabase()

  return (data, column_names)


def fetchAirports():
  connectDatabase()

  cursor.execute(f"""SELECT * FROM DB_AIRPORTS""")

  data = cursor.fetchall()
  column_names = [description[0] for description in cursor.description]
  closeDatabase()

  return (data, column_names)


def fetchAircrafts():
  connectDatabase()

  cursor.execute(f"""SELECT * FROM DB_AIRCRAFT""")

  data = cursor.fetchall()
  column_names = [description[0] for description in cursor.description]
  closeDatabase()

  return (data, column_names)


def fetchCrew():
  connectDatabase()

  cursor.execute(f"""SELECT
    C.CREW_ID,
    C.CREW_NAME,
    (SELECT COUNT(*) FROM DB_EMPLOYEE E WHERE E.EMP_CREW_ID = C.CREW_ID) AS SIZE,
    C.CREW_DETAILS
FROM
    DB_CABINCREWS C;""")

  data = cursor.fetchall()
  column_names = [description[0] for description in cursor.description]
  closeDatabase()

  return (data, column_names)


def fetchSchedule():
  connectDatabase()

  cursor.execute(f"""SELECT 
    F.FLIGHT_ID AS Flight_No, 
    P.PILOT_ID AS Pilot_No, 
    P.PASSPORT_NO AS Pilot_Passport_No, 
    DA.AIRPORT_CITY || '  -  ' || AA.AIRPORT_CITY AS Flight_Description, 
    P.LICENSE_TYPE AS Flight_Type, 
    A.AIRCRAFT_NAME AS Aircraft, 
    strftime('%Y-%m-%d %H:%M:%S', SD.SCH_DEPR_DATETIME) AS Departure_DateTime
FROM 
    DB_PILOTS P
    LEFT JOIN BRIDGE_ASSIGNEDPILOTS AP ON P.PILOT_ID = AP.PILOT_ID
    LEFT JOIN DB_FLIGHTS F ON AP.FLIGHT_ID = F.FLIGHT_ID
    LEFT JOIN DB_AIRCRAFT A ON F.AIRCRAFT_ID = A.AIRCRAFT_ID
    LEFT JOIN DB_DEPARTURES SD ON F.DEPARTURE_ID = SD.DEPARTURE_ID
    LEFT JOIN DB_ARRIVALS SA ON F.ARRIVAL_ID = SA.ARRIVAL_ID
    LEFT JOIN DB_AIRPORTS DA ON SD.DEP_AIRPORT_ID = DA.AIRPORT_ID
    LEFT JOIN DB_AIRPORTS AA ON SA.ARR_AIRPORT_ID = AA.AIRPORT_ID
ORDER BY SD.SCH_DEPR_DATETIME;
  """)

  data = cursor.fetchall()
  column_names = [description[0] for description in cursor.description]
  closeDatabase()

  return (data, column_names)


# def editData():
#   def saveChanges():

#   def cancelEdit():


def returnTable(tablename):
  connectDatabase()

  if tablename == "Departures":
    tableData, columns = fetchDepartures()
  elif tablename == "Arrivals":
    tableData, columns = fetchArrivals()
  elif tablename == "General Overview":
    tableData, columns = fetchFlightsDashboard()
  elif tablename == "Employee":
    tableData, columns = fetchEmployee()
  elif tablename == "Crew":
    tableData, columns = fetchCrew()
  elif tablename == "Pilot":
    tableData, columns = fetchPilots()
  elif tablename == "Pilot Schedule":
    tableData, columns = fetchSchedule()
  elif tablename == "Airport":
    tableData, columns = fetchAirports()
  elif tablename == "Aircraft":
    tableData, columns = fetchAircrafts()

  for widget in window.winfo_children():
    widget.destroy()

  dpar_button_frame = tk.Frame(window)

  departure_button = tk.Button(dpar_button_frame,
                               text="Departures",
                               command=lambda: returnTable("Departures"))
  arrival_button = tk.Button(dpar_button_frame,
                             text="Arrivals",
                             command=lambda: returnTable("Arrivals"))

  view_all_button = tk.Button(dpar_button_frame,
                              bg="grey64",
                              fg="white",
                              text="RETURN TO GENERAL OVERVIEW",
                              command=lambda: returnTable("General Overview"))

  title_label = tk.Label(window,
                         text=(str(tablename) + " Dashboard"),
                         font=("Arial", 12))
  title_label.pack(fill="x", pady=(10, 0))
  dpar_button_frame.pack(fill="x", pady=(0, 10))

  if tablename == "Departures":
    arrival_button.pack(side=tk.LEFT, padx=(10, 20), pady=5)
    view_all_button.pack(side=tk.LEFT, padx=(10, 20), pady=5)

  elif tablename == "Arrivals":
    departure_button.pack(side=tk.LEFT, padx=(20, 10), pady=5)
    view_all_button.pack(side=tk.LEFT, padx=(10, 20), pady=5)

  elif tablename == "General Overview":
    departure_button.pack(side=tk.LEFT, padx=(20, 10), pady=5)
    arrival_button.pack(side=tk.LEFT, padx=(10, 20), pady=5)

  table_frame = tk.Frame(window)
  table_frame.pack(fill="both", expand=True)

  container = tk.Frame(table_frame)
  container.pack(fill="both", expand=True)

  table_tree = ttk.Treeview(container, columns=columns, show="headings")

  for col in columns:
    table_tree.heading(col, text=col)
    table_tree.column(col, minwidth=50, stretch=0, anchor="c")

  for row in tableData:
    table_tree.insert("", "end", values=row)

  horizontal_scrollbar = ttk.Scrollbar(container,
                                       orient="horizontal",
                                       command=table_tree.xview)
  table_tree.configure(xscrollcommand=horizontal_scrollbar.set)

  horizontal_scrollbar.pack(side="bottom", fill="x")
  table_tree.pack(fill="both", expand=True)

  def updateRecord():
    pass

  def selectRecord():
    pass

  def getCrewChoices():

    connectDatabase()

    cursor.execute("SELECT CREW_ID FROM DB_CABINCREWS")
    choices = [row[0] for row in cursor.fetchall()]

    closeDatabase()
    return choices

  def getAircraftChoices():

    connectDatabase()

    cursor.execute("SELECT AIRCRAFT_ID FROM DB_AIRCRAFT")
    choices = [row[0] for row in cursor.fetchall()]

    closeDatabase()
    return choices

  def getAirportChoices():

    connectDatabase()

    cursor.execute("SELECT AIRPORT_ID FROM DB_AIRPORTS")
    choices = [row[0] for row in cursor.fetchall()]

    closeDatabase()
    return choices

  def getEmployeeChoices():

    connectDatabase()

    cursor.execute("SELECT EMP_ID FROM DB_EMPLOYEE")
    choices = [row[0] for row in cursor.fetchall()]

    closeDatabase()
    return choices

  def addRecord():
    for widget in window.winfo_children():
      widget.destroy()

    def insertRecord(data):
      connectDatabase()

      if tablename == "General Overview" or tablename == "Departures" or tablename == "Arrivals":
        departure_datetime = datetime.datetime.strptime(
          data["Departure DateTime"], '%Y-%m-%d %H:%M')
        arrival_datetime = datetime.datetime.strptime(data["Arrival DateTime"],
                                                      '%Y-%m-%d %H:%M')

        flight_duration = arrival_datetime - departure_datetime
        flight_duration_minutes = flight_duration.total_seconds() / 60

        cursor.execute(
          f"""INSERT INTO DB_DEPARTURES (DEP_AIRPORT_ID, DEP_TERMINAL, SCH_DEPR_DATETIME) 
                           VALUES (?, ?, ?)""",
          (data["Departure Airport"], data["Departure Terminal"],
           data["Departure DateTime"]))

        departure_id = cursor.lastrowid

        cursor.execute(
          f"""INSERT INTO DB_ARRIVALS (ARR_AIRPORT_ID, ARR_TERMINAL, SCH_ARR_DATETIME) 
         VALUES (?, ?, ?)""",
          (data["Arrival Airport"], data["Arrival Terminal"],
           data["Arrival DateTime"]))

        arrival_id = cursor.lastrowid

        cursor.execute(
          f"""INSERT INTO DB_FLIGHTS (DEPARTURE_ID, ARRIVAL_ID, AIRCRAFT_ID, CREW_ID, FLIGHT_DURATION) 
         VALUES (?, ?, ?, ?, ?)""",
          (departure_id, arrival_id, data["Aircraft"], data["Crew"],
           flight_duration_minutes))

      conn.commit()
      closeDatabase()

      for entry in entry_boxes.values():
        entry.delete(0, 'end')

      tkMessageBox.showinfo("Success", "Record added successfully!")

    #ADD FRAME
    add_label = tk.Label(window, text=("Add Flights"), font=("Arial", 12))
    add_label.pack(fill="x", pady=(30, 0))

    add_frame = tk.Frame(window)
    add_frame.pack(pady=(10), anchor=tk.CENTER)

    #ENTRY BOXES
    if tablename == "General Overview" or tablename == "Departures" or tablename == "Arrivals":

      fields = [
        "Aircraft", "Departure Airport", "Departure Terminal",
        "Departure DateTime", "Arrival Airport", "Arrival Terminal",
        "Arrival DateTime", "Crew"
      ]
      entry_boxes = {}

      for i, field in enumerate(fields):
        label = tk.Label(add_frame, text=field)
        label.grid(row=i, column=0)

        if field == "Departure DateTime" or field == "Arrival DateTime":
          entry = ttk.Combobox(add_frame)
          entry.insert(0, "YYYY-MM-DD HH:MM")

        elif field == "Crew":
          choices = getCrewChoices()
          entry = ttk.Combobox(add_frame, values=choices)

        elif field == "Aircraft":
          choices = getAircraftChoices()
          entry = ttk.Combobox(add_frame, values=choices)

        elif field == "Departure Airport" or field == "Arrival Airport":
          choices = getAirportChoices()
          entry = ttk.Combobox(add_frame, values=choices)

        else:
          entry = tk.Entry(add_frame)

        entry.grid(row=i, column=1, pady=5)
        entry_boxes[field] = entry

    elif tablename == "Employee":
      fields = [
        "Last Name", "First Name", "Role", "Crew", "Gender", "Annual Salary",
        "Contact Details"
      ]
      entry_boxes = {}

      for i, field in enumerate(fields):
        label = tk.Label(add_frame, text=field)
        label.grid(row=i, column=0)

        if field == "Crew ID":
          choices = getCrewChoices()
          entry = ttk.Combobox(add_frame, values=choices)

        elif field == "Gender":
          choices = ["Male", "Female", "Other"]
          entry = ttk.Combobox(add_frame, values=choices)

        else:
          entry = tk.Entry(add_frame)

        entry.grid(row=i, column=1, pady=5)
        entry_boxes[field] = entry

    elif tablename == "Crew":
      fields = ["Crew Name", "Crew Details"]
      entry_boxes = {}

      for i, field in enumerate(fields):
        label = tk.Label(add_frame, text=field)
        label.grid(row=i, column=0)

        entry = tk.Entry(add_frame)

        entry.grid(row=i, column=1, pady=5)
        entry_boxes[field] = entry

    elif tablename == "Airport":
      fields = ["Airport Name", "Airport Country", "Airport City"]
      entry_boxes = {}

      for i, field in enumerate(fields):
        label = tk.Label(add_frame, text=field)
        label.grid(row=i, column=0)

        entry = tk.Entry(add_frame)

        entry.grid(row=i, column=1, pady=5)
        entry_boxes[field] = entry

    elif tablename == "Aircraft":
      fields = ["Aircraft Name", "Aircraft Type", "Passenger Capacity"]
      entry_boxes = {}

      for i, field in enumerate(fields):
        label = tk.Label(add_frame, text=field)
        label.grid(row=i, column=0)

        if field == "Aircraft Type":
          choices = ["Commercial", "Private"]
          entry = ttk.Combobox(add_frame, values=choices)

        else:
          entry = tk.Entry(add_frame)

        entry.grid(row=i, column=1, pady=5)
        entry_boxes[field] = entry

    elif tablename == "Pilot":
      fields = [
        "Employee ID", "License Type", "Passport Number", "Country of Origin"
      ]
      entry_boxes = {}

      for i, field in enumerate(fields):
        label = tk.Label(add_frame, text=field)
        label.grid(row=i, column=0)

        if field == "Employee ID":
          choices = getEmployeeChoices()
          entry = ttk.Combobox(add_frame, values=choices)

        elif field == "License Type":
          choices = ["Commercial", "Private"]
          entry = ttk.Combobox(add_frame, values=choices)

        else:
          entry = tk.Entry(add_frame)

        entry.grid(row=i, column=1, pady=5)
        entry_boxes[field] = entry

      #ADD DATA BUTTON
    def get_entry_data():
      data = {}
      for col, entry in entry_boxes.items():
        data[col] = entry.get()
      insertRecord(data)

    retrieve_button = tk.Button(add_frame,
                                text="Confirm Data",
                                command=get_entry_data)
    retrieve_button.grid(row=len(columns), columnspan=2, pady=10)

    view_all_button = tk.Button(window,
                                bg="grey32",
                                fg="white",
                                text="RETURN TO PAGE",
                                command=lambda: returnTable(tablename))

    view_all_button.pack(padx=10, pady=(0, 5))

  select_button = tk.Button(window, text="Select Record", command=selectRecord)

  update_button = tk.Button(window, text="Save Record", command=updateRecord)

  add_button = tk.Button(window, text="Add Record", command=addRecord)
  assign_pilots_button = tk.Button(window,
                                   text="Assign Pilots",
                                   command=addRecord)

  back_button = tk.Button(window,
                          text="Open Dataset Manager",
                          fg="black",
                          command=masterPage)

  back_button.pack(side=tk.LEFT, padx=10)
  add_button.pack(side=tk.LEFT, padx=10)
  select_button.pack(side=tk.RIGHT, padx=10)
  update_button.pack(side=tk.RIGHT, padx=10)

  closeDatabase()


def masterPage():
  for widget in window.winfo_children():
    widget.destroy()

  button_frame = tk.Frame(window, bg="grey32")
  button_frame.pack(pady=20, expand="yes")

  view_all_button = tk.Button(button_frame,
                              bg="grey64",
                              fg="white",
                              text="RETURN TO GENERAL OVERVIEW",
                              command=lambda: returnTable("General Overview"))

  view_all_button.pack(padx=10, pady=15)

  airport_button = tk.Button(button_frame,
                             text="Airport Data",
                             command=lambda: returnTable("Airport"))
  aircraft_button = tk.Button(button_frame,
                              text="Aircraft Data",
                              command=lambda: returnTable("Aircraft"))
  employee_button = tk.Button(button_frame,
                              text="Employee Data",
                              command=lambda: returnTable("Employee"))
  pilot_button = tk.Button(button_frame,
                           text="Pilot Data",
                           command=lambda: returnTable("Pilot"))
  pilot_schedule_button = tk.Button(
    button_frame,
    text="Pilot Flight Rota",
    command=lambda: returnTable("Pilot Schedule"))
  crew_button = tk.Button(button_frame,
                          text="Crew Data",
                          command=lambda: returnTable("Crew"))

  employee_button.pack(pady=5)
  crew_button.pack(pady=5)
  pilot_button.pack(pady=5)
  pilot_schedule_button.pack(pady=5)

  airport_button.pack(pady=5)
  aircraft_button.pack(pady=5)


def startPage():
  centerframe = tk.Frame(window, bg="grey32")
  centerframe.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

  title = tk.Label(centerframe,
                   text="Airline Database Simulator",
                   bg="grey32",
                   fg="white",
                   font=("Arial", 24))
  title.pack()

  button = tk.Button(centerframe,
                     text="START",
                     bg="grey64",
                     fg="white",
                     font=("Arial", 16),
                     command=lambda: returnTable("General Overview"))
  button.pack()


startPage()

resetData()

tk.mainloop()
