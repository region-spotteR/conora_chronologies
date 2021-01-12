## Utility functions for Covid Research
import requests
import json
# import pandas as pd
import numpy as np
from loguru import logger
import sys
from collections import OrderedDict
from datetime import datetime, timedelta
import pathlib
import pickle

logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO")
logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level="ERROR")

def hello(name):
    print('HI THERE ' + name)

def calculate_smoothened_values(df,dateColName,caseColName,population,testColName=None):
    """
    Calculates smoothened covid case values by applying rolling averages and sums over 7 and 14 days. It also calculates an estimated r0 and new case per 100k for 7 and 14 days.
    If there is a daily test data it also calculates a test positive rate over 7 days.
    
    Parameters
    ----------
    df : DataFrame
        The dataframe
    dateColName : str
        The name of the date column
    caseColName : str
        The name of the new case column
    population : int
        The population of a country
    testColName : str, optional
        The name of the test column (default is None)

    Returns
    -------
    DataFrame
        a DataFrame with smoothened values over 7 and 14 day periods (rolling averages and sums; estimated r0 for 100k). If daily test data is available, 7 day positive test rate is included.
    """
    try:
        if testColName is None:  # Since some countries do not publish daily data on tests (looking at you Germany!) test values are only included for some 
            mini_df=df[[dateColName,caseColName]]
        else:
            mini_df=df[[dateColName,caseColName,testColName]]

        # Calculating 7 and 14 day rolling mean from mini_df for NEW CASES
        mini_df['New_Cases_7_Day_Mean'] = mini_df[caseColName].rolling(window=7).mean()
        mini_df['New_Cases_14_Day_Mean'] = mini_df[caseColName].rolling(window=14).mean()
        # Calculating 7 and 14 day rolling sum from mini_df for NEW CASES
        mini_df['New_Cases_7_Day_Sum'] = mini_df[caseColName].rolling(window=7).sum()
        mini_df['New_Cases_14_Day_Sum'] = mini_df[caseColName].rolling(window=14).sum()
        # Calculating estimated basic reproduction rate (r0)
        mini_df['Estimated_r0'] = (mini_df['New_Cases_7_Day_Sum'] + 5) / ((mini_df['New_Cases_14_Day_Sum'] - mini_df['New_Cases_7_Day_Sum']) + 5)
        # Calculate newcase per 100k for 7 and 14 days
        mini_df[['New_Cases_100K_7_Days', 'New_Cases_100K_14_Days']]=(mini_df[['New_Cases_7_Day_Sum', 'New_Cases_14_Day_Sum']] / population) * 100000

        if testColName is not None:                 # Since some countries do not publish daily data on tests (looking at you Germany!) I make this calculation optional 
            # Calculating 7 and 14 day rolling sum for TEST NUMBER
            mini_df['Tests_7_Day_Sum'] = mini_df[testColName].rolling(window=7).sum()
            mini_df['Tests_14_Day_Sum'] = mini_df[testColName].rolling(window=14).sum()
            # Calculating smoothened īpatsvars (positive tests)
            mini_df['Positive_rate_7_Day'] = (mini_df['New_Cases_7_Day_Sum'] / mini_df['Tests_7_Day_Sum']) * 100
        
        return mini_df
        

    except Exception as e:
        logger.error(e)

