import sys
from loguru import logger
import time

from country_settings import get_attributes
from extract_data import download_covid_data
from transform_enrich import history, simulate

from visuals_plotly import visuals
from visuals_tabulator import historical_table

logger.add(sys.stderr, format="{time} {level} {message}", filter="main", level="INFO")
logger.add(sys.stderr, format="{time} {level} {message}", filter="main", level="ERROR")

def main():

    # 0.1 Define Country 
    if len(sys.argv)==1:
        country='fr'    
    else: 
        country=sys.argv[1]
        
        # Current choices 'de' or 'lv'
        # data=data(country)
        # data.load(country)

    ## 1.1. Load data from the API
    # former prepare self=data

    # 1.1.1 Assign downloaded data to dictionaries
    start_time = time.time()
    attr = get_attributes(country)
    cases_dict, tests_dict=download_covid_data(attr,country)
    daily={'Date': list(cases_dict.keys()),'New Cases': list(cases_dict.values())}
    daily['Tests']=list(tests_dict.values()) if attr.contains_tests else None

    logger.info("Extract: Data extracted in --- %s seconds ---" % (time.time() - start_time))

    ## 1.2. Enrich data from the API

    # 1.2.2 Create dictionaries with historic data
    from_young_to_old_dates=True
    historical_data=history()
    history.calculate_values(historical_data,attr.population,daily,reversed_dates=from_young_to_old_dates)
    logger.info("Transform: Created historical calculations  --- %s seconds ---" % (time.time() - start_time))

    if from_young_to_old_dates:
        new_cases_avg=historical_data.data[historical_data.headers.index('7d mean')][0]
        new_cases_14d_avg=new_cases_avg=historical_data.data[historical_data.headers.index('14d mean')][0]
    else:
        mean7d=historical_data.data[historical_data.headers.index('7d mean')]
        mean14d=historical_data.data[historical_data.headers.index('14d mean')]
        new_cases_avg=mean7d[len(mean7d)-1]
        new_cases_14d_avg=mean14d[len(mean14d)-1]

    # 1.2.3 Create dictionaries with simulated data (simulating the future)
    simulated=simulate(new_cases_avg,attr.population,new_cases_assumed14=new_cases_14d_avg)
    simulated.simulate_new_cases()
    simulated.create_th_values()
    logger.info("Transform: Data is prepared - starting to write to html --- %s seconds ---" % (time.time() - start_time))


    ## 1.3. Create tables
    # 1.3.1 Create historical table
    history_dict_list=historical_table.create_dicts(historical_data)
    history_columns=historical_table.create_history_columns(historical_data.headers7)
    historical_table.write_tabulator(history_dict_list,history_columns,country)

    # 1.3.2 create threshold and other data
    plots_obj=visuals(attr)
    historical_data.data
    plots_obj.plot_threshold(simulated,country)

    logger.info("Done writing html-files --- %s seconds ---" % (time.time() - start_time))

    # 2. Epilog: How to use deprecated code

    # from deprecated.old_visuals import old_visuals
    # depricated=old_visuals(attr) 
    # depricated.plot_smoothened(historical_data,country) # deprecated - Tabulator is better
    # depricated.plot_timeline(historical_data,country) # Needs to be adapted - Timeline make sense if different countries regions are compared by the same KPI

if __name__== "__main__":
    main()