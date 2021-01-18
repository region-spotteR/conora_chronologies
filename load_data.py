import requests
import json
from loguru import logger
import sys
from collections import OrderedDict
from datetime import datetime, timedelta
import pathlib
import pickle

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

def download_covid_data(url,country,contains_tests=False,reversed_dates=True):
    """
    Downloads covid data from a url and returns a status code if the download fails.

    Parameters
    ----------
    url : string
        The request url
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
            tests_dict=load_cached_dict(f'tests_{country}') if contains_tests else None       
            return cases_dict, tests_dict
        else:
            response = requests.get(url)
            if response.status_code==200:
                resp_dict=json.loads(response.content)

                if country=='lv':
                    cases_dict, tests_dict=data_preparation_lv(resp_dict,reversed_dates=reversed_dates)
                elif country=='de':
                    cases_dict=data_preparation_de(resp_dict,reversed_dates=reversed_dates)
                    tests_dict=None
                else:
                    logger.error(f'No data preparation method for country {country} available')
                    
                # caching the data and then returning it
                cache_dict(cases_dict,f'cases_{country}')
                cache_dict(tests_dict,f'tests_{country}') if contains_tests else None
                return cases_dict, tests_dict

            else:
                logger.error(f'Get request failed with HTTP status code: {response.status_code}')

    except Exception as e:
        logger.error(e)

def data_preparation_lv(response_dict,reversed_dates=True):
    """
    Creates an sorted dictionary of dates, new cases and tests for the latvian Covid data

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


def data_preparation_de(response_dict,reversed_dates=True):
    """
    Creates an sorted dictionary of dates, new cases and tests for the latvian Covid data

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
            current_date=item['Meldedatum'].split(' ')[0].replace('/','-')
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
