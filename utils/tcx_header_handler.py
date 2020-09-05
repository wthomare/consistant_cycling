# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import re

import pandas as pd

class tcx_header_handler(object):
    
    def parse(self, file):
        
        with open(file) as xml_file:
            xml_str = xml_file.read()
            xml_str = re.sub(' xmlns="[^"]+"', '', xml_str, count=1)
            
            root = ET.fromstring(xml_str)
            
            self.activity = root.findall('.//Activity')[0].attrib['Sport']
            self.calories = float(root.findall('.//Calories')[0].text)
            self.elasped_time = pd.Timedelta(float(root.findall('.//TotalTimeSeconds')[0].text), unit = 'sec')
            self.MaxVelocity = float(root.findall('.//MaximumSpeed')[0].text)
            self.distance = float(root.findall('.//DistanceMeters')[0].text)
            self.AvgHR = float(root.findall('.//AverageHeartRateBpm')[0][0].text)
            self.MaxHR = float(root.findall('.//MaximumHeartRateBpm')[0][0].text)
            self.intensity = root.findall('.//Intensity')[0].text
            self.TrigMethod = root.findall('.//TriggerMethod')[0].text
            
            
    def get_frame(self):
        
        df = pd.DataFrame({'activity' : [self.activity],
                           'calories' : [int(self.calories)],
                           'duree' : [self.elasped_time],
                           'max_speed' : [round(self.MaxVelocity, 1)],
                           'distance' : [round(self.distance/1000,1)],
                           'avg_bpm' : [int(self.AvgHR)],
                           'max_bpm' : [int(self.MaxHR)],
                           'intensity' : [self.intensity],
                           'Method' : [self.TrigMethod]})
        
        return df
    
    
    
if __name__=='__main__':
    
    file = 'files/Afternoon_Ride.tcx'
    
    handler = tcx_header_handler()
    parse = handler.parse(file)
    
    df = handler.get_frame()