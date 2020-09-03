import ggps
import fitparse
import os
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

fit_file = "files//Sous_Force.fit"
tcx_file = "files//Afternoon_Ride.tcx"

# ----------------------------------------------------------------------------
class ride_parser(object):

    # ------------------------------------------------------------------------
    def __init__(self, ride_path):
        self.units = None
        
        if os.path.exists(ride_path):
            self.filename, self.file_extension = os.path.splitext(ride_path)
            self.path = ride_path
        else:
            raise FileExistsError("No file at : [%s]" %ride_path)
        
        if self.file_extension == '.fit':
            self.fit_to_df()
        elif self.file_extension == '.tcx':
            self.tcx_to_df()
        else:
            raise TypeError("The extension [%s] is not supported" %self.file_extension)
        
    # ------------------------------------------------------------------------
    def fit_to_df(self):
        self.parser = (self.file_extension, fitparse.FitFile(self.path))
        df_records = []
        for record in self.parser[1].get_messages('record'):
            _record = record.as_dict()['fields']
            df_records.append(pd.Series({'%s'%x['name'] : x['value'] for x in _record}).to_frame().transpose())
        
        # self.units = pd.Series({'%s'%x['name'] : (x['units'] if 'units' in x.keys() else None ) for x in _record}).to_frame().transpose()
        
        self.result = self.format_fit(pd.concat(df_records))
        self.ride_id = int(pd.Timestamp(self.result['timestamp'].iloc[0]).timestamp())
        self.format_details()
        
    # ------------------------------------------------------------------------
    def tcx_to_df(self):
        handler = ggps.TcxHandler()
        handler.parse(self.path)
        tkpts = handler.trackpoints
        
        df_trackpoint = pd.DataFrame([tkpt.values for tkpt in tkpts])
        self.result = self.format_tcx(df_trackpoint)
        self.ride_id = int(pd.Timestamp(handler.first_time).timestamp())
        self.format_details()

    # ------------------------------------------------------------------------
    def format_details(self):        
        elasped_time = (self.result['timestamp'].iloc[-1] - self.result['timestamp'].iloc[0]).seconds
        delta_alt = self.result['altitude'].diff().clip(lower=0).sum()
        distance = self.result['distance'].iloc[-1]
        
        self.details = pd.DataFrame({'delta':[elasped_time], 'altitude':[delta_alt], 'distance':[distance]})
    
    # ------------------------------------------------------------------------
    def format_fit(self, df_input):
        df_output = pd.DataFrame({})
        df_output['timestamp'] = df_input['timestamp']
        
        for Tuple in [('latitude', 'position_lat'), ('longitude', 'position_long'),
                      ('distance', 'distance'), ('heart_rate', 'heart_rate'),
                      ('cadence', 'cadence'), ('altitude', 'altitude'),
                      ('power', 'power'), ('speed', 'speed')]:
            if Tuple[1] in df_input.keys():
                df_output[Tuple[0]] = df_input[Tuple[1]].astype(float)
            else:
                 df_output[Tuple[0]] = [None for x in range(len(df_output['timestamp']))]
                 
        return df_output

    # ------------------------------------------------------------------------
    def format_tcx(self, df_input):
        df_output = pd.DataFrame({})
        df_output['timestamp'] = pd.to_datetime(df_input['time'])        
        
        for Tuple in [('latitude', 'latitudedegrees'), ('longitude', 'longitudedegrees'),
                      ('distance', 'distancekilometers'), ('heart_rate', 'heartratebpm'),
                      ('cadence', 'cadencerpm'), ('altitude', 'altitudemeters'),
                      ('power', 'power')]:
        
            if Tuple[1] in df_input.keys():
                df_output[Tuple[0]] = df_input[Tuple[1]].astype(float)
            else:
                 df_output[Tuple[0]] = [None for x in range(len(df_output['timestamp']))]

        df_output['speed'] = df_output['distance'].diff().shift(-1).multiply(3.6*1000)
        return df_output
        

        
if __name__ == '__main__':

    #parser = ride_parser(fit_file)
    parser = ride_parser(tcx_file)
    
    df = parser.result
    
    clean_lat = df["latitude"].dropna()
    clean_long = df["longitude"].dropna()

    fig = px.line_mapbox(df, lat="latitude", lon="longitude", hover_name ='distance', center ={'lat':clean_lat.iloc[0], 'lon':clean_long.iloc[0]}, zoom=3, height=400, width =400)
    
    fig.update_layout(mapbox_style="open-street-map", mapbox_zoom=4, mapbox_center_lat = 41,
        margin={"r":0,"t":0,"l":0,"b":0})
    
    fig.write_html("file.html", include_plotlyjs='cdn')