def calculate_smoothened_values_pandaless(population,list_of_cases,list_of_days,list_of_tests=None,reversed_dates=True):
    """
    Calculates smoothened covid case values by applying rolling averages and sums over 7 and 14 days. It also calculates an estimated r0 and new case per 100k for 7 and 14 days.
    If there is a daily test data it also calculates a test positive rate over 7 days.
    
    Parameters
    ----------
    population : int
        The population of a country
    list_of_cases : list
        A list sorted by date (chronologically) containing the daily new cases
    list_of_days : list
        A list sorted by date (chronologically) containing the dates of new cases
    list_of_tests : list, optional
        A list sorted by date (chronologically) containing the tests reported on that day
    reversed_dates : bool
        A boolean which is true if the result dictionary should be sorted from most current to oldest date. If False the dictionary is sorted from oldest to most current date.


    Returns
    -------
    list
        A list of columns containing numerical (smoothened) summary statistics
    list
        A second lists of strings containing the column names
    """
    try:
        New_Cases_7_Day_Sum=list(rolling_sum(list_of_cases))
        New_Cases_14_Day_Sum=list(rolling_sum(list_of_cases,interval=14))
        New_Cases_7_Day_Mean=list(map(lambda x: round(x/7,2) if x is not None else None,New_Cases_7_Day_Sum))
        New_Cases_14_Day_Mean=list(map(lambda x: round(x/14,2) if x is not None else None,New_Cases_14_Day_Sum))
        New_Cases_100K_7_Days=list(map(lambda x: round((x/population)*100000,2) if x is not None else None,New_Cases_7_Day_Sum))
        New_Cases_100K_14_Days=list(map(lambda x: round((x/population)*100000,2) if x is not None else None,New_Cases_14_Day_Sum))
        Estimated_R0=list(map(lambda x,y: calculateR(x,y),New_Cases_7_Day_Sum,New_Cases_14_Day_Sum))

        if list_of_tests is not None:                # Since some countries do not publish daily data on tests (looking at you Germany!) I make this calculation optional 
            # Calculating 7 and 14 day rolling sum for TEST NUMBER
            Tests_7_Day_Sum=list(rolling_sum(list_of_tests))
            Tests_14_Day_Sum=list(rolling_sum(list_of_tests,interval=14))
            # Calculating smoothened īpatsvars (positive tests)
            Positive_rate_7_Days=list(map(lambda x,y: calculateTestPositivity(x,y),New_Cases_7_Day_Sum,Tests_7_Day_Sum))
            Positive_rate_daily=list(map(lambda x,y: calculateTestPositivity(x,y),list_of_cases,list_of_tests))

            result=[list_of_days,list_of_cases,list_of_tests,Positive_rate_daily,Estimated_R0,Positive_rate_7_Days,            New_Cases_7_Day_Mean,New_Cases_100K_7_Days,New_Cases_7_Day_Sum,Tests_7_Day_Sum,New_Cases_14_Day_Mean,New_Cases_100K_14_Days,New_Cases_14_Day_Sum,Tests_14_Day_Sum]
            header_names=['Date','New Cases','Tests administered','Positive Rate','R (estimate)','Positive Rate 7d','7d mean','Cases100k_7days','Cases Sum 7d','Tests Sum 7d','14d mean','Cases100k_14days','Cases Sum 14d','Tests Sum 14d']
        else:
            result=[list_of_days,list_of_cases,Estimated_R0,New_Cases_7_Day_Mean,New_Cases_100K_7_Days,New_Cases_7_Day_Sum,New_Cases_14_Day_Mean,New_Cases_100K_14_Days,New_Cases_14_Day_Sum]
            header_names=['Date','New Cases','R (estimate)','7d mean','Cases100k_7days','Cases Sum 7d','14d mean','Cases100k_14days','Cases Sum 14d']

        
        return result, header_names
        

    except Exception as e:
        logger.error(e)

def calculateTestPositivity(new_cases,new_tests):
    """
    Calculates how many tests where positive

    Parameters
    ----------
    new_cases : int
        An integer containing amount of (new) cases
    new_tests : int
        An integer containing amount of (new) tests

    Returns
    -------
    float
        A percentage
    """
    try:
        if new_cases is None or new_tests is None:
            return None
        else:
            return round(((new_cases/new_tests))*100,2)

    except Exception as e:
        logger.error(e)


def calculateR(last7days_cases,last14days_cases,constant_int=5):
    """
    Calculates the R value over 7 days. Therefore it needs 14 days of data

    Parameters
    ----------
    last7days_cases : int
        An integer containing the sum of the cases in the last 7 days
    last14days_cases : int
        An integer containing the sum of the cases in the last 14 days
    constant_int : int, optional
        An integer which keep the R-value from becoming infinity because it has been divided by zero

    Returns
    -------
    float
        A R_0 value
    """
    try:
        if last7days_cases is None or last14days_cases is None:
            return None
        else:
            last_week_7days_Sum=last14days_cases-last7days_cases
            return round((last7days_cases+constant_int)/(last_week_7days_Sum+constant_int),2)

    except Exception as e:
        logger.error(e)

