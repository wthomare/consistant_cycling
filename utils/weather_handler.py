# -*- coding: utf-8 -*-
"""
Created on Sat Sep  5 16:13:56 2020

@author: wilfr
"""


import csv
import codecs
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
            with open('files/openweatherdata_key.txt', 'rb') as key_file:
                self.key = key_file.read().decode('utf8')
            
    # ------------------------------------------------------------------------
    def set_request(self, startDate, endDate, startHour, endHour, lat, lon):
        
        self.get_key()
        self.URL = self.startDateString + startDate + self.UTC \
                    + self.endDateString + endDate + self.UTC \
                    + self.startTimeString + startHour + self.endTimeString \
                    + endHour + self.keyString + self.key + self.locationString \
                    + lat + self.inter_lat_lon + lon
    
    # ------------------------------------------------------------------------
    def get_data(self):
        CSVBytes = urllib.request.urlopen(self.URL)
        CSVText = csv.reader(codecs.iterdecode(CSVBytes, 'utf-8'))
        
        df = pd.read_csv(StringIO(CSVBytes.read().decode('utf8')))
        return df

if __name__=='__main__':

    handler = Weather_handler()
    handler.set_request(startDate ='2020-09-03',
                        endDate   = '2020-09-05',
                        startHour = "10",
                        endHour   = "16",
                        lat       = '47.218371',
                        lon       = '-1.553621')
    
    df_test = handler.get_data()

