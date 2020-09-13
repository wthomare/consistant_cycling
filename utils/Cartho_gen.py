# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from sqlalchemy import create_engine


import os
import pandas as pd
import plotly.express as px

class Cartho_gen(object):
    
    # ------------------------------------------------------------------------
    def __init__(self, user_id, user_name):
        self.user_id = "ride_"+user_id
        self.user_name = user_name
        self.graph_folder = os.path.join('static', self.user_name, 'graphic')

        self.engine = create_engine('mysql+pymysql://root:root@localhost:3306/rides', echo=False)
        self.cnx = self.engine.raw_connection()
        self.cursor = self.cnx.cursor()

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
    def create_html(self, clef):
        
        query = 'SELECT longitude, latitude, distance FROM ride_%s WHERE clef=%s'%(self.user_id, clef)
        df_ride = pd.read_sql(query, con=self.engine)
        
        clean_lat = df_ride["latitude"].dropna()
        clean_long = df_ride["longitude"].dropna()
    
        fig = px.line_mapbox(df_ride, lat="latitude", lon="longitude", hover_name ='distance', center ={'lat':clean_lat.iloc[1], 'lon':clean_long.iloc[1]}, zoom=3, height=400, width =400)
        
        fig.update_layout(mapbox_style="open-street-map", mapbox_zoom=4, mapbox_center_lat = 41,
            margin={"r":0,"t":0,"l":0,"b":0})
        
        fig.write_html(os.path.join(self.graph_folder, "%s_%s.html"%(self.user_id, clef)), include_plotlyjs='cdn')
                 
            
    # ------------------------------------------------------------------------
    def check_user(self):
        """
        Check if all rides have equivalent graphic otherwise create it

        """
        existing_ride = self.load_id()
        graph_list = os.listdir(self.graph_folder)
        
        for clef in existing_ride['clef'].values:
            if not "%s_%s.html"%(self.user_id, clef) in graph_list:
                self.create_html(clef)
        
    # ------------------------------------------------------------------------
    def body_extract(self, html_file):
        with open(os.path.join(self.graph_folder, html_file), 'rb') as file:
            tree = BeautifulSoup(file, 'lxml')
            body = tree.body
        return body
    
    # ------------------------------------------------------------------------
    def list_gpx(self):
        """
        Return the body of each graphic for a user into a list

        """
        self.check_user()
        graph_list = os.listdir(self.graph_folder)
        
        list_body = [(int(html_file.split('_')[-1].split('.')[0]), self.body_extract(html_file)) for html_file in graph_list]
        return list_body

    # ------------------------------------------------------------------------
    def list_details(self):
        """
        Return the details of each ride for a user into a dictionary
        """
        query = """SELECT COUNT(*) FROM information_schema.tables WHERE table_name='ride_%s'"""%self.user_id
        self.cursor.execute(query)
        if self.cursor.fetchone()[0] == 1:
        
            query = "SELECT DISTINCT * FROM details_%s"%self.user_id
            df_details = pd.read_sql(query, con=self.engine)
            df_details['duree'].iloc[0] = pd.to_timedelta(df_details['duree'].iloc[0], unit='ns')
            
            details = {}
            for row, column in df_details.iterrows():
                k = int(column['clef'])
                v = column.drop(['clef'])
                v = v.to_frame().fillna('  ').T.to_html().replace('dataframe', 'table is-bordered').replace('table border="1"', 'table border="1"')
                details[k] = v
        else:
            details={}
        return details