def simulate_new_cases(R_range,current_number,population,window_length=56):
    """
    Simulates daily new cases (in general and per 100k) according to a specified range of R; adds Date column
    
    Parameters
    ----------
    R_range : list
        A list of floats representing the range of R
    current_number : int
        The current number of new cases
    population : int
        The population of a country
    window_length : int
        The amount of days to forecast (default is 56)

    Returns
    -------
    DataFrame
        a DataFrame with daily new cases (in general and per 100k) according to a specified range of R. For cases per 100k also shows 7 and 14 day periods. Adds Date column starting from the current date
    """
    try:
        Rs_dict={}
        colName7=[]
        colName14=[]
        for R_s in R_range:
            step_value=(R_s-1)/7
            colName7.append('per100k_7d_R'+str(R_s))
            colName14.append('per100k_14d_R'+str(R_s))
            Rs_dict['new_R'+str(R_s)]=np.arange(start=1,stop=1+(step_value*window_length),step=step_value)

        #simulated_cases.rolling(window=7).sum()/population*100000 # 7-day 100k
        newdf=pd.DataFrame.from_dict(Rs_dict)*current_number #959.200000 #14days #1002.800000 # 21days
        newdf7=newdf.rolling(window=7).sum()/population*100000
        newdf14=newdf.rolling(window=14).sum()/population*100000
        newdf7.columns=colName7
        newdf14.columns=colName14

        days = pd.Series(pd.date_range(start='today', periods=window_length, freq='D').map(lambda t: t.strftime('%Y-%m-%d')),name='Date')
        return pd.concat([days,newdf.reset_index(drop=True),newdf7.reset_index(drop=True), newdf14], axis=1)

    except Exception as e:
        logger.error(e)

def simulate_new_cases_pandaless(R_range,new_cases_avg,population,window_length=56):
    """
    Simulates daily new cases (in general and per 100k) according to a specified range of R; adds Date column
    
    Parameters
    ----------
    R_range : list
        A list of floats representing the range of R
    new_cases_avg : int
        The current number of new cases
    population : int
        The population of a country
    window_length : int
        The amount of days to forecast (default is 56)

    Returns
    -------
    list
        A list of simulated new cases for each day
    list
        A list of the cases per 100k KPI for 7 days
    list
        A list of the cases per 100k KPI for 14 days
    """
    try:
        # create range of dates and insert it at the beginning of the list
        base = datetime.today()
        date_list = [base + timedelta(days=x) for x in range(window_length)]

        new_cases_list=[date_list]
        casesPer100k_7d_list=[date_list]
        casesPer100k_14d_list=[date_list]
        for R_s in R_range:
            step_value=(R_s-1)/7
            new_cases=np.arange(start=1,stop=1+(step_value*window_length),step=step_value)*new_cases_avg
            New_Cases_7_Day_Sum=rolling_sum(new_cases,interval=7)
            New_Cases_14_Day_Sum=rolling_sum(new_cases,interval=14)
            FC_cases_per100k_7d=list(map(lambda x: round((x/population)*100000,2) if x is not None else None,New_Cases_7_Day_Sum))
            FC_cases_per100k_14d=list(map(lambda x: round((x/population)*100000,2) if x is not None else None,New_Cases_14_Day_Sum))        
            new_cases_list.append(list(np.round(new_cases,2)))
            casesPer100k_7d_list.append(FC_cases_per100k_7d)
            casesPer100k_14d_list.append(FC_cases_per100k_14d)

        return new_cases_list, casesPer100k_7d_list, casesPer100k_14d_list

    except Exception as e:
        logger.error(e)


def simulate_threshold_dates(R_range,new_cases_avg,population,thresholds=[10,20,50,100,200,400,600,800,1000],window_length=1000,sum7=True):
    """
    Simulates daily new cases (in general and per 100k) according to a specified range of R and calculates after how many days under an assumed R_0 a threshold is reached.
    
    Parameters
    ----------
    R_range : list
        A list of floats representing the range of R
    current_number : int
        The current number of new cases
    population : int
        The population of a country
    thresholds : list
        A list of integers representing the threshold which R has to go above or below
    window_length : int
        An integer telling the function how far into the future it shall look. Default is 1000 days
    sum7 : bool
        A boolean telling the function if we want the cases per 100k for 7 or for 14 days. Default is True which results in results for cases per 100k for 7 days
    
    Returns
    -------
    List
        A nested list, where the first element is the R_range. All the other lists contain days when the threshold is reached. The second element is showing the values for the first threshold (defaults  to 10) and the third element shows the results for the second threshold given (defaults to 20) etc. pp
    """
    try:

        # Task: Create this logic in jupyter notebooks
        if sum7:
            interval=7
        else:
            interval=14

        R_dict={}

        
        for R_s in R_range:
            ### FC_cases_per100k function
            step_value=(R_s-1)/7
            new_cases=np.arange(start=1,stop=1+(step_value*window_length),step=step_value)*new_cases_avg # verify if this works
            New_Cases_Sum=rolling_sum(new_cases,interval=interval,reversed_dates=False)
            FC_cases_per100k=list(map(lambda x: (x/population)*100000 if x is not None else None,New_Cases_Sum)) # for sum7=False we need rolling_sum(new_cases,interval=14)         
            R_dict[R_s]=FC_cases_per100k   

        result_list=[R_range]
        for th in thresholds:
            threshold_days=list(map(lambda R_s: verify_threshold(R_dict[R_s],th,interval=interval),R_range))
            result_list.append(threshold_days)
            
        return result_list


                # ### verify threshold function
               
                # if th<FC_cases_per100k[0]:
                #     index_threshold=np.flatnonzero(FC_cases_per100k<th)
                # else:
                #     index_threshold=np.flatnonzero(FC_cases_per100k>th)
                
                # if index_threshold.size!=0:
                #     threshold_days.append(index_threshold[0]+interval)
                # else:
                #     threshold_days.append(np.nan)



    except Exception as e:
        logger.error(e)


