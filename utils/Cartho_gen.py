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
        self.graph_2d = os.path.join('static', self.user_name, 'graphic_2d')

        self.engine = create_engine('mysql+pymysql://root:root@localhost:3306/rides', echo=False)
        self.cnx = self.engine.raw_connection()
        self.cursor = self.cnx.cursor()
        
        self.original_data = None

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
    def extract_ride(self, clef):
        query = 'SELECT altitude, longitude, latitude, distance FROM ride_%s WHERE clef=%s'%(self.user_id, clef)
        self.original_data = pd.read_sql(query, con=self.engine)       
    
    # ------------------------------------------------------------------------
    def create_html(self, clef):
        if self.original_data is None:
            self.extract_ride(clef)
        
        clean_lat = self.original_data["latitude"].dropna()
        clean_long = self.original_data["longitude"].dropna()
    
        fig = px.line_mapbox(self.original_data, lat="latitude", lon="longitude", hover_name ='distance', center ={'lat':clean_lat.iloc[1], 'lon':clean_long.iloc[1]}, zoom=3, height=400, width =400)
        
        fig.update_layout(mapbox_style="open-street-map", mapbox_zoom=4,
            margin={"r":0,"t":0,"l":0,"b":0})
        
        fig.write_html(os.path.join(self.graph_folder, "%s_%s.html"%(self.user_id, clef)), include_plotlyjs='cdn')
        
    # ------------------------------------------------------------------------
    def create_elevation_html(self, clef):
        if self.original_data is None:
            self.extract_ride(clef)
        
        fig = px.area(self.original_data, x="distance", y="altitude", height=200, width =1200, labels={'distance':'km', 'altitude':'m'}, color_discrete_sequence=['grey'])
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        fig.write_html(os.path.join(self.graph_2d, "%s_%s.html"%(self.user_id, clef)), include_plotlyjs='cdn')
        
            
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
                self.create_elevation_html(clef)
        
    # ------------------------------------------------------------------------
    def body_extract(self, path, html_file):
        with open(os.path.join(os.path.join(path, html_file)), 'rb') as file:
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
        graph_2d_list = os.listdir(self.graph_2d)

        list_body = [(int(graph_list[i].split('_')[-1].split('.')[0]), self.body_extract(self.graph_folder, graph_list[i]), self.body_extract(self.graph_2d, graph_2d_list[i])) for i in range(len(graph_list))]
        
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
