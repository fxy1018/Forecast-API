
# Forecast.io Project

## Author:

Ruobin Wu (ruobinwu@yahoo.com)

## Completion Date:

Apr 8, 2017 (Eastern Daylight Time)

## Steps:

1. read in csv file
2. convert postal code to geocode
3. expand the date range, generate a sub-dataframe for each row and combine all sub-dataframes into a large one 
4. convert the large dataframe into pivot table
5. generate daily weather info in csv format and excel report of precipitation

## Code:

### Imported packages


```python
import requests
import pandas as pd
import googlemaps
import csv
import os
import sys
import json
import datetime
```

### Record class
create a record class, the objects of the class are rows in locations.csv file


```python
class Record(object):
    def __init__(self, record):
        self.locId = record[0]
        self.postalCode = record[1]
        self.startDate = record[2] 
        self.endDate = record[3]
        self.lat = None
        self.lng = None
```

### Function of reading csv file
create a function to read in the csv file using package csv; convert postal code to geocode using Google Maps API;


```python
def readCSV(fileName):
    f = open(fileName, 'r')
    reader = csv.reader(f)
    records = []
    # skip the header of csv file
    next(reader)
    for row in reader:
        record = Record(row)
        # convert postal code to geocode
        record.lat, record.lng = getGeocode(record.postalCode)        
        records.append(record)
    f.close()
    return(records)

# the API Key is in local environment variable
def getGeocode(postalCode):
    google_maps = googlemaps.Client(key=os.environ['GOOGLE_MAPS_API_KEY'])
    location = google_maps.geocode(postalCode)
    if not location:
        return(None, None)
    geolocation = location[0]['geometry']['location']
    return(geolocation['lat'], geolocation['lng'])
```

### Function of creating a sub-dataframe

create a sub-dataframe for weather info of a specific location and its day period


```python
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
```

### Function to write data into Excel file
generate a excel report using data on a pivot table


```python
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
```

### Main function


```python
if __name__ == "__main__":
    # Step 1 & 2: read csv file and get geocode
    records = readCSV('locations.csv')
    # keep the original order of records
    originalLocations = [r.locId for r in records]
    # Step 3: merge each sub-dataframe to a large dataframe
    dataFrame = []
    for record in records:
        dataFrame.append(subDataFrame(record))
    df = pd.concat(dataFrame)
```

#### print a sample of first 10 rows of the dataframe


