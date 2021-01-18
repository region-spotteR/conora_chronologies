from loguru import logger
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time

class plots():
    def __init__(self,country_attributes):
        self.colors_sizes=country_attributes.color_scheme()
        self.country_name = country_attributes.country_name


    def add_table(self,header_dict,cells_dict,cell_fill_color,cell_font_color,header_fill_color,header_font_color,visibility=False,**kwargs):
        try:
            # Add traces
            self.fig.add_trace(
                go.Table(
                header=dict(values=header_dict,
                            fill_color=header_fill_color,
                            align='left',
                            line_color=self.colors_sizes.cellFontColor,#+['white' for i in range(1,len(below_threshold_headers))],
                            font=dict(color=header_font_color, size=self.colors_sizes.headerFontSize)
                            ),
                cells=dict(values=cells_dict,
                        fill_color=cell_fill_color,
                        font=dict(color=cell_font_color,size=self.colors_sizes.cellFontSize),
                        align='left'),
                        visible=visibility
                        ),
                **kwargs
            )

        except Exception as e:
            logger.error(e)


    def update_layout(self,menus,title_text=None):
        try:
            if title_text is None:
                title_dict = None
            else:
                title_dict = dict(
                    text=title_text,
                    font=dict(size=self.colors_sizes.titleFontSize,
                            color=self.colors_sizes.titleColor),
                )

            self.fig.update_layout(title=title_dict,updatemenus=menus)

        except Exception as e:
            logger.error(e)


    def plot_smoothened(self,smooth_obj,country,full_html=True):
        try:
            attr=self.smoothened(smooth_obj,self.colors_sizes)
            self.fig=attr.fig
            h_fill_color=self.colors_sizes.headerBGcolor
            h_font_color=self.colors_sizes.headerFontColor
            self.add_table(attr.headers7,smooth_obj.data7,attr.fill_color7,attr.cell_font_color,h_fill_color,h_font_color,visibility=True)
            self.add_table(attr.headers14,smooth_obj.data14,attr.fill_color14,attr.cell_font_color,h_fill_color,h_font_color)
            self.add_table(attr.headers,smooth_obj.data,attr.fill_color,attr.cell_font_color,h_fill_color,h_font_color)
            smooth_dropdowns = add_update_menus(attr.dropdown1,attr.dropdown2,attr.dropdown3)
            self.update_layout(smooth_dropdowns,f"<b> Corona statistics for {self.country_name} </b>")
            self.fig.write_html(f'plot_output/smoothened_example_{country}.html',full_html=full_html)
            #logger.info("Finished plotting smoothened data --- %s seconds ---" % (time.time() - start_time))

        except Exception as e:
            logger.error(e)

        
    class smoothened():
        def __init__(self,data_obj,country_attributes):
            self.colors_sizes = country_attributes
            self.fig = go.Figure()
            self.fill_color7 = create_fill_colors(data_obj.data7,self.colors_sizes.rowEvenColor,self.colors_sizes.rowOddColor)
            self.fill_color14 = create_fill_colors(data_obj.data14,self.colors_sizes.rowEvenColor,self.colors_sizes.rowOddColor)
            self.fill_color = create_fill_colors(data_obj.data,self.colors_sizes.rowEvenColor,self.colors_sizes.rowOddColor)
            self.headers7 = [f'<b>{x} </b>' for x in data_obj.headers7]
            self.headers14 = [f'<b>{x} </b>' for x in data_obj.headers14]
            self.headers = [f'<b>{x} </b>' for x in data_obj.headers]
            self.cell_font_color = 'black'
            self.dropdown1 = {'label':'7 day Calculations','visibility': [True,False,False]}
            self.dropdown2 = {'label':'14 day Calculations','visibility': [False,True,False]}
            self.dropdown3 = {'label':'All Calculations','visibility': [False,False,True]}
    
    def plot_threshold(self,th_obj,country,full_html=True):
        try:
            attr = self.threshold(th_obj,self.colors_sizes)
            self.fig = attr.create_figure(self.country_name)
            attr.create_cell_and_header_lists()
            if attr.values7_below_th:
                cell_fill_color=create_fill_colors(attr.below_list7,self.colors_sizes.rowEvenColor,self.colors_sizes.rowOddColor)
                h_fill_color=['white'] + ([self.colors_sizes.headerBGcolor]*len(attr.below_headers7))
                h_font_color=[self.colors_sizes.PivotColumnTextColor]+([self.colors_sizes.headerFontColor]*len(attr.below_headers7))
                self.add_table(attr.below_headers7,attr.below_list7,cell_fill_color,attr.below_cellFontColor7,h_fill_color,h_font_color,visibility=True, row=1, col=1)
            if attr.values14_below_th:
                cell_fill_color=create_fill_colors(attr.below_list14,self.colors_sizes.rowEvenColor,self.colors_sizes.rowOddColor)
                h_fill_color=['white'] + ([self.colors_sizes.headerBGcolor]*len(attr.below_headers14))
                h_font_color=[self.colors_sizes.PivotColumnTextColor]+([self.colors_sizes.headerFontColor]*len(attr.below_headers14))
                self.add_table(attr.below_headers14,attr.below_list14,cell_fill_color,attr.below_cellFontColor14,h_fill_color,h_font_color,visibility=True, row=1, col=1)
            if attr.values7_above_th:
                row_number = 2 if attr.table_count > 2 else 1
                cell_fill_color=create_fill_colors(attr.above_list7,self.colors_sizes.rowEvenColor,self.colors_sizes.rowOddColor)
                h_fill_color=['white'] + ([self.colors_sizes.headerBGcolor]*len(attr.above_headers7))
                h_font_color=[self.colors_sizes.PivotColumnTextColor]+([self.colors_sizes.headerFontColor]*len(attr.above_headers7))
                self.add_table(attr.above_headers7,attr.above_list7,cell_fill_color,attr.above_cellFontColor7,h_fill_color,h_font_color,visibility=True, row=row_number, col=1)
            if attr.values14_above_th:
                row_number = 2 if attr.table_count > 2 else 1
                cell_fill_color=create_fill_colors(attr.above_list14,self.colors_sizes.rowEvenColor,self.colors_sizes.rowOddColor)
                h_fill_color=['white'] + ([self.colors_sizes.headerBGcolor]*len(attr.above_headers14))
                h_font_color=[self.colors_sizes.PivotColumnTextColor]+([self.colors_sizes.headerFontColor]*len(attr.above_headers14))
                self.add_table(attr.above_headers14,attr.above_list14,cell_fill_color,attr.above_cellFontColor14,h_fill_color,h_font_color,visibility=True, row=row_number, col=1)
            
            attr.create_dropdown(self.country_name)
            threshold_dropdowns = add_update_menus(attr.dropdown1,attr.dropdown2)
            self.update_layout(threshold_dropdowns,attr.titleText)
            
            self.fig.write_html(f"plot_output/threshold_days_example2_{country}.html",validate=False,full_html=full_html)
 
        except Exception as e:
            logger.error(e)
    


    class threshold():
        def __init__(self,data_obj,country_attributes):
            self.colors_sizes = country_attributes
            self.titleText=None

            # Which is the index of the first simulated effektive R-value above 1
            self.in_Rrange = data_obj.input_range_for_r
            self.index_first_R_above_one=next((i for i in range(0,len(self.in_Rrange)) if self.in_Rrange[i]>1),len(self.in_Rrange))

            # Data source
            self.list7=data_obj.threshold_days7
            self.list14=data_obj.threshold_days14

            # Data width 
            self.th_len=len(self.list7) # should be proportionate to the threshold list length -> th_len
            th_range=range(1,self.th_len) # first list item are the effektive simulated R-values -> first to last are threshold days

            # How many of the first threshold values are below our current cases per 100k for 7/14 days
            self.th_above_current7_i=next((i for i in th_range if self.list7[i][0] is None),
                                            len(self.list7))
            self.th_above_current14_i=next((i for i in th_range if self.list14[i][0] is None),
                                            len(self.list14))    

            # are there any threshold days below/above our current cases per 100k for 7/14 days?
            self.values7_below_th=(self.th_above_current7_i>1)
            self.values14_below_th=(self.th_above_current14_i>1)
            self.values7_above_th=(self.th_above_current7_i<self.th_len)
            self.values14_above_th=(self.th_above_current14_i<self.th_len)
            self.table_count = sum([self.values7_below_th,self.values14_below_th,self.values7_above_th,self.values14_above_th])
        


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
                                            size=self.colors_sizes.titleFontSize,
                                            color=self.colors_sizes.titleColor
                                            )
                        subplot_title['xanchor']='left'
                        subplot_title['x']=0
                        subplot_title['y']=subplot_title['y']+0.04
                    
                    return fig

                else:
                    return go.Figure()

            except Exception as e:
                logger.error(e)
        

        def create_cell_and_header_lists(self,th_list=[10,20,50,100,200,400,600,800,1000]):
            try:
                r1_index=self.index_first_R_above_one
                if self.values7_below_th:
                    self.below_list7=[self.list7[i][:r1_index] for i in range(0,self.th_above_current7_i)]
                    self.below_headers7=self.create_header(self.th_above_current7_i,th_list,below=True)
                    self.below_cellFontColor7=self.create_cell_font_color(self.th_above_current7_i,th_list)
                if self.values14_below_th:
                    self.below_list14=[self.list14[i][:r1_index] for i in range(0,self.th_above_current14_i)]
                    self.below_headers14=self.create_header(self.th_above_current14_i,th_list,below=True)
                    self.below_cellFontColor14=self.create_cell_font_color(self.th_above_current14_i,th_list)
                if self.values7_above_th:
                    self.above_list7=[self.list7[i][r1_index:] for i in range(self.th_above_current7_i,self.th_len)]
                    self.above_list7.insert(0,self.list7[0][r1_index:])
                    self.above_headers7=self.create_header(self.th_above_current7_i,th_list,below=False)
                    self.above_cellFontColor7=self.create_cell_font_color(self.th_above_current7_i,th_list,below=False)
                if self.values14_above_th:
                    self.above_list14=[self.list7[i][r1_index:] for i in range(self.th_above_current14_i,self.th_len)]
                    self.above_list14.insert(0,self.list14[0][r1_index:])
                    self.above_headers14=self.create_header(self.th_above_current14_i,th_list,below=False)
                    self.above_cellFontColor14=self.create_cell_font_color(self.th_above_current14_i,th_list,below=False)
                    
            except Exception as e:
                logger.error(e)
        
        def create_header(self,index,th_list,below=True):
            try:
                header1=['<b> Assumed R value </b>']
                if below:
                    header2=[f"<b>New Cases per 100k < {th_list[i]}</b>" for i in range(0,index-1)]
                else:
                    header2=[f"<b>New Cases per 100k > {th_list[i]}</b>" for i in range(index-1,len(th_list))]
                    
                return header1+header2

            except Exception as e:
                logger.error(e)

        def create_cell_font_color(self,index,th_list,below=True):
            try:
                index_th = index-1 if below else len(th_list)-index
                index_R1= self.index_first_R_above_one if below else len(self.in_Rrange)-self.index_first_R_above_one
                normalCellFontColor=[self.colors_sizes.cellFontColor]*index_R1
                return [[self.colors_sizes.PivotColumnTextColor]*index_R1] + [normalCellFontColor]*index_th
    
            except Exception as e:
                logger.error(e)


        def create_dropdown(self,country_name):
            try:
                if self.table_count==4:
                    self.dropdown1 = {'label':'7 day Calculations','visibility': [True,False,True,False]}
                    self.dropdown2 = {'label':'14 day Calculations','visibility': [False,True,False,True]}
                elif self.table_count==3 and not (self.values7_below_th):
                    # no below threshold for 7 days per 100k sums
                    self.dropdown1 = {'label':'7 day Calculations','visibility': [False,True,False]}
                    self.dropdown2 = {'label':'14 day Calculations','visibility': [True,False,True]}
                    # If there is no below threshold for 14 days then there is also no below threshold table for the 7 days --> else
                elif self.table_count ==3 and not (self.values14_above_th):
                    # no above threshold for 14 days per 100k 
                    self.dropdown1 = {'label':'7 day Calculations','visibility': [True,False,True]}
                    self.dropdown2 = {'label':'14 day Calculations','visibility': [False,True,False]}
                    # If there is no above threshold for 7 days then there is also no above threshold table for the 14 days -> else
                else:
                    below=f"<b> {country_name}: Dates when the new cases per 100k fall <em> below </em> a threshold </b>"
                    above=f"<b> {country_name}: Dates when the new cases per 100k rise <em> above </em> a threshold </b>"
                    self.dropdown1 = {'label':'7 day Calculations','visibility': [True,False]}
                    self.dropdown2 = {'label':'14 day Calculations','visibility': [False,True]}
                    self.titleText = below if self.values7_below_th else above            
                          
            except Exception as  e:
                logger.error(e)



def create_fill_colors(nested_list,rowEvenColor,rowOddColor):
    try:
        row_length=len(nested_list[0])
        col_length=len(nested_list)
        if (row_length%2)==0:
            rowColors=[rowOddColor,rowEvenColor]*int(row_length/2)
        else:
            denominator=int((row_length-1)/2)
            rowColors=[rowOddColor,rowEvenColor]*int(denominator/2)
            rowColors.append(rowOddColor)
        
        return [rowColors*col_length]
    except Exception as e:
        logger.error(e)


def add_update_menus(option1_dict,option2_dict,option3_dict=None):
    try:
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
                active=0,
                buttons=custom_buttons,
                x=1,
                xanchor="right",
                y=1.07,
                yanchor="top"
            )
        ]
        return menu
    
    except Exception as e:
        logger.error(e)
    