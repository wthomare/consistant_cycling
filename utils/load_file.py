# -*- coding: utf-8 -*-

from utils.parser_to_df import ride_parser
from sqlalchemy import create_engine

import os
import pandas as pd


class Load_ride(object):
    def __init__(self, file, user_id):
        self.file = file
        self.user_id = "ride_"+user_id
        
        self.engine = create_engine('mysql+pymysql://root:root@localhost:3306/rides', echo=False)
        self.cnx = self.engine.raw_connection()
        self.cursor = self.cnx.cursor()
        
        # TODO Remove after dev
        self.cursor.execute('DROP TABLE IF EXISTS ride_%s' %self.user_id)
        
    def check_ride_db(self):
        
        query = """SELECT COUNT(*) FROM information_schema.tables WHERE table_name='ride_%s'"""%self.user_id
        self.cursor.execute(query)
        
        if not self.cursor.fetchone()[0] == 1:
            print('Create ride table for user %s' %self.user_id)
            query = "CREATE TABLE ride_%s (id INT AUTO_INCREMENT PRIMARY KEY, clef INT, timestamp TIMESTAMP, latitude FLOAT, longitude FLOAT, distance FLOAT, heart_rate INT, cadence INT, altitude FLOAT, power FLOAT, speed FLOAT)"%self.user_id
            self.cursor.execute(query)
            
    def load_id(self):
        query = "SELECT DISTINCT clef FROM ride_%s"%self.user_id
        df_ride_id = pd.read_sql(query, con=self.engine)
        return df_ride_id
    
    def load_df(self):
        
        self.df.to_sql(con=self.engine, name='ride_%s'%self.user_id, if_exists='append', index=False, chunksize=10000)
        
    def delete_file(self):
        os.remove(self.file)
        
    def execute(self):
        """
        Process as usual
        """
        
        # Parse the file
        self.parser = ride_parser(self.file)
        self.ride_id = self.parser.ride_id
        self.df = self.parser.result
        
        # Check if the ride table for the user exist. Otherwise create it
        self.check_ride_db()
        
        # Load all ride id to avoid double insert
        self.saved_id = self.load_id()
        
        if self.ride_id in self.saved_id.values:
            print('The ride with the ID [%s] is already loaded for the user : [%s]' %(self.ride_id, self.user_id))
            return False
        else:
            self.load_df()
        
        self.delete_file()
        return True