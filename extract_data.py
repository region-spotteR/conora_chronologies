from logging import raiseExceptions
import requests
import csv
import json
from loguru import logger
import sys
from collections import OrderedDict
from datetime import datetime, timedelta
import pathlib
import pickle
import urllib3


logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO")
logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level="ERROR")

def cache_dict(obj, name ):
    with open('download_cache/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_cached_dict(name ):
    with open('download_cache/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)


def verify_cache_existence(country):
    """
    Compares the cache file date with the current date and returns a boolean
    
    Parameters
    ----------
    country : str
        A two letter color code for a country e.g. 'de' for Germany

    Returns
    -------
    Bool
        A boolean. True if the current data is up to date, False otherwise
    """
    try:
        fname = pathlib.Path(f'download_cache/cases_{country}.pkl')
        if fname.exists():
            mtime = datetime.fromtimestamp(fname.stat().st_mtime)
            return datetime.today().date()<=mtime.date()
        else:
            logger.info(f'No cache file with the name: {fname}. It will be created')
            return False

    except Exception as e:
        logger.error(e)


## create separate download covid data functions for LV and DE

def download_covid_data(country_attributes,country,reversed_dates=True):
    """
    Loads covid data from cache if it already exists and otherwise triggers the download and the data cleaning (or standardisation) process

    Parameters
    ----------
    country_attributes : dict
        A dictionary containing country attributes
    country : str
        A two letter color code for a country e.g. 'de' for Germany
    reversed_dates : bool
        A boolean which is true if the result dictionary should be sorted from most current to oldest date. If False the dictionary is sorted from oldest to most current date.


    Returns
    -------
    dict
        A dictionary of lists with the keys Date, `New Cases` and Tests (if there is any test data).
    """

    try:
        if verify_cache_existence(country):
            cases_dict=load_cached_dict(f'cases_{country}')
            tests_dict=load_cached_dict(f'tests_{country}') if country_attributes.contains_tests else None       
            return cases_dict, tests_dict
        else:
            result= retrieve_data(country_attributes,country_attributes.url)

            if country=='de':
                cases_dict=data_preparation_de(result,reversed_dates=reversed_dates)
                tests_dict=None
            elif country=='fr':
                cases_dict, tests_dict=data_preparation_fr(result,reversed_dates=reversed_dates)
            elif country=='at':
                cases_dict=data_preparation_at(result,reversed_dates=reversed_dates)
                tests_dict=None
            elif country=='be':
                cases_dict, tests_dict=data_preparation_be(result,reversed_dates=reversed_dates)
            elif country=='lv':
                cases_dict, tests_dict=data_preparation_lv(result,reversed_dates=reversed_dates)
            else:
                logger.error(f'No data preparation method for country {country} available')
                
            # caching the data and then returning it
            cache_dict(cases_dict,f'cases_{country}')
            cache_dict(tests_dict,f'tests_{country}') if country_attributes.contains_tests else None
            return cases_dict, tests_dict


    except Exception as e:
        logger.error(e)

def retrieve_data(country_attributes,url):
    """
    Downloads covid data from a url and returns a status code if the download fails.

    Parameters
    ----------
    country_attributes : dict
        A dictionary containing country attributes
    url : str
        A string containing the url. This is used to make the function more generic



    Returns
    -------
    ? : ? 
        A list if a csv is downloaded and a dictionary if a json is downloaded
    """
    try: 
         ## lowing the ssl secure level for Austria - #facepalm. Austrian server apparently uses SSL security level 1 while others use level 2
        if country_attributes.country_name=="Austria":       
            requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL:@SECLEVEL=1'
                
        response = requests.get(url)
        if response.status_code==200:
            if country_attributes.csv:
                return load_csv(response.content,country_attributes.csv_separator,country_attributes.csv_encoding)
            else:
                return json.loads(response.content)
        else:
            logger.error(f'Get request failed with HTTP status code: {response.status_code}')

    except Exception as e:
        logger.error(e)

    

def load_csv(content,sep,encoding):
    """
    Transforms response content into a row wise list

    Parameter
    ---------
    content : bytes
        Bytes containing the csv
    sep : str
        The csv separator
    encoding : str
        The csv encoding

    Returns
    -------
    list : list
        A list containing each row of the csv
    """ 
    try:
        decoded_file=content.decode(encoding)
        cr = csv.reader(decoded_file.splitlines(), delimiter=sep)
        return list(cr)

    except Exception as e:
        logger.error(e)

def data_preparation_de(response_dict,reversed_dates=True):
    """
    Creates an sorted dictionary of dates, new cases and tests for the German Covid-19 data

    Parameters
    ----------
    response_dict : dict
        The raw response from the url as dictionary
    reversed_dates : bool
        A boolean which is true if the result dictionary should be sorted from most current to oldest date. If False the dictionary is sorted from oldest to most current date.

    Returns
    -------
    dict
        A dictionary of lists with the keys Date, `New Cases` and Tests (if there is any test data).
    """
    try:
        original_list=response_dict['features']
        day_dict = {}
        for elem in original_list:
            item=elem['properties']
            current_date=item['Meldedatum'].split('T')[0].replace('/','-')
            if current_date not in day_dict:
                day_dict[current_date]=item['AnzahlFall']
            else:
                day_dict[current_date]+=item['AnzahlFall'] # Summing up the data

        day_dict_sorted=OrderedDict()
        for key in sorted(day_dict.keys(),reverse=reversed_dates):
            day_dict_sorted[key]=day_dict[key]

        return day_dict_sorted

    except Exception as e:
        logger.error(e)

def data_preparation_fr(response_list,reversed_dates=True):
    """
    Creates an sorted dictionary of dates, new cases and tests for the French Covid-19 data

    Parameters
    ----------
    response_list : list
        A list with each item corresponding to a csv row
    reversed_dates : bool
        A boolean which is true if the result dictionary should be sorted from most current to oldest date. If False the dictionary is sorted from oldest to most current date.

    Returns
    -------
    dict
        A dictionary of lists with the keys Date, `New Cases` and Tests (if there is any test data).
    """
    try:
        column_names=response_list[0]
        date_ix=column_names.index('date')
        cases_ix=column_names.index('pos')
        rate_ix=column_names.index('tx_pos')
        cases_dict={}
        tests_dict={}

        my_iterator=range(1,len(response_list))
        if reversed_dates:
            my_iterator=reversed(my_iterator)

        for i in my_iterator:
            if response_list[i][cases_ix] is None or len(response_list[i][rate_ix])==0:
                next
            else:
                cases=int(response_list[i][cases_ix])
                rate=float(response_list[i][rate_ix])/100
                date=response_list[i][date_ix]
                estimated_tests=int(round(cases/rate))
                cases_dict[date]=cases
                tests_dict[date]=estimated_tests

        return cases_dict, tests_dict

    except Exception as e:
        logger.error(e)

def data_preparation_at(response_list,reversed_dates=True):
    """
    Creates an sorted dictionary of dates, new cases and tests for the Austrian Covid-19 data

    Parameters
    ----------
    response_dict : dict
        The raw response from the url as dictionary
    reversed_dates : bool
        A boolean which is true if the result dictionary should be sorted from most current to oldest date. If False the dictionary is sorted from oldest to most current date.

    Returns
    -------
    dict
        A dictionary of lists with the keys Date, `New Cases` and Tests (if there is any test data).
    """
    try:       
        # load the second csv 
        column_names=response_list[0]
        date_ix=0
        cases_ix=column_names.index('AnzahlFaelle')
        cases_dict={}
        # tests_dict2={} #not needed
        my_iterator=range(1,len(response_list))
        if reversed_dates:
            my_iterator=reversed(my_iterator)

        for i in my_iterator:
            date=datetime.strptime(response_list[i][date_ix],'%d.%m.%Y %H:%M:%S')
            if response_list[i][1]!="Österreich":
                next
            else:
                date_str=datetime.date(date).isoformat()
                cases=int(response_list[i][cases_ix])
                cases_dict[date_str]=cases  
                
        return cases_dict

    except Exception as e:
        logger.error(e)

def data_preparation_be(response_dict,reversed_dates=True):
    """
    Creates an sorted dictionary of dates, new cases and tests for the Belgian Covid-19 data

    Parameters
    ----------
    response_dict : dict
        The raw response from the url as dictionary
    reversed_dates : bool
        A boolean which is true if the result dictionary should be sorted from most current to oldest date. If False the dictionary is sorted from oldest to most current date.

    Returns
    -------
    dict
        A dictionary of lists with the keys Date, `New Cases` and Tests (if there is any test data).
    """
    try:       
        cases_dict={}
        tests_dict={}

        my_iterator=range(1,len(response_dict))
        if reversed_dates:
            my_iterator=reversed(my_iterator)

        for i in my_iterator:
            current_date=response_dict[i].get('DATE')
            #if current_date is not None: # there is some none types at the end of the JSON
            if current_date not in cases_dict:
                cases_dict[current_date]=response_dict[i]['TESTS_ALL_POS']
                tests_dict[current_date]=response_dict[i]['TESTS_ALL']
            else:
                cases_dict[current_date]+=response_dict[i]['TESTS_ALL_POS'] # Summing up the data
                tests_dict[current_date]+=response_dict[i]['TESTS_ALL'] # Summing up the data

        reversed_dates=True
        cases_dict_sorted=OrderedDict()
        tests_dict_sorted=OrderedDict()
        for key in sorted(cases_dict.keys(),reverse=reversed_dates):
            cases_dict_sorted[key]=cases_dict[key]
            tests_dict_sorted[key]=tests_dict[key]
                
        return cases_dict_sorted, tests_dict_sorted

    except Exception as e:
        logger.error(e)




def data_preparation_lv(response_dict,reversed_dates=True):
    """
    Creates an sorted dictionary of dates, new cases and tests for the Latvian Covid-19 data

    Parameters
    ----------
    response_dict : dict
        The raw response from the url as dictionary
    reversed_dates : bool
        A boolean which is true if the result dictionary should be sorted from most current to oldest date. If False the dictionary is sorted from oldest to most current date.

    Returns
    -------
    dict
        A dictionary of lists with the keys Date, `New Cases` and Tests (if there is any test data).
    """
    try:
        original_list=response_dict.get('result').get('records')

        if reversed_dates:
            loop_range=range(len(original_list)-1,-1,-1)
        else:
            loop_range=range(0,len(original_list))

        cases_dict={}
        tests_dict={}
        for i in loop_range:
            item=original_list[i]
            current_date=item['Datums'].split('T')[0]
            new_cases=int(item['ApstiprinataCOVID19InfekcijaSkaits'])
            new_tests=int(item['TestuSkaits'])
            cases_dict[current_date]=new_cases
            tests_dict[current_date]=new_tests       

        return cases_dict, tests_dict

    except Exception as e:
        logger.error(e)



