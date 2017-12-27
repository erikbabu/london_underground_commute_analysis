"""
This program analyses the difference in number of commuters for different
tube stations on the london underground network.
"""

import csv

from datetime import datetime

from collections import OrderedDict

from matplotlib import pyplot as plt

from operator import itemgetter

def list_underground_stations(data):
  """Returns a list of all underground stations in dataset."""
  stations = []
  for row in data:
    station_name = row[1].rstrip()
    stations.append(station_name)
  return stations[:-1]

def prompt_station_list_display(stations):
  """Asks if user would like to see list of stations. Displays if so."""
  see_list = raw_input("Would you like to see a list of stations? (y/n): ")
  if see_list.lower() == 'y':
    print("This is a list of all stations:")
    for station in stations:
      print("-" + station)
  print("")

def ask_user_for_stations(stations):
  """Returns a list of stations the user wants to analyse."""
  print("Option 1 -")
  print("Please enter the stations you would like to analyse.")
  print("You are allowed to pick at most 5 stations.")
  print("Type done when complete.")
  print("Note that entering 0 station names will default to option 2.\n")
  print("Option 2 -")
  print("Enter 'busiest 5' to see an analysis of the 5 busiest stations.\n")
  station_list = []
  #only allow 5 stations to be compared
  while len(station_list) < 5:
    station = raw_input("Station name: ")
    if station.lower().strip() == 'busiest 5':
      return None
    if station.lower().strip() == 'done':
      break
    if check_station_valid(station, stations):
      if station.title() not in station_list:
        station_list.append(station.title())
      else:
        print("Sorry, you have already entered that station.")
    else:
      print("Sorry, that station does not exist. Please try again.")
  return station_list

def busiest_five(data):
  """
  Returns a list of the 5 busiest stations
  """
  stations = list_underground_stations(data)
  station_dicts_unsorted = []
  counter = 0;

  for row in data:
    if counter < len(stations):
      station_name = stations[counter]
      counter += 1
      daily_total = int(row[101])
      station_to_total = {'Station name': station_name, 'Total Commuters':
                          daily_total}
      station_dicts_unsorted.append(station_to_total)

  #sort list by number of commuters in descending order
  station_dicts_sorted = sorted(station_dicts_unsorted,
                                key=itemgetter('Total Commuters'),
                                reverse=True)
  #get the top 5
  top_5 = station_dicts_sorted[:5]

  #return the list of stations
  return [item['Station name'] for item in top_5]

def check_station_valid(station, stations):
  """Returns whether station is in list of underground stations."""
  return station.title() in stations

def time_data_for_stations(data, stations, full_station_list):
  """
  Gets the commuter information per time slice for stations.
  """
  times = []
  #to preserve order get indices of all stations in list
  time_data_indices = []
  for station in stations:
    data_index = full_station_list.index(station)
    time_data_indices.append(data_index)

  for time_index in time_data_indices:
    row = data[time_index]
    station_time_info = []
    for time in range(4, 100):
      station_time_info.append(row[time])
    #convert from string to int and add to result list
    station_time_info = [int(time) for time in station_time_info]
    times.append(station_time_info)
  return times

def formatted_user_stations(station_list):
  """Builds title string showing all stations used for analyis."""
  if len(station_list) == 1:
    station_str = 'Commutes shown for '
  else:
    station_str = 'Difference in commutes between '
  while station_list:
    station = station_list.pop()
    if len(station_list) > 1:
      station_str += station + ", "
    elif len(station_list) == 1:
      station_str += station + " and "
    else:
      station_str += station
  return station_str

def plot_data(times, user_station_list, user_times_list):
  """Plots data on the graph."""
  fig = plt.figure(dpi=128, figsize=(10,6))

  #map the string to integer for plotting purposes
  times_mappings = list(range(len(times)))

  #rotate label 90 degrees to better fit graph
  plt.xticks(times_mappings, times, rotation=90)

  colours = ["red", "blue", "orange", "green", "black"]

  for i in range(0, len(user_station_list)):
    plt.plot(times_mappings, user_times_list[i], c=colours[i], alpha=0.5,
             label=user_station_list[i])

  #highlight difference between stations if only 2 being compared
  if len(user_station_list) == 2:
    plt.fill_between(times_mappings, user_times_list[0],
                     user_times_list[1], facecolor='purple', alpha=0.1)
  #display legend
  plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

def format_plot(title, date):
  """Formats the data plots on the graph."""
  plt.title(title, fontsize=24)
  plt.xlabel('Time slices', fontsize=16)
  plt.ylabel("Number of commuters/time slice", fontsize=16)
  plt.tick_params(axis='both', which='major', labelsize=12)


filename = raw_input("Please enter relative path of filename: ")
try:
  #format file to assist parsing in next step i.e. remove unecessary lines
  with open (filename, "r+") as f:
    lines = f.readlines()
    f.seek(0)
    line_num = 1
    should_truncate = True

    for line in lines:
      if line_num == 1 and "(C)" in line:
        #file already been formatted
        should_truncate = False
        break
      else:
        if not (line[0] == ',' and line[1] == ',') and 'COUNTS -' not in line:
          lines_that_need_stripping = [3, 5]
          if line_num in lines_that_need_stripping:
            #remove trailing commas
            comma_stripped_line = line.translate(None, ",")
            f.write(comma_stripped_line)
          else:
            f.write(line)
        line_num += 1

    if should_truncate:
      f.truncate()

  #parse formatted file
  with open(filename) as f:
    reader = csv.reader(f)
    #find header by skipping unrelated lines in dataset
    for i in range(3):
      header_row = next(reader)

    #convert reader into list to allow it to be passed into functions
    reader = [row for row in reader]

    #get list of all stations
    stations = list_underground_stations(reader)

    #ask user if they would like to see list of stations
    prompt_station_list_display(stations)

    #get list of stations that user wants to compare
    user_station_list = ask_user_for_stations(stations)

    #get times header
    times = [time.strip()[:4] for time in header_row[4:100]]
    date = '16 November 2017'

    if user_station_list:
      title = 'Difference in commutes between '
      title = formatted_user_stations(user_station_list[:])
    else:
      user_station_list = busiest_five(reader)
      title = 'Difference in commutes between 5 busiest stations '

    title += ' on ' + date
    #get time data for user selected stations
    user_times_list = time_data_for_stations(reader, user_station_list,
                                            stations)
    #display graph
    plot_data(times, user_station_list, user_times_list)
    format_plot(title, date)
    plt.show()

except IOError:
  print("Sorry, the file " + filename + " does not exist")
  quit()
