from covid_utils import download_lv_covid_data,calculate_smoothened_values_pandaless, simulate_threshold_dates, simulate_new_cases_pandaless

# URL for latvia
url='https://data.gov.lv/dati/eng/api/3/action/datastore_search_sql?sql=SELECT%20*%20from%20%22d499d2f0-b1ea-4ba2-9600-2c701b03bd4a%22'
cases_dict,tests_dict=download_lv_covid_data(url)

# Calculate smoothened data

smoothened_list, headers_smoothened=calculate_smoothened_values_pandaless(list(cases_dict.values()),population=1907675,list_of_tests=list(tests_dict.values()))

## Select all 14 day calculations from smoothened_list
headers_smoothened14 = list(filter(lambda x: x.find('7d')<0,headers_smoothened)) # Idea about x.find(): anything not containing the 7d calculations needs to be kept
smoothened_list14 = [x for x, y in zip(smoothened_list, headers_smoothened) if y.find('7d')<0]

## Select all 7 day calculations from smoothened_list
headers_smoothened7 = list(filter(lambda x: x.find('14d')<0,headers_smoothened)) # Idea about x.find(): anything not containing the 14d calculations needs to be kept
smoothened_list7 = [x for x, y in zip(smoothened_list, headers_smoothened) if y.find('14d')<0]


# Calculate simulated data

## Calculate threshold days
Range_for_R=[0.8,0.85,0.9,0.95,1.05,1.1,1.15,1.2]
mean7d=smoothened_list[headers_smoothened.index('7d mean')]
population_lv=1907675
threshold_days_list=simulate_threshold_dates(Range_for_R,mean7d[len(mean7d)-1],population_lv)
threshold_days_header=['R']+list(map(str,[10,20,50,100,200,400,600,800,1000]))

## simulate new cases
simulated_new_cases, simulated_casesPer100k_7d, simulated_casesPer100k_14d=simulate_new_cases_pandaless(Range_for_R,mean7d[len(mean7d)-1],population_lv)
simulated_cases_header=list(map(str,Range_for_R))


print('hello')