# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from sqlalchemy import create_engine


import os
import pandas as pd

class cartho_gen(object):
    
    def __init__(self, user_id, user_name):
        self.user_id = "ride_"+user_id
        self.user_name = user_name
        self.graph_folder = os.path.join('static', self.user_name, 'graphic')

        self.engine = create_engine('mysql+pymysql://root:root@localhost:3306/rides', echo=False)
        self.cnx = self.engine.raw_connection()
        self.cursor = self.cnx.cursor()

    def load_id(self):
        query = "SELECT DISTINCT clef FROM ride_%s"%self.user_id
        df_ride_id = pd.read_sql(query, con=self.engine)
        return df_ride_id
    
    def create_html(self, clef):
        
        query = 'SELECT longitute, latitude FROM ride_%s WHERE clef=%s'%(self.user_id, clef)
        df_ride = pd.read_sql(query, con=self.engine)
        
        clean_lat = df_ride["latitude"].dropna()
        clean_long = df_ride["longitude"].dropna()
    
        fig = px.line_mapbox(df, lat="latitude", lon="longitude", hover_name ='distance', center ={'lat':clean_lat.iloc[1], 'lon':clean_long.iloc[1]}, zoom=3, height=400, width =400)
        
        fig.update_layout(mapbox_style="open-street-map", mapbox_zoom=4, mapbox_center_lat = 41,
            margin={"r":0,"t":0,"l":0,"b":0})
        
        fig.write_html(os.path.join(self.graph_folder, "%s_%s.html"%(self.user_id, clef)), include_plotlyjs='cdn')
                 
            
    def check_user(self):
        """
        Check if all rides have equivalent graphic otherwise create it

        """
        existing_ride = self.load_id()
        graph_list = os.listdir(self.graph_folder)
        
        for clef in existing_ride['clef'].values:
            if not "%s_%s.html"%(self.user_id, clef) in graph_list:
                self.create_html(clef)
        
    def body_extract(self, html_file):
        with open(html_file, 'rb') as file:
            tree = BeautifulSoup(file, 'lxml')
            body = tree.body
        return body
    
    def list_body(self):
        """
        Return the body of each graphic for a user into a list

        """
        self.check_user()
        graph_list = os.listdir(self.graph_folder)
        
        list_body = [self.body_extract(html_file) for html_file in graph_list]
        return list_body

