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
	D.SCH_DEPR_DATETIME,
	AA.AIRPORT_NAME,
	AC.AIRCRAFT_NAME,
	F.FLIGHT_ID,
	A.ARR_TERMINAL
  FROM DB_FLIGHTS AS F
  LEFT JOIN DB_DEPARTURES D ON F.DEPARTURE_ID = D.DEPARTURE_ID
  LEFT JOIN DB_ARRIVALS A ON F.ARRIVAL_ID = A.ARRIVAL_ID
  LEFT JOIN DB_AIRPORTS AA ON A.ARR_AIRPORT_ID = AA.AIRPORT_ID
  LEFT JOIN DB_AIRCRAFT AC ON F.AIRCRAFT_ID = AC.AIRCRAFT_ID""")

  data = cursor.fetchall()
  column_names = [description[0] for description in cursor.description]
  closeDatabase()
  for i in data:
    print(i)
  return (data, column_names)


def fetchArrivals():

  connectDatabase()

  cursor.execute(f"""SELECT 
	A.SCH_ARR_DATETIME,
	AA.AIRPORT_NAME,
	AC.AIRCRAFT_NAME,
	F.FLIGHT_ID,
	A.ARR_TERMINAL
  FROM DB_FLIGHTS AS F
  LEFT JOIN DB_DEPARTURES D ON F.DEPARTURE_ID = D.DEPARTURE_ID
  LEFT JOIN DB_ARRIVALS A ON F.ARRIVAL_ID = A.ARRIVAL_ID
  LEFT JOIN DB_AIRPORTS AA ON D.DEP_AIRPORT_ID = AA.AIRPORT_ID
  LEFT JOIN DB_AIRCRAFT AC ON F.AIRCRAFT_ID = AC.AIRCRAFT_ID""")

  data = cursor.fetchall()
  column_names = [description[0] for description in cursor.description]
  closeDatabase()
  for i in data:
    print(i)
  return (data, column_names)


def fetchFlightsDashboard():

  connectDatabase()

  cursor.execute(f"""
  SELECT 
      F.FLIGHT_ID,
      D.SCH_DEPR_DATETIME,
      A.SCH_ARR_DATETIME,
      (strftime('%s', A.SCH_ARR_DATETIME) - strftime('%s', D.SCH_DEPR_DATETIME)) / 60 AS SCH_FLIGHT_DUR,
      (strftime('%s', A.ACT_ARR_DATETIME) - strftime('%s', D.ACT_DEPR_DATETIME)) / 60 AS ACT_FLIGHT_DUR,
      DD.AIRPORT_NAME AS DEP_AIRPORT,
      DD.AIRPORT_COUNTRY || ', ' || DD.AIRPORT_CITY AS DEP_LOCATION,
      D.DEP_TERMINAL,
      DA.AIRPORT_NAME AS ARR_AIRPORT,
      DA.AIRPORT_COUNTRY || ', ' || DA.AIRPORT_CITY AS ARR_LOCATION,
      A.ARR_TERMINAL,
      AC.AIRCRAFT_TYPE,
      AC.PASSENGER_CAPACITY
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


def returnTable(tablename):
  connectDatabase()

  if tablename == "Departures":
    tableData, columns = fetchDepartures()
  elif tablename == "Arrivals":
    tableData, columns = fetchArrivals()
  elif tablename == "DB_FLIGHTS":
    tableData, columns = fetchFlightsDashboard()

  for widget in window.winfo_children():
    widget.destroy()

  table_view_window = tk.Toplevel(window)
  table_view_window.title(f"Viewing {tablename} Table")

  table_frame = tk.Frame(table_view_window)
  table_frame.pack(fill="both", expand=True)

  container = tk.Frame(table_frame)
  container.pack(fill="both", expand=True)

  table_tree = ttk.Treeview(container,
                            columns=columns,
                            show="headings")

  for col in columns:
    table_tree.heading(col, text=col)
    table_tree.column(col, width=100)

  for row in tableData:
    table_tree.insert("", "end", values=row)

  horizontal_scrollbar = ttk.Scrollbar(container,
                                       orient="horizontal",
                                       command=table_tree.xview)
  table_tree.configure(xscrollcommand=horizontal_scrollbar.set)

  horizontal_scrollbar.pack(side="bottom", fill="x")
  table_tree.pack(fill="both", expand=True)


  back_button = tk.Button(window,
                          text="Back to Menu",
                          bg="white",
                          fg="black",
                          font=("Arial", 16),
                          command=menuPage)
  back_button.pack(fill="both")
  closeDatabase()


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
                     bg="grey32",
                     fg="white",
                     font=("Arial", 16),
                     command=menuPage)
  button.pack()


def menuPage():

  for widget in window.winfo_children():
    widget.destroy()

  centerframe = tk.Frame(window, bg="grey32")
  centerframe.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

  window.title("Menu")
  window.configure(background="white")

  button = tk.Button(centerframe,
                     text="Get Flight Data",
                     bg="white",
                     fg="black",
                     font=("Arial", 16),
                     command=lambda: returnTable("DB_FLIGHTS"))
  button.pack()


startPage()

resetData()

tk.mainloop()
