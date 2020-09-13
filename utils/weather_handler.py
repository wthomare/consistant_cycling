# -*- coding: utf-8 -*-

import codecs
import datetime
import urllib.request

import pandas as pd
from io import StringIO


# ----------------------------------------------------------------------------
class Weather_handler(object):
    """
    Return data from openweatherdata API
    """
    
    # ------------------------------------------------------------------------
    def __init__(self):
        
        self.startDateString = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/weatherdata/history?aggregateHours=1&combinationMethod=aggregate&startDateTime='
        self.UTC = 'T00%3A00%3A00'
        self.endDateString = '&endDateTime='
        self.startTimeString = '&dayStartTime='
        self.endTimeString = '%3A0%3A0&dayEndTime='
        self.keyString = '%3A0%3A0&collectStationContributions=false&maxStations=-1&maxDistance=-1&includeNormals=false&contentType=csv&unitGroup=metric&locationMode=single&key='
        self.locationString = '&dataElements=default&locations='
        self.inter_lat_lon = '%2C%20'
        
        self.key = None

    # ------------------------------------------------------------------------
    def get_key(self):
        
        if not self.key:
            with open('utils/files/openweatherdata_key.txt', 'r') as key_file:
                self.key = key_file.read()
            
    # ------------------------------------------------------------------------
    def set_request(self, startDate, endDate, startHour, endHour, lat, lon):
        
        self.get_key()
        self.URL = self.startDateString + str(startDate) + self.UTC \
                    + self.endDateString + str(endDate) + self.UTC \
                    + self.startTimeString + str(startHour) + self.endTimeString \
                    + str(endHour) + self.keyString + self.key + self.locationString \
                    + str(lat) + self.inter_lat_lon + str(lon)
    
    # ------------------------------------------------------------------------
    def get_data(self):
        CSVBytes = urllib.request.urlopen(self.URL)

        self.df = pd.read_csv(StringIO(CSVBytes.read().decode('utf8')))        
    
    # ------------------------------------------------------------------------
    def format_data(self):
        self.df = self.df[['Name', 'Date time', 'Temperature', 'Precipitation', 'Snow Depth', 'Wind Speed', 'Cloud Cover',
       'Relative Humidity',  'Conditions']]
        
        
        self.df = self.df.rename(columns={'Date time': 'Date_time'})
        
        self.df['Date_time'] = self.df['Date_time'].apply(lambda x : pd.Timestamp(x))
        
    
    # ------------------------------------------------------------------------
    def execute(self, df_input):
        # TODO : Ne pas utilisé la valeur moyenne de long et lat mais trouver celle de chaque heur et faire un requête ainsi
        
        date = df_input['timestamp'].dt.strftime('%Y-%m-%d')
        hour = df_input['timestamp'].dt.strftime('%H')
        
        startDate = date.iloc[0]
        endDate = date.iloc[-1]
        startHour = hour.iloc[0]
        endHour = hour.iloc[-1]
        
        lat = str(df_input['latitude'].mean())
        lon = str(df_input['longitude'].mean())
        
        self.set_request(startDate, endDate, startHour, endHour, lat, lon) 
        self.get_data()
        self.format_data()
        return self.df
        
        
if __name__=='__main__':

    handler = Weather_handler()
    handler.set_request(startDate ='2020-09-10',
                        endDate   = '2020-09-13',
                        startHour = "01",
                        endHour   = "05",
                        lat       = '47.218371',
                        lon       = '-1.553621')
    
    handler.get_data()
    handler.format_data()
    df_test = handler.df