def verify_threshold(simulated_cases_per100k,threshold,interval=7,returnDates=False):
    """
    Subfunction of simulate_threshold_dates.  Calculates after how many days a threshold is reached

    Parameters
    ----------
    FC_cases_per100k : list
        The list of cases per 100k, based on simulated daily new covid infections using an assumed R_0
    threshold : int
        An integer indicating which thresholds needs to be reached
    interval : int
        An integer specifying 7 if we base our calculation of cases per 100k on a 7-day period
        
    Returns
    -------
    integer or nan
        An integer of how many days it takes to reach that threshold or nan if the threshold can't be reached
    """
    try:
        FC_cases_per100k=simulated_cases_per100k[interval:]
        if threshold<FC_cases_per100k[0]:
            index_threshold=next((x[0] for x in enumerate(FC_cases_per100k) if x[1] < threshold),None)
        else:
            index_threshold=next((x[0] for x in enumerate(FC_cases_per100k) if x[1] > threshold),None)
        
        if index_threshold is not None:
            if returnDates:
                return index_threshold+interval
            else:
                days_till_threshold=index_threshold+interval
                threshold_date = datetime.today()+timedelta(days=days_till_threshold)
                return(threshold_date)

        else:
            return None

         
    except Exception as e:
        logger.error(e)

def rolling_sum(list_of_cases,interval=7,reversed_dates=True):
    """
    Calculates the rolling sum over a specified interval

    Parameters
    ----------
    list of cases : list
        The list of cases
    interval : int
        An integer indicating over which period the rolling sum should be taken
    reversed_dates : bool
        A boolean which is true if the result dictionary should be sorted from most current to oldest date. If False the dictionary is sorted from oldest to most current date.


    Returns
    -------
    list
        A list of rolling sums. Be aware that this list is exactly the `interval` amount shorter than `list_of_cases`
    """
    try:
        cumulated_sum=np.cumsum(list_of_cases,dtype=int)
        rolling_sum=list(cumulated_sum[interval:]-cumulated_sum[:-interval])
        if reversed_dates:
            emptyItems=list(np.repeat(None,interval))
            rolling_sum.extend(emptyItems)
            return rolling_sum
        else:
            result=list(np.repeat(None,interval))
            result.extend(rolling_sum)
            return result

    except Exception as e:
        logger.error(e)


############################################## this should go in a seperate load_data.py ##################

# there is still post request here!
def download_covid_data(url,country='lv'):
    """
    Downloads covid data from a url and returns a status code if the download fails. Of course for Germany the data extraction is a bit more complicated

    Parameters
    ----------
    url : string
        The request url
    country : string
        The country code (default is 'lv')

    Returns
    -------
    DataFrame
        a DataFrame with raw data
    """
    try:
        if country=='lv':
            response=requests.post(url)
        else:
            response=requests.get(url)
        if response.status_code==200:
            resp_dict=json.loads(response.content)
            if country=='lv':
                raw_df=pd.json_normalize(resp_dict.get('result').get('records'))
            else:
                rawdata=pd.json_normalize(resp_dict.get('features'))
                raw_df=rawdata[rawdata['properties.AnzahlFall']>-1].groupby(by=['properties.Meldedatum'])['properties.AnzahlFall'].sum().reset_index()
            
            return raw_df

        else:
            logger.error(f'Get request failed with HTTP status code: {response.status_code}')

    except Exception as e:
        logger.error(e)


