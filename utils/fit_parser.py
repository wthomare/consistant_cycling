# -*- coding: utf-8 -*-

import fitdecode
import pandas as pd


# ----------------------------------------------------------------------------
class Fit_parser(object):
    
    # ------------------------------------------------------------------------
    def __init__(self):
        
        self.dictio_trck = {'timestamp':[],
                            'position_lat':[],
                            'position_long':[],
                            'distance':[],
                            'heart_rate':[],
                            'altitude':[],
                            'speed':[],
                            'power':[],
                            'cadence':[]
            }
        self.trck_point = []

    # ------------------------------------------------------------------------
    def parse(self, file):
        
        with fitdecode.FitReader(file) as fit:
            for frame in fit:
                if isinstance(frame, fitdecode.FitDataMessage):
                    self.trck_point.append(frame)
                                        
    # ------------------------------------------------------------------------
    def check_point(self, point):
        
        field_name = (field.name for field in point)
        
        if set(self.dictio_trck.keys()).issubset(field_name):
            return True
        else:
            return False
        
    # ------------------------------------------------------------------------
    def fit_to_df(self):
        for point in self.trck_point[3:-2]:
            if self.check_point(point):
                for field in point:
                    if field.name in ['speed', 'distance'] and isinstance(field.value, float):
                        self.dictio_trck[field.name].append(field.value)
                    elif field.name in self.dictio_trck and field.name not in  ["speed", 'distance']:
                        self.dictio_trck[field.name].append(field.value)
                        
        df = pd.DataFrame(self.dictio_trck)
        df['position_lat'] = df['position_lat'].div(100000000)
        df['position_long'] = df['position_long'].div(100000000)
        df['distance'] = df['distance'].div(1000)
        df['speed'] = df['speed'].div(3.6)
        
        return df
    
    
    # ------------------------------------------------------------------------
    def format_details_fit(self):
        
        penul_dict = {}
        penul_point = self.trck_point[-2]
        for field in penul_point:
            penul_dict[field.name] = field.value
            
        df = pd.DataFrame({
            'activity':penul_dict['sport'],
            'calories':penul_dict['total_calories'],
            'duree': penul_dict['total_elapsed_time'] * 1000*1000*1000,
            'max_speed' : penul_dict['max_speed'],
            'avg_sped' : penul_dict['avg_speed'],
            'distance' : penul_dict['total_distance'],
            'avg_bpm' : penul_dict['avg_heart_rate'],
            'max_bpm' : penul_dict['max_heart_rate'],
            'avg_power' : penul_dict['avg_power'],
            'max_power' : penul_dict['max_power'],
            'ascension' : penul_dict['total_ascent'],
            'avg_cadence' : penul_dict["avg_cadence"],
            'max_cadence' : penul_dict['max_cadence']
            }, index = [0])
        return df
    
if __name__== '__main__' :
    file = 'files/Sous_Force.fit'
    
    parser = Fit_parser()
    parser.parse(file)
    
    df = parser.fit_to_df()
    df_d = parser.format_details_fit()