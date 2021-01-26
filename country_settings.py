class attributes_lv:
    def __init__(self,threshold_list,range_for_r):
        self.country_name = 'Latvia'
        self.population = 1907675
        self.url = 'https://data.gov.lv/dati/eng/api/3/action/datastore_search_sql?sql=SELECT%20*%20from%20%22d499d2f0-b1ea-4ba2-9600-2c701b03bd4a%22'
        self.url_contains_tests=True
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

class attributes_de:
    def __init__(self,threshold_list,range_for_r):
        self.country_name = 'Germany'
        self.population = 83190556
        self.url = 'https://opendata.arcgis.com/datasets/dd4580c810204019a7b8eb3e0b329dd6_0.geojson'
        self.url_contains_tests=False
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
        if country=='lv':
            attributes=attributes_lv(threshold_list,range_for_r)
        elif country=='de':
            attributes=attributes_de(threshold_list,range_for_r)
        else:
            print("Error no such country attribute defined")
        
        return attributes

    except Exception as e:
        print(e)
            
        
    
# de -> Germany attributes
# lv  -> Latvia attributes
#  de  