from covid_utils import download_lv_covid_data,download_de_covid_data_pandaless,calculate_smoothened_values_pandaless, simulate_threshold_dates, simulate_new_cases_pandaless
import time
from loguru import logger
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

def process_data_and_create_plots(country='lv'):
    try:
        start_time = time.time()

        if country=='lv':
            # URL for latvia
            url='https://data.gov.lv/dati/eng/api/3/action/datastore_search_sql?sql=SELECT%20*%20from%20%22d499d2f0-b1ea-4ba2-9600-2c701b03bd4a%22'
            from_young_to_old_dates=True
            cases_dict,tests_dict=download_lv_covid_data(url,reversed_dates=from_young_to_old_dates)
            population=1907675
            list_of_tests_by_day=list(tests_dict.values())
            country_name='Latvia'


            # Thresholds for the threshold days plot
            CasesPer100k_thresholds=[10,20,50,100,200,400,600,800,1000]

            # color configuration
            rowEvenColor = '#F3EED9'#'#FFE3F1'#'#FFAFAE'
            rowOddColor = 'white'
            headerBGcolor='#9E3039'
            headerFontColor='white'
            titleColor = '#9E3039'
            titleFontSize = 27


        elif country=='de':
            url='https://opendata.arcgis.com/datasets/dd4580c810204019a7b8eb3e0b329dd6_0.geojson'
            from_young_to_old_dates=True
            cases_dict=download_de_covid_data_pandaless(url,reversed_dates=from_young_to_old_dates)
            list_of_tests_by_day=None
            population=83190556 # Germany September 2020 population estimate
            country_name='Germany'

            # Thresholds for the threshold days plot
            CasesPer100k_thresholds=[10,20,50,100,200,400,600,800,1000]


            rowEvenColor = '#FFE6D9'#'#FFE3F1'#'#FFAFAE'
            rowOddColor = 'white'
            headerBGcolor='#FFCE00'
            headerFontColor='black'
            titleColor = 'black'
            titleFontSize = 27

        else:
            logger.error(f'No download method for country {country} available')
            return

        print("Data loaded in --- %s seconds ---" % (time.time() - start_time))
        # Calculate smoothened data
        list_of_days=list(cases_dict.keys())
        smoothened_list, headers_smoothened=calculate_smoothened_values_pandaless(population,list(cases_dict.values()),list_of_days,
                                                                                    list_of_tests=list_of_tests_by_day,
                                                                                    reversed_dates=from_young_to_old_dates)

        ## Select all 7 day calculations from smoothened_list
        headers_smoothened7 = list(filter(lambda x: x.find('14d')<0,headers_smoothened)) # Idea about x.find(): anything not containing the 14d calculations needs to be kept
        smoothened_list7 = [x for x, y in zip(smoothened_list, headers_smoothened) if y.find('14d')<0]

        ## Select all 14 day calculations from smoothened_list
        headers_smoothened14 = list(filter(lambda x: x.find('7d')<0 or x=='Positive Rate 7d', headers_smoothened)) # Idea about x.find(): anything not containing the 7d calculations needs to be kept
        smoothened_list14 = [x for x, y in zip(smoothened_list, headers_smoothened) if y.find('7d')<0 or y=='Positive Rate 7d' ]

        print("Finished creating smoothened data --- %s seconds ---" % (time.time() - start_time))

        # Calculate simulated data

        ## Calculate threshold days
        Range_for_R=[0.8,0.85,0.9,0.95,1.05,1.1,1.15,1.2]
        if from_young_to_old_dates:
            new_cases_avg=smoothened_list[headers_smoothened.index('7d mean')][0]
        else:
            mean7d=smoothened_list[headers_smoothened.index('7d mean')]
            new_cases_avg=mean7d[len(mean7d)-1]
        
        threshold_days_list=simulate_threshold_dates(Range_for_R,new_cases_avg,population,CasesPer100k_thresholds)
        threshold_days_list14=simulate_threshold_dates(Range_for_R,new_cases_avg,population,CasesPer100k_thresholds,sum7=False)
        threshold_days_header=list(map(str,CasesPer100k_thresholds))

        ## simulate new cases
        simulated_new_cases, simulated_casesPer100k_7d, simulated_casesPer100k_14d=simulate_new_cases_pandaless(Range_for_R,new_cases_avg,population)
        simulated_cases_header=['Date']+list(map(str,Range_for_R))

        print("Done preprocessing data - starting to save the plots --- %s seconds ---" % (time.time() - start_time))


        ######################################## smoothened dataset #######################################
        
        fig = go.Figure()


        fillColorList=create_fill_colors(smoothened_list7,rowEvenColor,rowOddColor)
        headers_smoothened_bold=[f'<b>{x} </b>' for x in headers_smoothened7]

        # Add traces
        fig.add_trace(
            go.Table(
            header=dict(values=headers_smoothened_bold,
                        fill_color=headerBGcolor,
                        align='left',
                        font=dict(color=headerFontColor, size=12)
                        ),
            cells=dict(values=smoothened_list7,
                    fill_color=fillColorList, # dictionary here
                    align='left'),
                    visible=True
                    )
        )


        fillColorList=create_fill_colors(smoothened_list14,rowEvenColor,rowOddColor)
        headers_smoothened_bold=[f'<b>{x} </b>' for x in headers_smoothened14]

        # Add traces
        fig.add_trace(
            go.Table(
            header=dict(values=headers_smoothened_bold,
                        fill_color=headerBGcolor,
                        align='left',
                        font=dict(color=headerFontColor, size=12)
                        ),
            cells=dict(values=smoothened_list14,
                    fill_color=fillColorList, # dictionary here
                    align='left'),
                    visible=False
                    )
        )


        fillColorList=create_fill_colors(smoothened_list,rowEvenColor,rowOddColor)
        headers_smoothened_bold=[f'<b>{x} </b>' for x in headers_smoothened]


        # Add traces
        fig.add_trace(
            go.Table(
            header=dict(values=headers_smoothened_bold,
                        fill_color=headerBGcolor,
                        align='left',
                        font=dict(color=headerFontColor, size=12)
                        ),
            cells=dict(values=smoothened_list,
                    fill_color=fillColorList, # dictionary here
                    align='left'),
                    visible=False
                    )
        )


        fig.update_layout(
            title=dict(
                text=f"<b> Corona statistics for {country_name} </b>",
                font=dict(
                    size=titleFontSize,
                    color=titleColor
                ),
                ),
            updatemenus=[
                dict(
                    active=0,
                    buttons=list([
                        dict(
                            label='7 day Calculations',
                            method='update',
                            args=[{"visible":[True,False,False]}]
                        ),
                        dict(
                            label='14 day Calculations',
                            method="update",
                            args=[{"visible":[False,True,False]}]
                        ),
                        dict(
                            label='All Calculations',
                            method="update",
                            args=[{"visible":[False,False,True]}]
                        )
                    ]),
                    x=1,
                    xanchor="right",
                    y=1.07,
                    yanchor="top"
                )
            ]
        )

        fig.write_html(f'plot_output/smoothened_example_{country}.html')


        print("Finished plotting smoothened data --- %s seconds ---" % (time.time() - start_time))


        ######################################## threshold dataset #######################################

        # return the index of the first threshold columns with values above the current level; If none are above this return the last index plus 1
        firstColumnAboveCurrentCasesPer100k=next((i for i in range(1,len(threshold_days_list)) if threshold_days_list[i][0] is None),len(threshold_days_list))
        first_simulated_R_above_one=next((i for i in range(0,len(Range_for_R)) if Range_for_R[i]>1),len(Range_for_R))

        # create plot object
        
        if firstColumnAboveCurrentCasesPer100k>1 and firstColumnAboveCurrentCasesPer100k<len(threshold_days_list):
            fig = make_subplots(rows=2, cols=1,
                specs=[[{"type": "table"}], [{"type": "table"}]],
                subplot_titles=(f"<b> {country_name}: Dates when the new cases per 100k fall <em> below </em> a threshold </b>",
                f"<b> {country_name}: Dates when the new cases per 100k rise <em> above </em> a threshold </b>"),
            )
            updatemenus_dropdowns_visibility7=[True,False,True,False]
            updatemenus_dropdowns_visibility14=[False,True,False,True]
            threshold_subplots=True

            fig.update_layout(
                updatemenus=[
                    dict(
                        active=0,
                        buttons=list([
                            dict(
                                label='7 day Calculations',
                                method='update',
                                args=[{"visible":updatemenus_dropdowns_visibility7}]
                            ),
                            dict(
                                label='14 day Calculations',
                                method="update",
                                args=[{"visible":updatemenus_dropdowns_visibility14}]
                            )
                        ]),
                        x=1,
                        xanchor="right",
                        y=1.07,
                        yanchor="top"
                    )
                ]
            )
        else:
            fig = go.Figure()
            updatemenus_dropdowns_visibility7=[True,False]
            updatemenus_dropdowns_visibility14=[False,True]
            threshold_subplots=False
            if firstColumnAboveCurrentCasesPer100k>1:
                threshold_title_text=f"<b> {country_name}: Dates when the cases per 100k fall <em> below </em> a threshold </b>"
            if firstColumnAboveCurrentCasesPer100k<len(threshold_days_list):
                threshold_title_text=f"<b> {country_name}: Dates when the cases per 100k rise <em> above </em> a threshold </b>"

            fig.update_layout(
                 title=dict(
                    text=threshold_title_text,
                    font=dict(
                        size=titleFontSize,
                        color=titleColor
                    ),
                    ),
                updatemenus=[
                    dict(
                        active=0,
                        buttons=list([
                            dict(
                                label='7 day Calculations',
                                method='update',
                                args=[{"visible":updatemenus_dropdowns_visibility7}]
                            ),
                            dict(
                                label='14 day Calculations',
                                method="update",
                                args=[{"visible":updatemenus_dropdowns_visibility14}]
                            )
                        ]),
                        x=1,
                        xanchor="right",
                        y=1.07,
                        yanchor="top"
                    )
                ]
            )

        # for stuff which is BELOW the current cases per 100k
        if firstColumnAboveCurrentCasesPer100k>1:       # If the second column already contains data above our current cases per 100k this, then all columns contain data above our current cases per 100k
            below_threshold_list=[threshold_days_list[i][:first_simulated_R_above_one] for i in range(0,firstColumnAboveCurrentCasesPer100k)]
            below_threshold_list14=[threshold_days_list14[i][:first_simulated_R_above_one] for i in range(0,firstColumnAboveCurrentCasesPer100k)]
            below_threshold_headers=['<b> Assumed R value </b>']+[f"<b> New Cases per 100k < {threshold_days_header[i]} </b>" for i in range(0,firstColumnAboveCurrentCasesPer100k-1)]

            fillColorList=create_fill_colors(below_threshold_list,rowEvenColor,rowOddColor)
            

            normalFontColor=['black']*first_simulated_R_above_one
            cellFontColor=[['#9E3039']*first_simulated_R_above_one] # first column font color
            cellFontColor.append([normalFontColor]*(firstColumnAboveCurrentCasesPer100k-1))

            header_len=len(below_threshold_headers)-1
            
            # Add traces
            fig.add_trace(
                go.Table(
                header=dict(values=below_threshold_headers,
                            fill_color=['white']+([headerBGcolor]*header_len),
                            align='left',
                            line_color=['#9E3039'],#+['white' for i in range(1,len(below_threshold_headers))],
                            font=dict(color=['#9E3039']+([headerFontColor]*header_len), size=14)
                            ),
                cells=dict(values=below_threshold_list,
                        fill_color=fillColorList,
                        font=dict(color=cellFontColor,size=12),
                        align='left'),
                        visible=True
                        ),
                row=1, col=1
            )

            fig.add_trace(
                go.Table(
                header=dict(values=below_threshold_headers,
                            fill_color=['white']+([headerBGcolor]*header_len),
                            align='left',
                            line_color=['#9E3039'],#+['white' for i in range(1,len(below_threshold_headers))],
                            font=dict(color=['#9E3039']+([headerFontColor]*header_len), size=14)
                            ),
                cells=dict(values=below_threshold_list14,
                        fill_color=fillColorList,
                        font=dict(color=cellFontColor,size=12),
                        align='left'),
                        visible=False
                        ),
                row=1, col=1
            )


        
        # for stuff which is ABOVE the current cases per 100k
        if firstColumnAboveCurrentCasesPer100k<len(threshold_days_list):       # If the last column doesnt contain data above our current cases per 100k, then all columns contain data below our current cases per 100k
            aboveColumnRange=range(firstColumnAboveCurrentCasesPer100k,len(threshold_days_list))
            aboveColumnRange_header=range(firstColumnAboveCurrentCasesPer100k-1,len(threshold_days_header))
            above_threshold_list=[threshold_days_list[i][first_simulated_R_above_one:] for i in aboveColumnRange]
            above_threshold_list.insert(0,threshold_days_list[0][first_simulated_R_above_one:]) #Insert R range above 1  
            above_threshold_list14=[threshold_days_list14[i][first_simulated_R_above_one:] for i in aboveColumnRange]
            above_threshold_list14.insert(0,threshold_days_list[0][first_simulated_R_above_one:]) #Insert R range above 1  
            above_threshold_headers=['<b> Assumed R value </b>']+[f"<b> New Cases per 100k > {threshold_days_header[i]} </b>" for i in aboveColumnRange_header]

            fillColorList=create_fill_colors(above_threshold_list,rowEvenColor,rowOddColor)
            
            

            normalFontColor=['black']*first_simulated_R_above_one
            cellFontColor=[['#9E3039']*first_simulated_R_above_one] # first column font color
            cellFontColor.append([normalFontColor]*(firstColumnAboveCurrentCasesPer100k-1))

            header_len=len(below_threshold_headers)-1
            
            # Add traces
            fig.add_trace(
                go.Table(
                header=dict(values=above_threshold_headers,
                            fill_color=['white']+([headerBGcolor]*header_len),
                            align='left',
                            line_color=['#9E3039'],#+['white' for i in range(1,len(below_threshold_headers))],
                            font=dict(color=['#9E3039']+([headerFontColor]*header_len), size=14)
                            ),
                cells=dict(values=above_threshold_list,
                        fill_color=fillColorList,
                        font=dict(color=cellFontColor,size=12),
                        align='left'),
                        visible=True
                        ),
                row=2, col=1
            )

            fig.add_trace(
                go.Table(
                header=dict(values=above_threshold_headers,
                            fill_color=['white']+([headerBGcolor]*header_len),
                            align='left',
                            line_color=['#9E3039'],#+['white' for i in range(1,len(below_threshold_headers))],
                            font=dict(color=['#9E3039']+([headerFontColor]*header_len), size=14)
                            ),
                cells=dict(values=above_threshold_list14,
                        fill_color=fillColorList,
                        font=dict(color=cellFontColor,size=12),
                        align='left'),
                        visible=False
                        ),
                row=2, col=1
            )

        fig.write_html(f"plot_output/threshold_days_example_{country}.html")

        print("Finished plotting threshold data --- %s seconds ---" % (time.time() - start_time))


        ######################################## simulated dataset #######################################

        fig = go.Figure()

        fillColorList=create_fill_colors(threshold_days_list,rowEvenColor,rowOddColor)
        headers_simulated_cases_bold=[f'<b>{x} </b>' for x in simulated_cases_header]

        #Cases per 100k 7days
        fig.add_trace(
            go.Table(
            header=dict(values=headers_simulated_cases_bold,
                        fill_color=headerBGcolor,
                        align='left',
                        font=dict(color=headerFontColor, size=12)
                        ),
            cells=dict(values=simulated_casesPer100k_7d,
                    fill_color=fillColorList,
                    align='left'),
                    visible=True,
                    )

        )

        #Cases per 100k 14days
        fig.add_trace(
            go.Table(
            header=dict(values=headers_simulated_cases_bold,
                        fill_color=headerBGcolor,
                        align='left',
                        font=dict(color=headerFontColor, size=12)
                        ),
            cells=dict(values=simulated_casesPer100k_14d,
                    fill_color=fillColorList,
                    align='left'),
                    visible=False,
                    )
        )

        #Only new cases
        fig.add_trace(
            go.Table(
            header=dict(values=headers_simulated_cases_bold,
                        fill_color=headerBGcolor,
                        align='left',
                        font=dict(color=headerFontColor, size=12)
                        ),
            cells=dict(values=simulated_new_cases,
                    fill_color=fillColorList,
                    align='left'),
                    visible=False,
                    )

        )

        fig.update_layout(
            title=dict(
                text=f"<b> Corona statistics based on simulated new (daily) cases with assumed R-Values for {country_name} </b>",
                font=dict(
                    size=titleFontSize,
                    color=titleColor
                ),
                ),
            updatemenus=[
                dict(
                    active=0,
                    buttons=list([
                        dict(
                            label='Cases per 100k 7days',
                            method='update',
                            args=[{"visible":[True,False,False]}]
                        ),
                        dict(
                            label='Cases per 100k 14days',
                            method="update",
                            args=[{"visible":[False,True,False]}]
                        ),
                        dict(
                            label='New cases (daily)',
                            method="update",
                            args=[{"visible":[False,False,True]}]
                        )
                    ]),
                    x=0.97,
                    xanchor="right",
                    y=1.07,
                    yanchor="top"
                )
            ]
        )



        fig.write_html(f"plot_output/simulated_example_{country}.html")

        print("Finished plotting daily simulated data --- %s seconds ---" % (time.time() - start_time))
        print("DONE!")

    except Exception as e:
        logger.error(e) 
