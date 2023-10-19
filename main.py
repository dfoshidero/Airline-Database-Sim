import sqlite3
import os
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as tkMessageBox
import connection

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
      (strftime('%s', A.SCH_ARR_DATETIME) - strftime('%s', D.SCH_DEPR_DATETIME)) / 60 AS Scheduled_Flt_Duration,
      (strftime('%s', A.ACT_ARR_DATETIME) - strftime('%s', D.ACT_DEPR_DATETIME)) / 60 AS Actual_Flt_Duration,
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

  cursor.execute(f"""SELECT C.CREW_ID, C.CREW_NAME, E.SIZE, C.CREW_DETAILS
  FROM DB_CABINCREWS C
  LEFT JOIN (
	SELECT EMP_CREW_ID, COUNT(EMP_ID) AS SIZE
	FROM DB_EMPLOYEE
	GROUP BY EMP_CREW_ID) E ON C.CREW_ID = E.EMP_CREW_ID""")

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

  title_label = tk.Label(window,
                         text=(str(tablename) + " Dashboard"),
                         font=("Arial", 12))
  title_label.pack(fill="x", pady=10)

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

  def select_record():
    pass

  select_button = tk.Button(window,
                            text="Select Record",
                            command=select_record)

  def update_record():
    pass

  update_button = tk.Button(window, text="Save Record", command=update_record)

  select_button.pack(side=tk.RIGHT, padx=10)
  update_button.pack(side=tk.RIGHT, padx=10)

  back_button = tk.Button(window,
                          text="Open Dataset Manager",
                          fg="black",
                          command=masterPage)
  back_button.pack(side=tk.LEFT, padx=10)
  closeDatabase()


def masterPage():
  for widget in window.winfo_children():
    widget.destroy()

  # Create a frame to hold the buttons
  button_frame = tk.Frame(window, bg="grey32")
  button_frame.pack(pady=20, expand="yes")  # Add padding at the top

  # Create the "VIEW ALL" button
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
  departure_button = tk.Button(button_frame,
                               text="Departures",
                               command=lambda: returnTable("Departures"))
  arrival_button = tk.Button(button_frame,
                             text="Arrivals",
                             command=lambda: returnTable("Arrivals"))
  crew_button = tk.Button(button_frame,
                          text="Crew Data",
                          command=lambda: returnTable("Crew"))

  departure_button.pack(pady=5)
  arrival_button.pack(pady=5)

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
