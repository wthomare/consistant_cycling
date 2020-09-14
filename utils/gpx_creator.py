# -*- coding: utf-8 -*-

import gpxpy
import gpxpy.gpx
import pandas as pd

import xml.etree.ElementTree as mod_etree 
from sqlalchemy import create_engine


class GPX_creator(object):
    """
    Take a ride in a ride table and create a gpx file 
    """
    def __init__(self):
        self.gpx = gpxpy.gpx.GPX()
        self.gpx.name = ''
        self.gpx.description = ''
        
        self.namespace = '{opencpn}'
    
    
    def set_header(self):
        self.root = mod_etree.Element(self.namespace + 'scale_min_max')
        #mod_etree.SubElement(root, namespace + 'UseScale')
        self.root.attrib['UseScale'] = "true"
        self.root.attrib['ScaleMin'] = "50000"
        self.root.attrib['ScaleMax'] = "0"
        self.rootElement2 = mod_etree.Element(self.namespace + 'arrival_radius')
        self.rootElement2.text = '0.050'
        
        #add extension to header
        nsmap = {self.namespace[1:-1]:'http://www.opencpn.org'}
        self.gpx.nsmap =nsmap
    
    def set_trackpoints(self, lat, long):
        
        for i in range(len(lat)):
        
            gpx_wps = gpxpy.gpx.GPXWaypoint()
            gpx_wps.latitude = lat[0]
            gpx_wps.longitude = long[1]
            gpx_wps.symbol = "Marks-Mooring-Float"
            gpx_wps.name = ""
            gpx_wps.description = ""
            #add the extension to the waypoint
            gpx_wps.extensions.append(self.root)
            self.gpx.waypoints.append(gpx_wps)
            
            
    def to_gpx(self):
        return self.gpx.to_xml()
    
if __name__== '__main__' :
    
    
    engine = create_engine('mysql+pymysql://root:root@localhost:3306/rides', echo=False)
    cnx = engine.raw_connection()
    cursor = cnx.cursor()
    
    query = 'SELECT altitude, longitude, latitude, distance FROM ride_ride_1 WHERE clef=1599378516'
    
    df = pd.read_sql(query, con=engine).dropna(axis=0)

    gpx_handler = GPX_creator()
    gpx_handler.set_header()
    
    gpx_handler.set_trackpoints(lat= df['latitude'].to_list(), long = df['longitude'].to_list())
    gpx_file = gpx_handler.to_gpx()