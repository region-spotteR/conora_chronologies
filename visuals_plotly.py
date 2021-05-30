from loguru import logger
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import date, timedelta, datetime

import plotly.graph_objects as go


class dictItemsToSelf:
    def __init__(self, dictionary):
        """
        Useful utility class to pass on attributes of a dictionary to a class object
        """
        for k, v in dictionary.items():
            setattr(self, k, v)             # same as self.k=v

class visuals():
    def __init__(self,country_attributes):
        """
        All color and sizing parameters are passed on using the dictItemsToSelf-class. 
        In addition the country name is extracted from the country attributes
        """
        dictItemsToSelf.__init__(self,country_attributes.color_sizes)
        self.country_name = country_attributes.country_name
        self.color_sizes_dict = country_attributes.color_sizes # needed for the threshold class

    def add_table(self,header_list,cells_list,cell_font_color,header_fill_color,header_font_color,visibility=False,cell_fill_color=None,**kwargs):
        """
        A generic function to append tables to a plotly Figure-object. 

        Parameters
        ----------
        
        header_list : list
            A list containing the column_headers
        cell_list : list 
            A list of lists containing the cell values
        cell_font_color : list
            A list of lists containing the cell font color
        header_fill_color : list
            A list containing the background color for each column
        header_font_color : list
            A list containing the font color for each column
        visibility : bool
            Optional. Defaults to False. Should this plot be visible
        cell_fill_color : list
            Optional. Defaults to None. A list of lists with cell background colors for each rows
        **kwargs
            further arguments for go.Table
        """
        try:
            if cell_fill_color is None:
                cell_fill_color = self.create_fill_colors(cells_list)
            # Add traces
            self.fig.add_trace(
                go.Table(
                header=dict(values=header_list,
                            fill_color=header_fill_color,
                            align='left',
                            line_color=self.colorCellFont,#+['white' for i in range(1,len(below_threshold_headers))],
                            font=dict(color=header_font_color, size=self.sizeHeaderFont)
                            ),
                cells=dict(values=cells_list,
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
        """
        Creates a list of background colors for each row. Colors are passed through from the country_settings.py

        Parameters
        ----------
        nested_list: list
            A list of lists containing the threshold values

        Returns
        -------
        list : list
            A list of lists containing background colors for each row
        """
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
        """
        Adds plot title and menus to the Figure-object. Colors are passed through from the country_settings.py

        Parameters
        ----------
        menus: list
            A list of dropdown or buttons menus 
        title_text: str
            Optional. Default is None. A string containing some title text
        """
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



    
    def plot_threshold(self,th_obj,country,full_html=True,only_below=True,no_buttons=True):
        """
        Creates a set of threshold tables and appends them to a plotly Figure object. Writes the output as a file

        Parameters
        ----------
        th_obj : simulate
            simulate-class object from transform_enrich.py. This object contains all simulations and the threshold day calculation
        country : str
            A string countaing a two digit country code
        full_html : bool
            Optional. Defaults to True. This boolean tells plotly if a full hmtl or just a div-object should be returned
        only_below: bool
            Optional. Defaults to true. Only values below the threshold are plotted. Turns of the confusing subplots
        no_buttons: bool
            Optional. Defaults to true. Have all controls in the dropdown (strongly recommended!)
        """
        try:
            if only_below:
                th_obj.values14_above_th=None
                th_obj.values7_above_th=None
            attr = self.threshold(th_obj,self.color_sizes_dict)
            self.fig = attr.create_figure_and_title(self.country_name)
            self.add_threshold_table(attr,th_obj.values7_below_th,th_obj.th_below7,th_dates=True)
            self.add_threshold_table(attr,th_obj.values7_below_th,th_obj.th_below7)
            self.add_threshold_table(attr,th_obj.values14_below_th,th_obj.th_below14,th_dates=True)
            self.add_threshold_table(attr,th_obj.values14_below_th,th_obj.th_below14)
            self.add_threshold_table(attr,th_obj.values7_above_th,th_obj.th_above7,below=False,th_dates=True)
            self.add_threshold_table(attr,th_obj.values7_above_th,th_obj.th_above7,below=False)
            self.add_threshold_table(attr,th_obj.values14_above_th,th_obj.th_above14,below=False,th_dates=True)
            self.add_threshold_table(attr,th_obj.values14_above_th,th_obj.th_above14,below=False)

            attr.create_dropdown()
            if no_buttons:
                dropdown_list=attr.update_dropdowns(attr.dropdown1,attr.dropdown2)
                threshold_dropdowns = add_update_menus(dropdown_list)
            else:
                attr.create_buttons(attr.dropdown1,attr.dropdown2)
                threshold_dropdowns = add_update_menus([attr.dropdown1,attr.dropdown2])
                threshold_dropdowns.append(add_update_menus([attr.button1,attr.button2],type_input='buttons',right=False)[0])

                annotations=list(self.fig['layout']['annotations'])
                annotations.append(
                    dict(text="Unit:", showarrow=False,
                                x=0, y=1.16, yref="paper", align="left",font=dict(
                                    size=14,
                                    color='black'
                                ))
                )
                self.fig['layout']['annotations']=tuple(annotations)
            
            if attr.table_count<=2:
                self.update_layout(threshold_dropdowns)
            else:
                self.update_layout(threshold_dropdowns,attr.titleText)

            self.fig.write_html(f"plot_output/thresholds_{country}.html",validate=False,full_html=full_html,include_plotlyjs=False)

            if attr.table_count<=2:
                self.add_title(country)


        except Exception as e:
            logger.error(e)

    def add_title(self,country):
        """ Adds the plot title as h1 html title"""
        try:
            plotly_js_str= """
                <script type="text/javascript"> window.PlotlyConfig = { MathJaxConfig: "local" }; </script>
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            """
            title_text=f'<h1 style="color:{self.colorTitle}"> <b> {self.country_name}: Dates when the new cases per 100k fall <em> below </em> a threshold </b> </h1> \n'
            with open(f'plot_output/thresholds_{country}.html','r') as file:
                div_str = file.read()
            new_str= title_text+plotly_js_str+div_str
            with open(f'plot_output/thresholds_{country}.html','w') as file:
                file.write(new_str)

        except Exception as e:
            logger.error(e)


    def add_threshold_table(self,th_class,cell_list,th_header,below=True,th_dates=False):
        """
        Adds a threshold table to the Figure-Object. 

        Parameters
        ----------
        th_class : threshold
            threshold-class object
        cell_list : list 
            A list of lists containing the cell values
        th_header : list
            A list containing the column_headers
        below: bool
            Defaults to true. The boolean indicates if cell_list contains values below the threshold or above. Only important for plotly subplots            
        th_dates: bool
            Defaults to False. A boolean indicating if the values in cell_list should be transformed in to dates
        """
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
                header=th_class.create_column_header(th_header,below)
                cell_font_color=th_class.create_cell_font_color(cell_list)
                if th_class.table_count > 2:
                    self.add_table(header,cell_list,cell_font_color,h_fill_color,h_font_color,row=row_number,col=1)
                else:
                    self.add_table(header,cell_list,cell_font_color,h_fill_color,h_font_color)

        except Exception as e:
            logger.error(e)


    class threshold(dictItemsToSelf):
        def __init__(self,data_obj,color_sizes_dict):
            """
            All color and sizing parameters are passed on using the dictItemsToSelf-class. 
            In addition booleans are created to indicate to class methods if objects exist. 
            """
            dictItemsToSelf.__init__(self,color_sizes_dict)
            self.bool7_below_th=(data_obj.values7_below_th is not None)
            self.bool14_below_th=(data_obj.values14_below_th is not None)
            self.bool7_above_th=(data_obj.values7_above_th is not None)
            self.bool14_above_th=(data_obj.values14_above_th is not None)
            self.table_count = sum([self.bool7_below_th,self.bool14_below_th,self.bool7_above_th,self.bool14_above_th])
            self.titleText=None # This has a default value of None since for subplots plotly is creating the title inside the figure creation

        def create_figure_and_title(self,country_name):
            """
            Starts the plotting process through creation of the Figure container. Also creates titles. Colors are passed through from the country_settings.py

            Parameters
            ----------
            country_name : str
                Country name as a string

            Returns
            -------
            Figure: Figure
                A plotly Figure object containing the title
            """
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
                    below=f"<b> {country_name}: Dates when the new cases per 100k fall <em> below </em> a threshold </b>"
                    above=f"<b> {country_name}: Dates when the new cases per 100k rise <em> above </em> a threshold </b>"
                    self.titleText = below if self.bool7_below_th else above  
                    return go.Figure()

            except Exception as e:
                logger.error(e)
                
        def create_column_header(self,th_list,below=True):
            """
            Create a list of column headers for the threshold table

            Parameters
            ----------
            th_list : list
                A list containing the used threshold values
            below : bool
                Optional. Default is True. A boolean indicating if the thresholds are below the current Covid incidence (Cases per 100k) or above 

            Returns
            -------
            list: list
                A list of header strings for the table
            """
            try:
                header1=['<b>Assumed R value </b>']
                comp_text= 'New Cases per 100k < ' if below else 'New Cases per 100k > '
                header2 =  [f"<b>{comp_text}{x}</b>" for x in th_list]
                return header1+header2

            except Exception as e:
                logger.error(e)
        
        def create_cell_font_color(self,nested_list):
            """
            Creates a list of lists containing the colors for each column item. Colors are passed through from the country_settings.py

            Parameters
            ----------
            nested_list : list
                A list of lists containing the table values

            Returns
            -------
            list: list
                A list of lists containing the cell colors
            """
            try:
                normalCellFontColor=[self.colorCellFont]*len(nested_list[0])
                return [[self.colorPivotColumnText]*len(nested_list[0])] + [normalCellFontColor]*(len(nested_list)-1)
    
            except Exception as e:
                logger.error(e)

        def create_dropdown(self):
            """
            Creates a dictionary for dropdowns with label attribute and visibility list. All out output is written to the threshold class
            """
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
                    self.dropdown1 = {'label':'7 day Calculations','visibility': [True,False]}
                    self.dropdown2 = {'label':'14 day Calculations','visibility': [False,True]}          
                          
            except Exception as  e:
                logger.error(e)
        
        def create_buttons(self,dropdown1,dropdown2):
            """
            Creates dictionary for buttons and updates existing dropdowns. No return since everything appended to the threshold class object

            Parameters
            ----------
            dropdown1 : dict
                A dictionary containing a label and visibility of the dropdown
            dropdown2 : dict
                A dictionary containing a label and visibility of the dropdown
            """
            try: 
                self.buttons=[{'label': 'dates','visibility':[True,False]*len(dropdown1.get('visibility'))},
                              {'label': 'days','visibility':[False,True]*len(dropdown1.get('visibility'))}]
                self.dropdown1['visibility']=[item for item in dropdown1.get('visibility') for i in range(2)]
                self.dropdown2['visibility']=[item for item in dropdown2.get('visibility') for i in range(2)]
                
            except Exception as e:
                logger.error(e)

        def update_dropdowns(self,dropdown1,dropdown2):
            """
            Updates existing dropdowns. No return since everything appended to the threshold class object

            Parameters
            ----------
            dropdown1 : dict
                A dictionary containing a label and visibility of the dropdown
            dropdown2 : dict
                A dictionary containing a label and visibility of the dropdown
            """
            try: 
                self.dropdown11={'label':'Days: 7 day Calculations','visibility': update_visibility(dropdown1['visibility'],order=[False,True])}
                self.dropdown1['label']='Dates: '+ dropdown1['label']
                self.dropdown1['visibility']=update_visibility(dropdown1['visibility'])
         
                self.dropdown22={'label':'Days: 14 day Calculations','visibility': update_visibility(dropdown2['visibility'],order=[False,True])}
                self.dropdown2['label']='Dates: '+ dropdown2['label']
                self.dropdown2['visibility']=update_visibility(dropdown2['visibility'])

                return [self.dropdown1,self.dropdown11,self.dropdown2,self.dropdown22]

            except Exception as e:
                logger.error(e)


        def get_threshold_dates(self,days):
            """
            Creates a date based on an integer

            Parameters
            ----------
            days : int
                Amount of days until a threshold is reached

            Returns
            -------
            th_date : string
                A date in isoformat 
            """
            try:    
                th_date=date.today()+timedelta(days)
                return th_date.isoformat()
            except Exception as e:
                logger.error(e)

        def get_th_date_list(self,th_list):
            """
            Creates a list of lists with concrete dates when a threshold is reached

            Parameters
            ----------
            th_list : list
                A list of lists containing the amount of days until a threshold is reached depending on an assumed R-Value

            Returns
            -------
            list
                A list of lists containing a definite day when a threshold is reached depending on an assumed R-Value
            """
            try:
                result=[[self.get_threshold_dates(day_int) for day_int in th_list[i]] for i in range(1,len(th_list))]
                result.insert(0,th_list[0])
                return result
            except Exception as e:
                logger.error(e)


def update_visibility(current_visibility,order=[True,False]):
    """ Updates the dropdown visibility for the plotly plot if another criteria is added"""
    try:
        end=[]
        for i in range(0,len(current_visibility)):
            if current_visibility[i]:
                end.append(order[0])
                end.append(order[1])
            else:
                end.append(False)
                end.append(False)

        return end

    except Exception as e:
        logger.error(e)
    
def add_update_menus(option_dict_list,type_input='dropdown',right=True):
    """
    Creates a list item with a (dropdown or button) menu
    
    Parameters
    ----------
    option_dict_list : list
        A list of dictionaries containing the option name and its visibility as a list of booleans (cf. create_dropdowns)
    type_input : str
        Optional. Default is 'dropdown'. A String containing the menu-type, can either be 'dropdown' or 'buttons'. 
    right : bool
        Optional. Default is True. A boolean indicating if the menu is left or right of the plot
    

    Returns
    -------
    list
        A list containing a dictionary with a list specification of the buttons and positioning attributes
    """
    try:
        if right:
            x_input=1
            xanchor_input="right"
            direction_input="down"
            y_input=1.17
        else:
            direction_input="left"
            x_input=0.08
            xanchor_input="left"
            y_input=1.17

        # Creating a list with the specification of each dropdown option
        custom_buttons=list([
            # dict(
            #     label=str(option_dict_list[0]['label']),
            #     method='update',
            #     args=[{"visible":option_dict_list[0]['visibility']}]
            # )
        ])

        for option_dict in option_dict_list:
            custom_buttons.append(
                dict(
                label=str(option_dict['label']),
                method='update',
                args=[{"visible":option_dict['visibility']}]
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
    