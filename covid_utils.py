## Utility functions for Covid Research
import bisect # for estimating dates for covid cases thresholds are reached
import requests
import json
import pandas as pd
import numpy as np
from loguru import logger
import sys
from collections import OrderedDict

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

        # return pd.concat([newdf.reset_index(drop=True),newdf7.reset_index(drop=True), newdf14], axis=1)
        
        #return pd.concat([newdf.reset_index(drop=True),newdf7.reset_index(drop=True), newdf14], axis=1).insert(0, 'Date', pd.date_range(start='today', periods=window_length, freq='D').map(lambda t: t.strftime('%Y-%m-%d')),inplace=True)
        days = pd.Series(pd.date_range(start='today', periods=window_length, freq='D').map(lambda t: t.strftime('%Y-%m-%d')),name='Date')
        return pd.concat([days,newdf.reset_index(drop=True),newdf7.reset_index(drop=True), newdf14], axis=1)

        # simulated_df = pd.concat([newdf.reset_index(drop=True),newdf7.reset_index(drop=True), newdf14], axis=1)
        # Add Date column
        # simulated_df = simulated_df.insert(0, 'Date', pd.date_range(start='today', periods=len(simulated_df), freq='D').map(lambda t: t.strftime('%Y-%m-%d')))
        # return simulated_df.insert(0, 'Date', pd.date_range(start='today', periods=len(simulated_df), freq='D').map(lambda t: t.strftime('%Y-%m-%d')))
        # return simulated_df


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
            FC_cases_per100k=rolling_sum(new_cases,interval=interval)/population*100000 # for sum7=False we need rolling_sum(new_cases,interval=14)         
            R_dict[R_s]=FC_cases_per100k   

        result_list=[R_range]
        for th in thresholds:
            threshold_days=[]
            test=list(map(lambda R_s: verify_threshold(R_dict[R_s],th,interval=interval),R_range))
            threshold_days.append(test)
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


def verify_threshold(FC_cases_per100k,threshold,interval=7):
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
        if threshold<FC_cases_per100k[0]:
            index_threshold=np.flatnonzero(FC_cases_per100k<threshold)
        else:
            index_threshold=np.flatnonzero(FC_cases_per100k>threshold)
        
        if index_threshold.size!=0:
            return index_threshold[0]+interval
        else:
            return np.nan

         
    except Exception as e:
        logger.error(e)

def rolling_sum(list_of_cases,interval=7):
    """
    Calculates the rolling sum over a specified interval

    Parameters
    ----------
    list of cases : list
        The list of cases
    interval : int
        An integer indicating over which period the rolling sum should be taken

    Returns
    -------
    list
        A list of rolling sums. Be aware that this list is exactly the `interval` amount shorter than `list_of_cases`
    """
    try:
        cumulated_sum=np.cumsum(list_of_cases,dtype=float)
        rolling_sum=cumulated_sum[interval:]-cumulated_sum[:-interval]
        return rolling_sum

    except Exception as e:
        logger.error(e)



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
            logger.error(f'Get request failed with HTTP status code: {response.status_code}'}

    except Exception as e:
        logger.error(e)



## create separate download covid data functions for LV and DE

def download_lv_covid_data(url):
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
        response = requests.get(url)
        if response.status_code==200:
            resp_dict=json.loads(response.content)
            raw_df=pd.json_normalize(resp_dict.get('result').get('records'))
            return raw_df

        else:
            logger.error(f'Get request failed with HTTP status code: {response.status_code}'}

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
            logger.error(f'Get request failed with HTTP status code: {response.status_code}'}

    except Exception as e:
        logger.error(e)

def download_de_covid_data_pandaless(url):
    """
    Downloads covid data from a url and returns a status code if the download fails. Is way faster since it doesn't use pandas

    Parameters
    ----------
    url : string
        The request url

    Returns
    -------
    dict
        A sorted dictionary with the Dates as key and the new Cases as values. Runs way faster than in pandas
    """

    try:
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
            for key in sorted(day_dict.keys()):
                day_dict_sorted[key]=day_dict[key]

            return day_dict_sorted

        else:
            logger.error(f'Get request failed with HTTP status code: {response.status_code}'}

    except Exception as e:
        logger.error(e)