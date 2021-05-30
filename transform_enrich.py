## Utility functions for Covid Research
import numpy as np
from loguru import logger
import sys
from datetime import datetime, timedelta

logger.add(sys.stderr, format="{time} {level} {message}", filter="enrich", level="INFO")
logger.add(sys.stderr, format="{time} {level} {message}", filter="enrich", level="ERROR")

class history():
    def calculate_values(self,population,daily_dict,reversed_dates=True):
        """
        Calculates smoothened covid case values by applying rolling averages and sums over 7 and 14 days. It also calculates an estimated r0 and new case per 100k for 7 and 14 days.
        If there is a daily test data it also calculates a test positive rate over 7 days.
        
        Parameters
        ----------
        population : int
            The population of a country
        daily_dict : dict
            A dictionary containing a list of dates, new cases and optionally the amount of tests for that day
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
            list_of_cases=daily_dict['New Cases']
            New_Cases_7_Day_Sum=list(rolling_sum(list_of_cases))
            New_Cases_14_Day_Sum=list(rolling_sum(list_of_cases,interval=14))
            New_Cases_7_Day_Mean=list(map(lambda x: round(x/7,2) if x is not None else None,New_Cases_7_Day_Sum))
            New_Cases_14_Day_Mean=list(map(lambda x: round(x/14,2) if x is not None else None,New_Cases_14_Day_Sum))
            New_Cases_100K_7_Days=list(map(lambda x: round((x/population)*100000,2) if x is not None else None,New_Cases_7_Day_Sum))
            New_Cases_100K_14_Days=list(map(lambda x: round((x/population)*100000,2) if x is not None else None,New_Cases_14_Day_Sum))
            Estimated_delta=list(map(lambda x,y: calculateR(x,y),New_Cases_7_Day_Sum,New_Cases_14_Day_Sum))
            Estimated_R=[round(x**(4/7),2) for x in Estimated_delta if x is not None]

            if daily_dict['Tests'] is not None:                # Since some countries do not publish daily data on tests (looking at you Germany!) I make this calculation optional 
                # Calculating 7 and 14 day rolling sum for TEST NUMBER
                Tests_7_Day_Sum=list(rolling_sum(daily_dict['Tests']))
                Tests_14_Day_Sum=list(rolling_sum(daily_dict['Tests'],interval=14))
                # Calculating smoothened īpatsvars (positive tests)
                Positive_rate_7_Days=list(map(lambda x,y: calculateTestPositivity(x,y),New_Cases_7_Day_Sum,Tests_7_Day_Sum))
                Positive_rate_14_Days=list(map(lambda x,y: calculateTestPositivity(x,y),New_Cases_14_Day_Sum,Tests_14_Day_Sum))
                Positive_rate_daily=list(map(lambda x,y: calculateTestPositivity(x,y),list_of_cases,daily_dict['Tests']))

                self.data=[daily_dict['Date'],list_of_cases,daily_dict['Tests'],Positive_rate_daily,Estimated_delta,Estimated_R,Positive_rate_7_Days,Positive_rate_14_Days,New_Cases_7_Day_Mean,New_Cases_100K_7_Days,New_Cases_7_Day_Sum,Tests_7_Day_Sum,New_Cases_14_Day_Mean,New_Cases_100K_14_Days,New_Cases_14_Day_Sum,Tests_14_Day_Sum]
                self.headers=['Date','New Cases','Tests administered','Positive Rate','growth factor','R (estimate)','Positive Rate 7d','Positive Rate 14d','7d mean','Cases/100k 7d','Cases Sum 7d','Tests Sum 7d','14d mean','Cases 100k 14d','Cases Sum 14d','Tests Sum 14d']
            else:
                self.data=[daily_dict['Date'],list_of_cases,Estimated_delta,Estimated_R,New_Cases_7_Day_Mean,New_Cases_100K_7_Days,New_Cases_7_Day_Sum,New_Cases_14_Day_Mean,New_Cases_100K_14_Days,New_Cases_14_Day_Sum]
                self.headers=['Date','New Cases','Growth factor','R (estimate)','7d mean','Cases/100k 7d','Cases Sum 7d','14d mean','Cases/100k 14d','Cases Sum 14d']

            ## Select all 7 day calculations from smoothened_list
            self.headers7=list(filter(lambda x: x.find('14d')<0,self.headers)) # Idea about x.find(): anything not containing the 14d calculations needs to be kept
            self.data7 = [x for x, y in zip(self.data, self.headers) if y.find('14d')<0]

            ## Select all 14 day calculations from smoothened_list
            self.headers14 = list(filter(lambda x: x.find('7d')<0, self.headers)) # Idea about x.find(): anything not containing the 7d calculations needs to be kept
            self.data14 = [x for x, y in zip(self.data, self.headers) if y.find('7d')<0]

        except Exception as e:
            logger.error(e)

## the following functions are utility functions 

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
        cumulated_sum=[int(x) for x in np.cumsum(list_of_cases,dtype=int)]      # needed for json convertability
        rolling_sum=[cumulated_sum[i+interval]-cumulated_sum[i] for i in range(0,len(cumulated_sum)-interval)]
        # rolling_sum=list(cumulated_sum[interval:]-cumulated_sum[:-interval])
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

class simulate():
    def __init__(self,new_cases_assumed,population,R_range=[0.8,0.85,0.9,0.95,1.05,1.1,1.15,1.2],thresholds=[10,20,50,100,200,400,600,800,1000],new_cases_assumed14=None):
        """ 
        Parameters
        ----------
        new_cases_assumed : int
            The current number of new cases. It is recommended to use the current mean over 7 days, since that statistic is robust to statistical noise occuring over a week.
        population : int
            The population of a country
        R_range : list
            A list of floats representing the range of R
        thresholds : list
            A list of integers representing the threshold which R has to go above or below
        new_cases_assumed14 : int
            The current number of new cases over 14 days. It is optional, but recommendation is to provide this input. Otherwise accuracy might suffer
        
        """
        self.input_new_cases_avg=new_cases_assumed
        self.input_population=population
        self.input_r_range=list(sorted(R_range))
        self.input_delta_range=[R**(7/4) for R in list(sorted(R_range))] # transform R 
        self.input_thresholds=thresholds
        self.input_new_cases_avg14=new_cases_assumed if new_cases_assumed14 is None else new_cases_assumed14
        
    def create_th_values(self):
        """
        Creates four lists. There is two types of lists: One where the simulated cases per 100k are below the 
        current cases per 100k (usually using a below in the name). The other lists are created when simulated cases per 100k are 
        *above* the current cases per 100k (usually using an above in the name). Since I use both 7 and 14 day calculations we end up
        with four lists. 
        
        Returns
        -------
        object
            An object containing relevant output. The lists start with `values`. The corresponding thresholds can be found in the list starting with `th_`
        """
        try:
            # Step 1: Calculate the index where a threshold is above the current cases per 100k - do it for both 7 and 14 days
            current_cases100k_7d=((self.input_new_cases_avg*7)/self.input_population)*100000 # quite accurate
            current_cases100k_14d=((self.input_new_cases_avg14*7)/self.input_population)*100000 # might be inaccurate if no 14d value was supplied
            th_list=self.input_thresholds
            th_above_current100k_7d=next((i for i in range(0,len(th_list)) if sorted(th_list)[i]>current_cases100k_7d),len(th_list))
            th_above_current100k_14d=next((i for i in range(0,len(th_list)) if sorted(th_list)[i]>current_cases100k_14d),len(th_list))
            
            # Step 2: Use this index to create below and above threshold lists for both 7 and 14 day calculations
            self.th_above7=sorted(th_list)[th_above_current100k_7d:]
            self.th_above14=sorted(th_list)[th_above_current100k_14d:]
            self.th_below7=sorted(th_list)[:th_above_current100k_7d]
            self.th_below14=sorted(th_list)[:th_above_current100k_14d]

            # Step 3: Create two lists one with R values above 1 and another with R values below 1
            delta_range=self.input_delta_range
            firstR_over1_i=next((i for i in range(0,len(delta_range)) if sorted(delta_range)[i]>1),len(delta_range))
            delta_below=sorted(delta_range)[:firstR_over1_i]        # contains only growth rates below 1
            delta_above=sorted(delta_range)[firstR_over1_i:]        # contains only growth rates above 1
            r_below=sorted(self.input_r_range)[:firstR_over1_i]
            r_above=sorted(self.input_r_range)[firstR_over1_i:]
            
            # Step 4: Use Steps 3  and  2 to create value lists for all 4 possible cases
            self.values7_above_th=self.get_th_list(self.th_above7,delta_above,r_above,below=False) if len(delta_above)>0 and len(self.th_above7)>0 else None
            self.values14_above_th=self.get_th_list(self.th_above14,delta_above,r_above,d7=False,below=False) if len(delta_above)>0 and len(self.th_above14)>0 else None
            self.values7_below_th=self.get_th_list(self.th_below7,delta_below,r_below) if len(delta_below)>0 and len( self.th_below7)>0 else None
            self.values14_below_th=self.get_th_list(self.th_below14,delta_below,r_below,d7=False)  if len(delta_below)>0  and len( self.th_below14)>0 else None
            # in_FC_cases_per100k_7d - dict

        except Exception as e:
            logger.error(e)

    def get_th_list(self,th_list,growth_list,r_list,d7=True,below=True):
        """
        Calculates after how many days a threshold is reached. Can only be executed after simulate_new_cases
        
        Parameters
        ----------
        th_list : list
            list of thresholds to verify. This list corresponds to d7 and below input
        r_list : float
            list of assumed assumed R values. Either only R values above or below 1; corresponds thus to below
        growth_list : float
            list of assumed growth rates, gained from the assumed R values in the class method. Either only growth rates above or below 1; corresponds thus to below
        d7 : bool
            Is the  a calculation over 7 or 14 days?
        below : bool
            Is the threshold below or above the current cases per 100k?

        Returns
        -------
        int
            An index indicating the number of days until the threshold is reached
        """
        try:
            FC_dict=self.in_FC_cases_per100k_7d if d7 else self.in_FC_cases_per100k_14d
            res=[r_list]
            for th in th_list:
                res.append([self.get_th_days(FC_dict[delta_s],th,d7,below) for delta_s in growth_list])
            return res
            
        except Exception as e:
            logger.error(e)
    
    def get_th_days(self,fc_list,th,d7,below):
        """
        Calculates after how many days a threshold is reached
        
        Parameters
        ----------
        fc_list : list
            the simulated cases per 100k
        th : int
            The threshold to look for
        d7 : bool
            Is the fc_list a calculation over 7 or 14 days?
        below : bool
            Is the threshold below or above the current cases per 100k?

        Returns
        -------
        int
            An index indicating the number of days until the threshold is reached
        """
        try:
            interval=7 if d7 else 14
            fc=fc_list[interval:]
            if below:
                return next((x[0]+interval for x in enumerate(fc) if x[1] < th),None)
            else:
                return next((x[0]+interval for x in enumerate(fc) if x[1] > th),None)

        except Exception as e:
            logger.error(e)

    def simulate_new_cases(self,output_limit=91,window_length=1000,return_threshold_days=True): #new
        """
        Simulates daily new cases (in general and per 100k) according to a specified range of R; adds Date column
        
        Parameters
        ----------
        output_length : int
            The amount of days to forecast (default is 91)
        window_length : int
            The amount of days to check where a threshold migth be reached
        return_threshold_days : bool
            Whether to calculate threshold days or not

        Returns
        -------
        list
            A list of simulated new cases for each day based on a range of assumed effective R-values
        list
            A list of the cases per 100k KPI for 7 days based on a range of assumed effective R-values
        list
            A list of the cases per 100k KPI for 14 days based on a range of assumed effective R-values
        """
        try:
            # create range of dates and insert it at the beginning of the list
            base = datetime.today()
            date_list = [(base + timedelta(days=x)).date().isoformat() for x in range(window_length)]

            self.cases_new=[date_list]
            self.casesPer100k_7d=[date_list]
            self.casesPer100k_14d=[date_list]
            self.in_FC_cases_per100k_7d={}
            self.in_FC_cases_per100k_14d={}
            for delta_s in sorted(self.input_delta_range):
                step_value=(delta_s-1)/7
                new_cases=np.arange(start=1,stop=1+(step_value*window_length),step=step_value)*self.input_new_cases_avg
                New_Cases_7_Day_Sum=rolling_sum(new_cases,interval=7,reversed_dates=False)
                New_Cases_14_Day_Sum=rolling_sum(new_cases,interval=14,reversed_dates=False)
                self.in_FC_cases_per100k_7d[delta_s]=list(map(lambda x: round((x/self.input_population)*100000,2) if x is not None else None,New_Cases_7_Day_Sum))
                self.in_FC_cases_per100k_14d[delta_s]=list(map(lambda x: round((x/self.input_population)*100000,2) if x is not None else None,New_Cases_14_Day_Sum))
                                        
                # append cases for simulated
                self.cases_new.append(list(np.round(new_cases,2)))
                self.casesPer100k_7d.append(self.in_FC_cases_per100k_7d[delta_s])
                self.casesPer100k_14d.append(self.in_FC_cases_per100k_14d[delta_s])


            # calculates after how many days under an assumed R_0 a threshold is reached.
            if return_threshold_days:
                self.threshold_days7=[self.input_r_range]
                self.threshold_days14=[self.input_r_range]
            
                for th in self.input_thresholds:                    
                    threshold_days_list7=[self.verify_threshold(self.in_FC_cases_per100k_7d[delta_s],th,interval=7) for delta_s in self.input_delta_range]
                    self.threshold_days7.append(threshold_days_list7)
                    threshold_days_list14=[self.verify_threshold(self.in_FC_cases_per100k_14d[delta_s],th,interval=14) for delta_s in self.input_delta_range]
                    self.threshold_days14.append(threshold_days_list14)

        except Exception as e:
            logger.error(e)




    def verify_threshold(self, simulated_cases_per100k,threshold,interval=7,returnDates=False):
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
                    return(threshold_date.date().isoformat())

            else:
                return None
            
        except Exception as e:
            logger.error(e)


############################################## this should go in a seperate load_data.py ##################