```python
df[0:10]
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>apparentTemperatureMax</th>
      <th>apparentTemperatureMaxTime</th>
      <th>apparentTemperatureMin</th>
      <th>apparentTemperatureMinTime</th>
      <th>cloudCover</th>
      <th>days</th>
      <th>dewPoint</th>
      <th>humidity</th>
      <th>icon</th>
      <th>locations</th>
      <th>...</th>
      <th>sunriseTime</th>
      <th>sunsetTime</th>
      <th>temperatureMax</th>
      <th>temperatureMaxTime</th>
      <th>temperatureMin</th>
      <th>temperatureMinTime</th>
      <th>time</th>
      <th>visibility</th>
      <th>windBearing</th>
      <th>windSpeed</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>50.46</td>
      <td>1485961200</td>
      <td>42.53</td>
      <td>1485907200</td>
      <td>0.95</td>
      <td>2017-01-31</td>
      <td>48.09</td>
      <td>0.96</td>
      <td>fog</td>
      <td>9be000ae23275d57e1273d211a54ffd7</td>
      <td>...</td>
      <td>1485934901</td>
      <td>1485967844</td>
      <td>50.46</td>
      <td>1485961200</td>
      <td>46.65</td>
      <td>1485907200</td>
      <td>1485907200</td>
      <td>4.39</td>
      <td>173</td>
      <td>8.52</td>
    </tr>
    <tr>
      <th>0</th>
      <td>51.10</td>
      <td>1486047600</td>
      <td>42.80</td>
      <td>1486018800</td>
      <td>0.80</td>
      <td>2017-02-01</td>
      <td>47.03</td>
      <td>0.90</td>
      <td>partly-cloudy-day</td>
      <td>9be000ae23275d57e1273d211a54ffd7</td>
      <td>...</td>
      <td>1486021207</td>
      <td>1486054355</td>
      <td>51.10</td>
      <td>1486047600</td>
      <td>48.01</td>
      <td>1486018800</td>
      <td>1485993600</td>
      <td>6.73</td>
      <td>173</td>
      <td>14.22</td>
    </tr>
    <tr>
      <th>0</th>
      <td>44.42</td>
      <td>1486126800</td>
      <td>31.72</td>
      <td>1486159200</td>
      <td>0.65</td>
      <td>2017-02-02</td>
      <td>41.89</td>
      <td>0.86</td>
      <td>partly-cloudy-day</td>
      <td>9be000ae23275d57e1273d211a54ffd7</td>
      <td>...</td>
      <td>1486107511</td>
      <td>1486140865</td>
      <td>49.72</td>
      <td>1486126800</td>
      <td>39.57</td>
      <td>1486162800</td>
      <td>1486080000</td>
      <td>7.20</td>
      <td>175</td>
      <td>11.07</td>
    </tr>
    <tr>
      <th>0</th>
      <td>44.77</td>
      <td>1486220400</td>
      <td>32.39</td>
      <td>1486166400</td>
      <td>0.23</td>
      <td>2017-02-03</td>
      <td>36.80</td>
      <td>0.89</td>
      <td>partly-cloudy-day</td>
      <td>9be000ae23275d57e1273d211a54ffd7</td>
      <td>...</td>
      <td>1486193814</td>
      <td>1486227376</td>
      <td>47.23</td>
      <td>1486220400</td>
      <td>35.52</td>
      <td>1486188000</td>
      <td>1486166400</td>
      <td>7.47</td>
      <td>188</td>
      <td>3.30</td>
    </tr>
    <tr>
      <th>0</th>
      <td>34.89</td>
      <td>1486306800</td>
      <td>32.69</td>
      <td>1486278000</td>
      <td>0.49</td>
      <td>2017-02-04</td>
      <td>37.55</td>
      <td>0.95</td>
      <td>partly-cloudy-day</td>
      <td>9be000ae23275d57e1273d211a54ffd7</td>
      <td>...</td>
      <td>1486280114</td>
      <td>1486313888</td>
      <td>40.84</td>
      <td>1486306800</td>
      <td>37.03</td>
      <td>1486278000</td>
      <td>1486252800</td>
      <td>5.31</td>
      <td>25</td>
      <td>3.99</td>
    </tr>
    <tr>
      <th>0</th>
      <td>39.93</td>
      <td>1486389600</td>
      <td>31.39</td>
      <td>1486350000</td>
      <td>0.31</td>
      <td>2017-02-05</td>
      <td>35.86</td>
      <td>0.90</td>
      <td>partly-cloudy-night</td>
      <td>9be000ae23275d57e1273d211a54ffd7</td>
      <td>...</td>
      <td>1486366413</td>
      <td>1486400399</td>
      <td>44.36</td>
      <td>1486389600</td>
      <td>32.72</td>
      <td>1486364400</td>
      <td>1486339200</td>
      <td>4.85</td>
      <td>163</td>
      <td>3.81</td>
    </tr>
    <tr>
      <th>0</th>
      <td>45.70</td>
      <td>1486476000</td>
      <td>32.85</td>
      <td>1486425600</td>
      <td>0.52</td>
      <td>2017-02-06</td>
      <td>39.52</td>
      <td>0.89</td>
      <td>fog</td>
      <td>9be000ae23275d57e1273d211a54ffd7</td>
      <td>...</td>
      <td>1486452710</td>
      <td>1486486911</td>
      <td>48.87</td>
      <td>1486476000</td>
      <td>38.09</td>
      <td>1486504800</td>
      <td>1486425600</td>
      <td>5.12</td>
      <td>213</td>
      <td>0.72</td>
    </tr>
    <tr>
      <th>0</th>
      <td>36.71</td>
      <td>1486515600</td>
      <td>30.18</td>
      <td>1486594800</td>
      <td>0.89</td>
      <td>2017-02-07</td>
      <td>35.25</td>
      <td>0.90</td>
      <td>partly-cloudy-day</td>
      <td>9be000ae23275d57e1273d211a54ffd7</td>
      <td>...</td>
      <td>1486539005</td>
      <td>1486573422</td>
      <td>39.48</td>
      <td>1486515600</td>
      <td>35.42</td>
      <td>1486594800</td>
      <td>1486512000</td>
      <td>4.70</td>
      <td>22</td>
      <td>5.37</td>
    </tr>
    <tr>
      <th>0</th>
      <td>28.10</td>
      <td>1486648800</td>
      <td>26.16</td>
      <td>1486670400</td>
      <td>1.00</td>
      <td>2017-02-08</td>
      <td>31.23</td>
      <td>0.89</td>
      <td>fog</td>
      <td>9be000ae23275d57e1273d211a54ffd7</td>
      <td>...</td>
      <td>1486625299</td>
      <td>1486659934</td>
      <td>35.11</td>
      <td>1486648800</td>
      <td>33.52</td>
      <td>1486681200</td>
      <td>1486598400</td>
      <td>4.96</td>
      <td>50</td>
      <td>7.82</td>
    </tr>
    <tr>
      <th>0</th>
      <td>27.62</td>
      <td>1486742400</td>
      <td>25.62</td>
      <td>1486764000</td>
      <td>0.89</td>
      <td>2017-02-09</td>
      <td>32.14</td>
      <td>0.94</td>
      <td>fog</td>
      <td>9be000ae23275d57e1273d211a54ffd7</td>
      <td>...</td>
      <td>1486711591</td>
      <td>1486746445</td>
      <td>34.48</td>
      <td>1486742400</td>
      <td>32.72</td>
      <td>1486749600</td>
      <td>1486684800</td>
      <td>2.49</td>
      <td>23</td>
      <td>8.03</td>
    </tr>
  </tbody>
</table>
<p>10 rows × 29 columns</p>
</div>




```python
    # Step 4: convert data frame into pivot table
    table = pd.pivot_table(df, 
                        values = 'precipProbability', 
                        index = ['locations'],
                        columns = ['days'])
    # reset the index back to the original order
    table = table.reindex(originalLocations)
