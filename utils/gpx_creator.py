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
    # ------------------------------------------------------------------------
    def __init__(self):
        self.gpx = gpxpy.gpx.GPX()
        self.gpx_track = gpxpy.gpx.GPXTrack()
        self.gpx.tracks.append(self.gpx_track)

        self.gpx.name = ''
        self.gpx.description = ''
        
        self.namespace = '{opencpn}'
    
    
    # ------------------------------------------------------------------------
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
    
    # ------------------------------------------------------------------------
    def set_trackpoints(self, df):
        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        self.gpx_track.segments.append(gpx_segment)
        for i in range(len(df)):
            gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(df['latitude'].iloc[i], df['longitude'].iloc[i], df['altitude'].iloc[i]))
            
            
    # ------------------------------------------------------------------------
    def to_gpx(self):
        self.xml_string = self.gpx.to_xml()
    
    # ------------------------------------------------------------------------
    def save_bpx(self, path):
        assert(path[-3:]=='gpx')
        with open(path, 'w') as xml_file:
            xml_file.write(self.xml_string)
    
if __name__== '__main__' :
    
    
    engine = create_engine('mysql+pymysql://root:root@localhost:3306/rides', echo=False)
    cnx = engine.raw_connection()
    cursor = cnx.cursor()
    
    query = 'SELECT altitude, longitude, latitude, distance FROM ride_ride_1 WHERE clef=1599378516'
    
    df = pd.read_sql(query, con=engine).dropna(axis=0)

    gpx_handler = GPX_creator()
    # gpx_handler.set_header()
    
    gpx_handler.set_trackpoints(df)
    gpx_handler.to_gpx()
    gpx_handler.save_bpx('test.gpx')