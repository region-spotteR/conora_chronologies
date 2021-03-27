from loguru import logger
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import date, timedelta

class dictItemsToSelf:
    def __init__(self, dictionary):
        for k, v in dictionary.items():
            setattr(self, k, v)             # same as self.k=v

class plots():
    def __init__(self,country_attributes):
        dictItemsToSelf.__init__(self,country_attributes.color_sizes)
        # self.colors_sizes=country_attributes.color_sizes() # wrong
        self.country_name = country_attributes.country_name
        self.color_sizes_dict = country_attributes.color_sizes
        # self.rowEvenColor = self.colors_sizes.rowEvenColor
        # self.rowOddColor = self.colors_sizes.rowOddColor

    def add_table(self,header_dict,cells_dict,cell_font_color,header_fill_color,header_font_color,visibility=False,cell_fill_color=None,**kwargs):
        try:
            if cell_fill_color is None:
                cell_fill_color = self.create_fill_colors(cells_dict)
            # Add traces
            self.fig.add_trace(
                go.Table(
                header=dict(values=header_dict,
                            fill_color=header_fill_color,
                            align='left',
                            line_color=self.colorCellFont,#+['white' for i in range(1,len(below_threshold_headers))],
                            font=dict(color=header_font_color, size=self.sizeHeaderFont)
                            ),
                cells=dict(values=cells_dict,
                        fill_color=cell_fill_color,
                        font=dict(color=cell_font_color,size=self.sizeCellFont),
                        align='left'),
                        visible=visibility
                        ),
                **kwargs
            )

        except Exception as e:
            logger.error(e)

    def create_fill_colors(self,nested_list):
        try:
            row_length=len(nested_list[0])
            col_length=len(nested_list)
            if (row_length%2)==0:
                rowColors=[self.colorOddRows,self.colorEvenRows]*int(row_length/2)
            else:
                denominator=int((row_length-1)/2)
                rowColors=[self.colorOddRows,self.colorEvenRows]*int(denominator/2)
                rowColors.append(self.colorOddRows)
            
            return [rowColors*col_length]
        except Exception as e:
            logger.error(e)


    def update_layout(self,menus,title_text=None):
        try:
            if title_text is None:
                title_dict = None
            else:
                title_dict = dict(
                    text=title_text,
                    font=dict(size=self.sizeTitleFont,color=self.colorTitle),
                )

            self.fig.update_layout(title=title_dict,updatemenus=menus)

        except Exception as e:
            logger.error(e)

    def add_threshold_table(self,cell_list,header_list,below=True,dates=True):
        try:
            if cell_list is not None:
                th_flow='New Cases per 100k < ' if below else 'New Cases per 100k > '
                headers_l=['<b> Assumed R value </b>']+[f"<b>{th_flow} {str(th)} </b>" for th in header_list]

        except Exception as e:
            logger.error(e)


    def plot_smoothened(self,smooth_obj,country,full_html=True):
        try:
            attr=self.smoothened(smooth_obj)
            self.fig=attr.fig
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
            self.fig = go.Figure()
            self.headers7 = [f'<b>{x} </b>' for x in data_obj.headers7]
            self.headers14 = [f'<b>{x} </b>' for x in data_obj.headers14]
            self.headers = [f'<b>{x} </b>' for x in data_obj.headers]
            self.dropdown1 = {'label':'7 day Calculations','visibility': [True,False,False]}
            self.dropdown2 = {'label':'14 day Calculations','visibility': [False,True,False]}
            self.dropdown3 = {'label':'All Calculations','visibility': [False,False,True]}
    
    def plot_threshold(self,th_obj,country,full_html=True):
        try:
            attr = self.threshold(th_obj,self.color_sizes_dict)
            self.fig = attr.create_figure(self.country_name)
            self.add_threshold_table(attr,th_obj.values7_below_th,th_obj.th_below7,th_dates=True)
            self.add_threshold_table(attr,th_obj.values7_below_th,th_obj.th_below7)
            self.add_threshold_table(attr,th_obj.values14_below_th,th_obj.th_below14,th_dates=True)
            self.add_threshold_table(attr,th_obj.values14_below_th,th_obj.th_below14)
            self.add_threshold_table(attr,th_obj.values7_above_th,th_obj.th_above7,below=False,th_dates=True)
            self.add_threshold_table(attr,th_obj.values7_above_th,th_obj.th_above7,below=False)
            self.add_threshold_table(attr,th_obj.values14_above_th,th_obj.th_above14,below=False,th_dates=True)
            self.add_threshold_table(attr,th_obj.values14_above_th,th_obj.th_above14,below=False)

            attr.create_dropdown(self.country_name)
            attr.create_buttons(attr.dropdown1,attr.dropdown2)
            threshold_dropdowns = add_update_menus(attr.dropdown1,attr.dropdown2)
            threshold_dropdowns.append(add_update_menus(attr.button1,attr.button2,type_input='buttons',right=False)[0])
            annotations=list(self.fig['layout']['annotations'])
            annotations.append(
                dict(text="Unit:", showarrow=False,
                             x=0, y=1.06, yref="paper", align="left",font=dict(
                                 size=14,
                                color='black'
                             ))
            )
            self.fig['layout']['annotations']=tuple(annotations)


            self.update_layout(threshold_dropdowns,attr.titleText)
            self.fig.write_html(f"plot_output/threshold_days_example2_{country}.html",validate=False,full_html=full_html)
        
        except Exception as e:
            logger.error(e)

    def add_threshold_table(self,th_class,cell_list,th_header,below=True,th_dates=False):
        try:
            if cell_list is not None:
                if th_dates:
                    cell_list_days=th_class.get_th_date_list(cell_list)
                    cell_list=cell_list_days

                row_number = 2 if th_class.table_count > 2 else 1
                if below:
                    row_number=1
                h_fill_color=['white'] + ([self.colorHeaderBG]*len(th_header))
                h_font_color=[self.colorPivotColumnText]+([self.colorHeaderFont]*len(th_header))
                header=th_class.create_header(th_header,below)
                cell_font_color=th_class.create_cell_font_color(cell_list)
                self.add_table(header,cell_list,cell_font_color,h_fill_color,h_font_color,row=row_number,col=1)

        except Exception as e:
            logger.error(e)


    class threshold(dictItemsToSelf):
        def __init__(self,data_obj,color_sizes_dict):
            dictItemsToSelf.__init__(self,color_sizes_dict)
            self.bool7_below_th=(data_obj.values7_below_th is not None)
            self.bool14_below_th=(data_obj.values14_below_th is not None)
            self.bool7_above_th=(data_obj.values7_above_th is not None)
            self.bool14_above_th=(data_obj.values14_above_th is not None)
            self.table_count = sum([self.bool7_below_th,self.bool14_below_th,self.bool7_above_th,self.bool14_above_th])
            self.titleText=None

        def create_figure(self,country_name):
            try:
                if self.table_count>2:
                    fig = make_subplots(rows=2, cols=1,
                                        specs=[[{"type": "table"}], [{"type": "table"}]],
                                        subplot_titles=(f"<b> {country_name}: Dates when the new cases per 100k fall <em> below </em> a threshold </b>",
                                        f"<b> {country_name}: Dates when the new cases per 100k rise <em> above </em> a threshold </b>"),
                            )
                    
                    for subplot_title in fig['layout']['annotations']:
                        subplot_title['font']=dict(
                                            size=self.sizeTitleFont,
                                            color=self.colorTitle
                                            )
                        subplot_title['xanchor']='left'
                        subplot_title['x']=0
                        subplot_title['y']=subplot_title['y']+0.07
                    
                    return fig

                else:
                    return go.Figure()

            except Exception as e:
                logger.error(e)
                
        def create_header(self,th_list,below=True):
            try:
                header1=['<b> Assumed R value </b>']
                comp_text= 'New Cases per 100k < ' if below else 'New Cases per 100k > '
                header2 =  [f"<b>{comp_text}{x}</b>" for x in th_list]
                return header1+header2

            except Exception as e:
                logger.error(e)
        
        def create_cell_font_color(self,nested_list):
            try:
                normalCellFontColor=[self.colorCellFont]*len(nested_list[0])
                return [[self.colorPivotColumnText]*len(nested_list[0])] + [normalCellFontColor]*(len(nested_list)-1)
    
            except Exception as e:
                logger.error(e)

        def create_dropdown(self,country_name):
            try:
                if self.table_count==4:
                    self.dropdown1 = {'label':'7 day Calculations','visibility': [True,False,True,False]}
                    self.dropdown2 = {'label':'14 day Calculations','visibility': [False,True,False,True]}
                elif self.table_count==3 and not (self.bool7_below_th):
                    # no below threshold for 7 days per 100k sums
                    self.dropdown1 = {'label':'7 day Calculations','visibility': [False,True,False]}
                    self.dropdown2 = {'label':'14 day Calculations','visibility': [True,False,True]}
                    # If there is no below threshold for 14 days then there is also no below threshold table for the 7 days --> else
                elif self.table_count ==3 and not (self.bool14_above_th):
                    # no above threshold for 14 days per 100k 
                    self.dropdown1 = {'label':'7 day Calculations','visibility': [True,False,True]}
                    self.dropdown2 = {'label':'14 day Calculations','visibility': [False,True,False]}
                    # If there is no above threshold for 7 days then there is also no above threshold table for the 14 days -> else
                else:
                    below=f"<b> {country_name}: Dates when the new cases per 100k fall <em> below </em> a threshold </b>"
                    above=f"<b> {country_name}: Dates when the new cases per 100k rise <em> above </em> a threshold </b>"
                    self.dropdown1 = {'label':'7 day Calculations','visibility': [True,False]}
                    self.dropdown2 = {'label':'14 day Calculations','visibility': [False,True]}
                    self.titleText = below if self.bool7_below_th else above            
                          
            except Exception as  e:
                logger.error(e)
        
        def create_buttons(self,dropdown1,dropdown2):
            try: 
                self.button1={'label': 'dates','visibility':[True,False]*len(dropdown1.get('visibility'))}
                self.button2={'label': 'days','visibility':[False,True]*len(dropdown1.get('visibility'))}
                self.dropdown1['visibility']=[item for item in dropdown1.get('visibility') for i in range(2)]
                self.dropdown2['visibility']=[item for item in dropdown2.get('visibility') for i in range(2)]
                
            except Exception as e:
                logger.error(e)

        def get_threshold_dates(self,days):
            try:    
                th_date=date.today()+timedelta(days)
                return th_date.isoformat()
            except Exception as e:
                logger.error(e)

        def get_th_date_list(self,th_list):
            try:
                result=[[self.get_threshold_dates(day_int) for day_int in th_list[i]] for i in range(1,len(th_list))]
                result.insert(0,th_list[0])
                return result
            except Exception as e:
                logger.error(e)



def add_update_menus(option1_dict,option2_dict,type_input='dropdown',right=True,option3_dict=None):
    try:
        if right:
            x_input=1
            xanchor_input="right"
            direction_input="down"
            y_input=1.07
        else:
            direction_input="left"
            x_input=0.05
            xanchor_input="left"
            y_input=1.07

        custom_buttons=list([
            dict(
                label=str(option1_dict['label']),
                method='update',
                args=[{"visible":option1_dict['visibility']}]
            ),
            dict(
                label=str(option2_dict['label']),
                method='update',
                args=[{"visible":option2_dict['visibility']}]
            )
        ])
        if option3_dict is not None:
            custom_buttons.append(
                dict(
                label=str(option3_dict['label']),
                method='update',
                args=[{"visible":option3_dict['visibility']}]
                )
            )

        menu = [
            dict(
                type=type_input,
                active=0,
                direction=direction_input,
                buttons=custom_buttons,
                x=x_input,
                xanchor=xanchor_input,
                y=y_input,
                yanchor="top"
            )
        ]
        return menu
    
    except Exception as e:
        logger.error(e)
    