```

#### print a sample of the pivot table


```python
table
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>days</th>
      <th>2017-01-31</th>
      <th>2017-02-01</th>
      <th>2017-02-02</th>
      <th>2017-02-03</th>
      <th>2017-02-04</th>
      <th>2017-02-05</th>
      <th>2017-02-06</th>
      <th>2017-02-07</th>
      <th>2017-02-08</th>
      <th>2017-02-09</th>
      <th>...</th>
      <th>2017-02-19</th>
      <th>2017-02-20</th>
      <th>2017-02-21</th>
      <th>2017-02-22</th>
      <th>2017-02-23</th>
      <th>2017-02-24</th>
      <th>2017-02-25</th>
      <th>2017-02-26</th>
      <th>2017-02-27</th>
      <th>2017-02-28</th>
    </tr>
    <tr>
      <th>locations</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>9be000ae23275d57e1273d211a54ffd7</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>a35e427b4130be7b2a892e286f0ebb91</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.00</td>
      <td>0.67</td>
      <td>0.66</td>
      <td>0.0</td>
      <td>0.52</td>
      <td>0.64</td>
      <td>0.57</td>
      <td>0.74</td>
      <td>0.61</td>
    </tr>
    <tr>
      <th>185674a2eb5c14fbdbb1d05a4109ea55</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>afbddd7f957a1c822293616e95a2d84c</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>81cea1e224ad183b751acce139f4e276</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>5f1ce9b7c8cd32c08d98310540fb6604</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.98</td>
      <td>0.00</td>
      <td>0.97</td>
      <td>0.0</td>
      <td>0.98</td>
      <td>0.97</td>
      <td>0.93</td>
      <td>0.98</td>
      <td>0.98</td>
    </tr>
    <tr>
      <th>5180af03094779de849ca816c9f5b753</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>7f2aa8e72612f9130e06b32a0d2a58d7</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>8b049b660e984912c48da213f2f7c650</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>fe5d591b3509247487a917d4e8a33f65</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>f8a762f49d2abffe630be60295f71ed0</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>58f7d1d3ce8cc4e808bf840b56714b38</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.98</td>
      <td>0.00</td>
      <td>0.97</td>
      <td>0.0</td>
      <td>0.98</td>
      <td>0.97</td>
      <td>0.93</td>
      <td>0.98</td>
      <td>0.98</td>
    </tr>
    <tr>
      <th>84d414ec45c5b436c8470ce314c3b83f</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>51fa5362e943615c7b31d367b461fd2c</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>c60d40fa98e6235ba0d1485c4253bfe6</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>07d09eab6c837d4b0c0b17aba37e1dcf</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>f69e492442cd452124c75e6805d8e37d</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>f5e2c06c5530335d2c994d20ed071bcb</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>16bdd6fe40ed85ce99a456af6d7cff93</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.98</td>
      <td>0.0</td>
      <td>0.98</td>
      <td>0.98</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.98</td>
      <td>0.00</td>
      <td>0.97</td>
      <td>0.0</td>
      <td>0.98</td>
      <td>0.97</td>
      <td>0.93</td>
      <td>0.98</td>
      <td>0.98</td>
    </tr>
    <tr>
      <th>11aeddbd12e79cae8dddb694e200f00d</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
<p>20 rows × 29 columns</p>
</div>




```python
    # Step 5: write daily weather info into csv file and precipitation info into Excel file
    df.to_csv('daily_weather_info.csv', na_rep = 'NaN', index = False)
    writeToExcel(table)
```

## Insight:
1. Four locations that have precipitation data are St Albans, Patchway, Stratford-upon-Avon, and Reading in UK. 
2. The later three show great consistency in precipitation between Feb 19 to 28, 2017.
3. The precipitation of three locations varied dramically during these days.
