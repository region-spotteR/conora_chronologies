from loguru import logger
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import date, timedelta, datetime

import plotly.graph_objects as go

# a quick fix way to import visuals_plotly module
import os
import sys

currentdir = os.path.dirname(__file__)
#currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

from visuals_plotly import add_update_menus, visuals


class dictItemsToSelf:
    def __init__(self, dictionary):
        for k, v in dictionary.items():
            setattr(self, k, v)             # same as self.k=v

class old_visuals(visuals):
    def __init__(self,country_attributes):
        dictItemsToSelf.__init__(self,country_attributes.color_sizes)
        self.country_name = country_attributes.country_name
    
    def plot_timeline(self,smooth_obj,country,full_html=True):
        try:
            self.headers = smooth_obj.headers
            date_list=[datetime.strptime(x, "%Y-%m-%d").date() for x in smooth_obj.data[0]]
            fig = make_subplots(rows=2, cols=1,
                        specs=[[{"type": "scatter"}], [{"type": "table"}]]
                    )

            for i in range(1,len(smooth_obj.headers)):
                fig.add_trace(go.Scatter(x=date_list, y=smooth_obj.data[i],
                                name=smooth_obj.headers[i]),row=1,col=1)
                # fig.add_trace(go.Scatter(x=date_list, y=smooth_obj.data[i],
                #                 name=smooth_obj.headers[i]),row=2,col=1)

            fig.update_xaxes(
                rangeslider_visible=True,
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="YTD", step="year", stepmode="todate"),
                        dict(count=1, label="1y", step="year", stepmode="backward"),
                        dict(step="all")
                    ])
                )
            )

            fig.update_layout(yaxis=dict(type='log'))
            fig.write_html(f'plot_output/smooth_timeline_{country}.html',full_html=full_html)

        except Exception as e:
            logger.error(str(e))
    
    def plot_smoothened(self,smooth_obj,country,full_html=True):
        try:
            attr=self.smoothened(smooth_obj)
            self.fig=go.Figure()
            h_fill_color=self.colorHeaderBG
            h_font_color=self.colorHeaderFont
            self.add_table(attr.headers7,smooth_obj.data7,self.colorCellFont,h_fill_color,h_font_color,visibility=True)
            self.add_table(attr.headers14,smooth_obj.data14, self.colorCellFont,h_fill_color,h_font_color)
            self.add_table(attr.headers,smooth_obj.data,self.colorCellFont,h_fill_color,h_font_color)
            smooth_dropdowns = add_update_menus(attr.dropdown1,attr.dropdown2,option3_dict=attr.dropdown3)
            self.update_layout(smooth_dropdowns,f"<b> Corona statistics for {self.country_name} </b>")
            self.fig.write_html(f'plot_output/smoothened_example_{country}.html',full_html=full_html)
            #logger.info("Finished plotting smoothened data --- %s seconds ---" % (time.time() - start_time))            

        except Exception as e:
            logger.error(e)

        
    class smoothened():
        def __init__(self,data_obj):
            self.headers7 = [f'<b>{x} </b>' for x in data_obj.headers7]
            self.headers14 = [f'<b>{x} </b>' for x in data_obj.headers14]
            self.headers = [f'<b>{x} </b>' for x in data_obj.headers]
            self.dropdown1 = {'label':'7 day Calculations','visibility': [True,False,False]}
            self.dropdown2 = {'label':'14 day Calculations','visibility': [False,True,False]}
            self.dropdown3 = {'label':'All Calculations','visibility': [False,False,True]}