def cache_dict(obj, name ):
    with open('download_cache/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_cached_dict(name ):
    with open('download_cache/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)


def verify_cache_existence():
    """
    Compares the cache file date with the current date and returns a boolean
    
    Returns
    -------
    Bool
        A boolean. True if the current data is up to date, False otherwise
    """
    try:
        fname = pathlib.Path('download_cache/cases_lv.pkl')
        if fname.exists():
            mtime = datetime.fromtimestamp(fname.stat().st_mtime)
            return datetime.today().date()<=mtime.date()
        else:
            logger.info(f'No cache file with the name: {fname}. It will be created')
            return False

    except Exception as e:
        logger.error(e)


## create separate download covid data functions for LV and DE

def download_lv_covid_data(url,reversed_dates=True):
    """
    Downloads covid data from a url and returns a status code if the download fails.

    Parameters
    ----------
    url : string
        The request url
    reversed_dates : bool
        A boolean which is true if the result dictionary should be sorted from most current to oldest date. If False the dictionary is sorted from oldest to most current date.

    Returns
    -------
    List
        A list with new daily cases in chronological order from oldest to most current date
    List
        A list with the amount of covid tests in chronological order from oldest to most current date
    """

    try:
        if verify_cache_existence():
            cases_dict=load_cached_dict('cases_lv')
            tests_dict=load_cached_dict('tests_lv')
            return cases_dict, tests_dict
        else:
            response = requests.get(url)
            if response.status_code==200:
                resp_dict=json.loads(response.content)
                original_list=resp_dict.get('result').get('records')
                cases_dict={}
                tests_dict={}
                if reversed_dates:
                    loop_range=range(len(original_list)-1,-1,-1)
                else:
                    loop_range=range(0,len(original_list))

                for i in loop_range:
                    item=original_list[i]
                    current_date=item['Datums']
                    new_cases=int(item['ApstiprinataCOVID19InfekcijaSkaits'])
                    new_tests=int(item['TestuSkaits'])
                    cases_dict[current_date]=new_cases
                    tests_dict[current_date]=new_tests            
                
                # caching the data and then returning it
                cache_dict(cases_dict,'cases_lv')
                cache_dict(tests_dict,'tests_lv')
                return cases_dict, tests_dict

            else:
                logger.error(f'Get request failed with HTTP status code: {response.status_code}')

    except Exception as e:
        logger.error(e)


def download_de_covid_data(url):
    """
    Downloads covid data from a url and returns a status code if the download fails.

    Parameters
    ----------
    url : string
        The request url

    Returns
    -------
    DataFrame
        a DataFrame with raw data
    """

    try:
        response=requests.get(url)
        if response.status_code==200:
            resp_dict=json.loads(response.content)
            rawdata=pd.json_normalize(resp_dict.get('features'))
            raw_df=rawdata[rawdata['properties.AnzahlFall']>-1].groupby(by=['properties.Meldedatum'])['properties.AnzahlFall'].sum().reset_index()
            return raw_df

        else:
            logger.error(f'Get request failed with HTTP status code: {response.status_code}')

    except Exception as e:
        logger.error(e)

def download_de_covid_data_pandaless(url,reversed_dates=True):
    """
    Downloads covid data from a url and returns a status code if the download fails. Is way faster since it doesn't use pandas

    Parameters
    ----------
    url : string
        The request url
    reversed_dates : bool
        A boolean which is true if the result dictionary should be sorted from most current to oldest date. If False the dictionary is sorted from oldest to most current date.

    Returns
    -------
    dict
        A sorted dictionary with the Dates as key and the new Cases as values. Runs way faster than in pandas
    """

    try:
        if verify_cache_existence():
            cases_dict=load_cached_dict('cases_de')
            return cases_dict
        else:

            response=requests.get(url)
            if response.status_code==200:
                resp_dict=json.loads(response.content)

                original_list=resp_dict['features']
                day_dict = {}
                for elem in original_list:
                    item=elem['properties']
                    current_date=item['Meldedatum']
                    if current_date not in day_dict:
                        day_dict[current_date]=item['AnzahlFall']
                    else:
                        day_dict[current_date]+=item['AnzahlFall'] # Summing up the data

                day_dict_sorted=OrderedDict()
                for key in sorted(day_dict.keys(),reverse=reversed_dates):
                    day_dict_sorted[key]=day_dict[key]

                # caching the data and then returning it
                cache_dict(cases_dict,'cases_lv')                
                return day_dict_sorted

            else:
                logger.error(f'Get request failed with HTTP status code: {response.status_code}')

    except Exception as e:
        logger.error(e)