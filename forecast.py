'''
Created on Apr 5, 2017

Steps:

1. read in csv file
2. convert postal code to geocode
3. expand the date range, generate a sub-dataframe for each row and combine all sub-dataframes into a large one
4. convert the large dataframe into pivot table
5. generate daily weather info in csv format and excel report of precipitation

@author: Ruobin Wu
'''
import requests
import pandas as pd
import googlemaps
import csv
import os
import sys
import json
import datetime

# a record is a row in location file
class Record(object):
    def __init__(self, record):
        self.locId = record[0]
        self.postalCode = record[1]
        self.startDate = record[2] 
        self.endDate = record[3]
        self.lat = None
        self.lng = None

# step 1: read in the csv file
def readCSV(fileName):
    f = open(fileName, 'r')
    reader = csv.reader(f)
    records = []
    # skip the header of csv file
    next(reader)
    for row in reader:
        record = Record(row)
        # step 2 : convert postal code to geocode
        record.lat, record.lng = getGeocode(record.postalCode)        
        records.append(record)
    f.close()
    return(records)

# step 2: convert postal code to geocode using Google Maps API
# the API Key is in local environment variable
def getGeocode(postalCode):
    google_maps = googlemaps.Client(key=os.environ['GOOGLE_MAPS_API_KEY'])
    location = google_maps.geocode(postalCode)
    if not location:
        return(None, None)
    geolocation = location[0]['geometry']['location']
    return(geolocation['lat'], geolocation['lng'])

def subDataFrame(record):
    dfArray = []
    for time in range(int(record.startDate), int(record.endDate) + 1, 60 * 60 * 24):
        apiKey = os.environ['FORECAST_IO_API_KEY']
        URL = "https://api.darksky.net/forecast/"
        URL += apiKey + "/" + str(record.lat) + "," + str(record.lng) + "," + str(time) + "?"
        URL += "exclude=currently,minutely,hourly,alerts,flags"
        try:
            r = requests.get(URL)
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
            sys.exit(1)
        rJSON = r.text
        weather = json.loads(rJSON)
        daily = weather['daily']['data'][0]

        # add days and locations to daily weather information
        daily['days'] = datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d')
        daily['locations'] = record.locId

        for key in daily:
            daily[key] = [daily[key]]

        df = pd.DataFrame(daily)
        dfArray.append(df)

    subDataFrame = pd.concat(dfArray)
    return(subDataFrame)

# step 5: write into an excel file
def writeToExcel(table):
    writer = pd.ExcelWriter('precipitation.xlsx', engine='xlsxwriter')
    table.to_excel(writer, 'Sheet1', na_rep='NaN')
    # add percentage sign to numbers
    workbook  = writer.book
    worksheet = writer.sheets['Sheet1']
    fmt = workbook.add_format({'num_format': '0%'})
    index = 1
    while (index <= len(table.columns)):
        worksheet.set_column(index, index, None, fmt)
        index += 1
    writer.save()

if __name__ == "__main__":
    # Step 1 & 2: read csv file and get geocode
    records = readCSV('locations.csv')
    # keep the original order of records
    originalLocations = [r.locId for r in records]
    # Step 3: merge each sub data frame to a large data frame
    dataFrame = []
    for record in records:
        dataFrame.append(subDataFrame(record))
    df = pd.concat(dataFrame)
    # Step 4: convert data frame into pivot table
    table = pd.pivot_table(df, 
                        values = 'precipProbability', 
                        index = ['locations'],
                        columns = ['days'])
    # reset the index back to the original order
    table = table.reindex(originalLocations)
    # Step 5: write daily weather info into csv file and precipitation info into Excel file
    df.to_csv('daily_weather_info.csv', na_rep = 'NaN', index = False)
    writeToExcel(table)