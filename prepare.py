from country_settings import get_attributes
from load_data import download_covid_data
from enrich import smoothened, simulate

import sys
from loguru import logger
import time

logger.add(sys.stderr, format="{time} {level} {message}", filter="prepare", level="INFO")
logger.add(sys.stderr, format="{time} {level} {message}", filter="prepare", level="ERROR")

class data:
    def __init__(self,country):
        self.attr = get_attributes(country)
        # self.CasesPer100k_thresholds=[10,20,50,100,200,400,600,800,1000]
        # self.Range_for_R=[0.8,0.85,0.9,0.95,1.05,1.1,1.15,1.2]

    def load(self,country):
        try:
            start_time = time.time()
            cases_dict, tests_dict=download_covid_data(self.attr.url,country,self.attr.url_contains_tests)
            self.daily={'Date': list(cases_dict.keys()),'New Cases': list(cases_dict.values())}
            self.daily['Tests']=list(tests_dict.values()) if self.attr.url_contains_tests else None

            logger.info("Data loaded in --- %s seconds ---" % (time.time() - start_time))
            
            from_young_to_old_dates=True
            self.smooth=smoothened()
            smoothened.calculate_values(self.smooth,self.attr.population,self.daily,reversed_dates=from_young_to_old_dates)
            logger.info("Finished creating smoothened data --- %s seconds ---" % (time.time() - start_time))

            if from_young_to_old_dates:
                new_cases_avg=self.smooth.data[self.smooth.headers.index('7d mean')][0]
                new_cases_14d_avg=new_cases_avg=self.smooth.data[self.smooth.headers.index('14d mean')][0]
            else:
                mean7d=self.smooth.data[self.smooth.headers.index('7d mean')]
                mean14d=self.smooth.data[self.smooth.headers.index('14d mean')]
                new_cases_avg=mean7d[len(mean7d)-1]
                new_cases_14d_avg=mean14d[len(mean14d)-1]


            self.simulated=simulate(new_cases_avg,self.attr.population,new_cases_assumed14=new_cases_14d_avg)
            self.simulated.simulate_new_cases()
            self.simulated.create_th_values()
            logger.info("Done preprocessing data - starting to save the plots --- %s seconds ---" % (time.time() - start_time))
            self.attr.color_scheme().headerBGcolor

        except Exception as e:
            logger.error(e)
                






