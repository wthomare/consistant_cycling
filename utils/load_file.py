# -*- coding: utf-8 -*-

from utils.parser_to_df import ride_parser
from sqlalchemy import create_engine

import os
import pandas as pd

from utils.weather_handler import Weather_handler


class Load_ride(object):

    # ------------------------------------------------------------------------
    def __init__(self, file, user_id):
        self.file = file
        self.user_id = "ride_"+user_id
        
        self.engine = create_engine('mysql+pymysql://root:root@localhost:3306/rides', echo=False)
        self.cnx = self.engine.raw_connection()
        self.cursor = self.cnx.cursor()

        self.engine_meteo = create_engine('mysql+pymysql://root:root@localhost:3306/meteo', echo=False)
        self.cnx_meteo = self.engine_meteo.raw_connection()
        self.cursor_meteo = self.cnx_meteo.cursor()        

        self.meteo = Weather_handler()
        
    # ------------------------------------------------------------------------
    def check_db(self):
        
        query = """SELECT COUNT(*) FROM information_schema.tables WHERE table_name='ride_%s'"""%self.user_id
        self.cursor.execute(query)
        
        if not self.cursor.fetchone()[0] == 1:
            query = "CREATE TABLE ride_%s (id INT AUTO_INCREMENT PRIMARY KEY, clef INT, timestamp TIMESTAMP, latitude FLOAT, longitude FLOAT, distance FLOAT, heart_rate INT, cadence INT, altitude FLOAT, power FLOAT, speed FLOAT)"%self.user_id
            self.cursor.execute(query)

        query = """SELECT COUNT(*) FROM information_schema.tables WHERE table_name='details_%s'"""%self.user_id
        self.cursor.execute(query)
        
        if not self.cursor.fetchone()[0] == 1:
            query = "CREATE TABLE details_%s (id INT AUTO_INCREMENT PRIMARY KEY, clef INT, activity VARCHAR(255), calories INT, duree FLOAT, max_speed FLOAT, distance FLOAT, avg_bpm INT, max_bpm INT, intensity VARCHAR(255), Method VARCHAR(255))"%self.user_id
            self.cursor.execute(query)

        query = """SELECT COUNT(*) FROM information_schema.tables WHERE table_name='meteo_%s'"""%self.user_id
        self.cursor_meteo.execute(query)
        
        if not self.cursor_meteo.fetchone()[0] == 1:
            query = """CREATE TABLE meteo_%s (id INT AUTO_INCREMENT PRIMARY KEY, Name VARCHAR(255),clef INT, Date_time TIMESTAMP,
            Temperature FLOAT, Precipitation FLOAT, Snow Depth FLOAT, Wind Speed FLOAT, Cloud Cover FLOAT,
            Relative Humidity  FLOAT, Conditions VARCHAR(255))"""%self.user_id
            self.cursor_meteo.execute(query)
            
    # ------------------------------------------------------------------------
    def load_id(self):
        
        query = """SELECT COUNT(*) FROM information_schema.tables WHERE table_name='ride_%s'"""%self.user_id
        self.cursor.execute(query)

        if self.cursor.fetchone()[0] == 1:
            query = "SELECT DISTINCT clef FROM ride_%s"%self.user_id
            df_ride_id = pd.read_sql(query, con=self.engine)
        else:
            df_ride_id = pd.DataFrame({'clef':[]})
        
        return df_ride_id
    
    # ------------------------------------------------------------------------
    def load_df(self):
        
        self.df.to_sql(con=self.engine, name='ride_%s'%self.user_id, if_exists='append', index=False, chunksize=10000)
        
    # ------------------------------------------------------------------------
    def load_details(self):
        self.df_details.to_sql(con=self.engine, name='details_%s'%self.user_id, if_exists='append', index=False, chunksize=10000)

    # ------------------------------------------------------------------------
    def load_meteo(self, data):
        data['clef'] = self.parser.ride_id
        data.to_sql(con=self.engine_meteo, name='meteo_%s'%self.user_id, if_exists='append', index=False, chunksize=10000)
        
    # ------------------------------------------------------------------------
    def delete_file(self):
        os.remove(self.file)
        
    # ------------------------------------------------------------------------
    def execute(self):
        """
        Process as usual
        """
        
        # Parse the file
        self.parser = ride_parser(self.file)
        self.ride_id = self.parser.ride_id
        self.df = self.parser.result
        self.df_details = self.parser.details
        
        meteo_data = self.meteo.execute(self.df)
        self.load_meteo(meteo_data)
        
        ID = pd.Series([self.ride_id for i in range(len(self.df['timestamp']))], index=[i for i in range(len(self.df['timestamp']))])
        self.df['clef'] = ID
        
        ID = [self.ride_id]
        self.df_details['clef'] = ID
        
        # Check if the tables for the user exist. Otherwise create it
        self.check_db()
        
        # Load all ride id to avoid double insert
        self.saved_id = self.load_id()
        
        if self.ride_id in self.saved_id.values:
            print('The ride with the ID [%s] is already loaded for the user : [%s]' %(self.ride_id, self.user_id))
            return False
        else:
            self.load_df()
            self.load_details()
        
        self.delete_file()
        return True