# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from geopy.geocoders import Nominatim

import pandas as pd



class Meteo_gen(object):
    
    def __init__(self, user_id, clef):
        
        self.user_id = "ride_"+user_id
        self.clef  = clef
        
        
        self.engine = create_engine('mysql+pymysql://root:root@localhost:3306/meteo', echo=False)
        self.cnx = self.engine.raw_connection()
        self.cursor = self.cnx.cursor()
        
        self.geolocator = Nominatim(user_agent="wilfried.thomare@gmail.com")
        

    # ------------------------------------------------------------------------
    def load_id(self):

        query = """SELECT COUNT(*) FROM information_schema.tables WHERE table_name='meteo_%s'"""%self.user_id
        self.cursor.execute(query)
        if self.cursor.fetchone()[0] == 1:
            
            query = "SELECT DISTINCT clef FROM meteo_%s"%self.user_id
            df_ride_id = pd.read_sql(query, con=self.engine)
            df_ride_id['clef'] = pd.to_numeric(df_ride_id['clef'])
        else:
            df_ride_id = pd.DataFrame({'clef':[]})
        return df_ride_id        

        
    # ------------------------------------------------------------------------
    def check_ride(self):
        """
        Check if self.clef is in the meteo table of the user

        """
        
        existing_ride = self.load_id()
        if int(self.clef) in existing_ride['clef'].values:
            return True
        else:
            raise ValueError("Unknow ride id : [%s]" %self.clef)
    

    # ------------------------------------------------------------------------
    def extract_ride(self):
        #  TODO quand changement fait sur cartho_gen pour long et lat appliquer içi aussi
        
        if self.check_ride():
            query = "SELECT * FROM meteo_%s WHERE clef=%s"%(self.user_id, self.clef)
            df_details = pd.read_sql(query, con=self.engine)
            
            place = self.geolocator.reverse(df_details['Name'].iloc[0]).address
            
            df_details['Name'] = df_details['Name'].apply(lambda x : place)
                        
            return df_details.to_dict()