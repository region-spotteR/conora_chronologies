class attributes_de:
    def __init__(self,threshold_list,range_for_r):
        self.country_name = 'Germany'
        self.population = 83190556
        self.url = 'https://opendata.arcgis.com/datasets/dd4580c810204019a7b8eb3e0b329dd6_0.geojson'
        self.contains_tests=False
        self.csv=False # if the resources have csv format
        self.CasesPer100k_thresholds=threshold_list
        self.Range_for_R=range_for_r
        self.color_sizes = dict(
            colorEvenRows = '#FFE6D9',
            colorOddRows = 'white',
            colorHeaderBG= '#FFCE00',
            sizeHeaderFont = 14,
            colorHeaderFont='black',
            colorCellFont = 'black',
            sizeCellFont = 12,
            colorTitle = 'black',
            sizeTitleFont = 27,
            colorPivotColumnText='#DD0000'
        )

# https://www.data.gouv.fr/fr/datasets/synthese-des-indicateurs-de-suivi-de-lepidemie-covid-19/
class attributes_fr:
    def __init__(self,threshold_list,range_for_r):
        self.country_name = 'France'
        self.population = 67406000
        self.url = "https://www.data.gouv.fr/fr/datasets/r/f335f9ea-86e3-4ffa-9684-93c009d5e617"
        self.contains_tests=True
        self.csv_encoding='latin'
        self.csv_separator=','
        self.csv=True                   # if the resources have csv format
        self.CasesPer100k_thresholds=threshold_list
        self.Range_for_R=range_for_r
        self.color_sizes=dict(
            colorEvenRows = '#FFE6D9',       #'#FFE3F1'#'#FFAFAE'
            colorOddRows = 'white',
            colorHeaderBG='#001489',
            sizeHeaderFont = 14,
            colorHeaderFont='white',
            colorCellFont = 'black',
            sizeCellFont = 12,
            colorTitle = '#001489',
            sizeTitleFont = 27,
            colorPivotColumnText='#001489'
        )

class attributes_at:
    def __init__(self,threshold_list,range_for_r):
        self.country_name = 'Austria'
        self.population = 8901064
        self.url="https://covid19-dashboard.ages.at/data/CovidFaelle_Timeline.csv"
        self.contains_tests=False
        self.csv_encoding='utf-8'
        self.csv_separator=';'
        self.csv=True # if the resources have csv format
        self.CasesPer100k_thresholds=threshold_list
        self.Range_for_R=range_for_r
        self.color_sizes=dict(
            colorEvenRows = '#F3EED9',       #'#FFE3F1'#'#FFAFAE'
            colorOddRows = 'white',
            colorHeaderBG='#ED2939',
            sizeHeaderFont = 14,
            colorHeaderFont='white',
            colorCellFont = 'black',
            sizeCellFont = 12,
            colorTitle = '#ED2939',
            sizeTitleFont = 27,
            colorPivotColumnText='#ED2939'
        )
# Austria: What the fuck?! The way data is published I would guess this country is a banana republic

class attributes_be:
    def __init__(self,threshold_list,range_for_r):
        self.country_name = 'Belgium'
        self.population = 11492641
        self.url = 'https://epistat.sciensano.be/Data/COVID19BE_tests.json'
        self.contains_tests=True
        self.csv=False # if the resources have csv format
        self.CasesPer100k_thresholds=threshold_list
        self.Range_for_R=range_for_r
        self.color_sizes = dict(
            colorEvenRows = '#FFE6D9',
            colorOddRows = 'white',
            colorHeaderBG= '#FDDA24',
            sizeHeaderFont = 14,
            colorHeaderFont='black',
            colorCellFont = 'black',
            sizeCellFont = 12,
            colorTitle = 'black',
            sizeTitleFont = 27,
            colorPivotColumnText='#EF3340' 
        )

class attributes_lv:
    def __init__(self,threshold_list,range_for_r):
        self.country_name = 'Latvia'
        self.population = 1907675
        self.url = 'https://data.gov.lv/dati/eng/api/3/action/datastore_search_sql?sql=SELECT%20*%20from%20%22d499d2f0-b1ea-4ba2-9600-2c701b03bd4a%22'
        self.contains_tests=True
        self.csv=False # if the resources have csv format
        self.CasesPer100k_thresholds=threshold_list
        self.Range_for_R=range_for_r
        self.color_sizes=dict(
            colorEvenRows = '#F3EED9',       #'#FFE3F1'#'#FFAFAE'
            colorOddRows = 'white',
            colorHeaderBG='#9E3039',
            sizeHeaderFont = 14,
            colorHeaderFont='white',
            colorCellFont = 'black',
            sizeCellFont = 12,
            colorTitle = '#9E3039',
            sizeTitleFont = 27,
            colorPivotColumnText='#9E3039'
        )

def get_attributes(country,threshold_list=[10,20,50,100,200,400,600,800,1000],range_for_r=[0.8,0.85,0.9,0.95,1.05,1.1,1.15,1.2]):
    """
    Gets the country specific attributes like Name, population, url etc. 

    Parameters
    ----------
    country : str
        A two letter color code for a country e.g. 'de' for Germany
    thresholds_list : list
        optional: A list of integers representing the threshold which R has to go above or below
    range_for_r : list
        optional: A list of floats representing the range of R

    Returns
    -------
    class
        Class with the country specific attributes. Also contains a color scheme class for this country
    """
    try:
        if country=='de':
            attributes=attributes_de(threshold_list,range_for_r)
        elif country=='fr':
            attributes=attributes_fr(threshold_list,range_for_r)        
        elif country=='at':
            attributes=attributes_at(threshold_list,range_for_r)
        elif country=='be':
            attributes=attributes_be(threshold_list,range_for_r)
        elif country=='lv':
            attributes=attributes_lv(threshold_list,range_for_r)
        else:
            print("Error no such country attribute defined")
        
        return attributes

    except Exception as e:
        print(e)
            
        
    
# de -> Germany attributes
# lv  -> Latvia attributes
#  de  