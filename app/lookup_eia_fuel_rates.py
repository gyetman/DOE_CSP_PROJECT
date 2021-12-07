from html import parser
import urllib.parse
import urllib.request
import json
import dash_html_components as html

# API key
KEY = '544d48d18f13dc9f9dc475908344ceaf'
# API URL
BASE_FUEL_URL = 'https://www.eia.gov/dnav/pet/pet_pri_gnd_dcus_'

STATE_FUEL_RATES = [
    'CA','CO','FL','MA','MN','NY','OH','TX','WA'
]
REGION_FEUL_RATES_LOOKUP ={
    'CT':'1x', # PADD1A
    'ME':'1x',
    'MA':'1x',
    'NH':'1x',
    'RI':'1x',
    'VT':'1x',

    'DE':'1y', #PADD1B
    'DC':'1y',
    'MD':'1y',
    'NJ':'1y',
    'NY':'1y',
    'PA':'1y',

    'FL':'1z', #PADD1C
    'GA':'1z',
    'NC':'1z',
    'SC':'1z',
    'VA':'1z',
    'WV':'1z',

    'IL':'20', #PADD2
    'IN':'20',
    'IO':'20',
    'KS':'20',
    'KY':'20',
    'MI':'20',
    'MS':'20',
    'NE':'20',
    'ND':'20',
    'OH':'20',
    'OK':'20',
    'SD':'20',
    'TN':'20',
    'WI':'20',

    'AL':'30',#PADD3
    'AR':'30',
    'LA':'30',
    'MS':'30',
    'NM':'30',
    'TX':'30',

    'CO':'40',#PADD4
    'ID':'40',
    'MT':'40',
    'UT':'40',
    'WY':'40',
    
    'AK':'5xca',#PADD5
    'AZ':'5xca',
    'HI':'5xca',
    'NV':'5xca',
    'OR':'5xca',
    'WA':'5xca',
}

# TODO: 
# find industrial (failing that, commercial)
# write out link to map-data.json as a new 
# entry: utility rates

## Also: if in the U.S., query the U.S. database,
# otherwise, query international data 

    
def lookup_rates(state='NJ'):
    '''Construct the URL for the EIA web page listing fuel rates
    using the provided state abbreviation '''
    if state.upper() in STATE_RATES:
        return f'{BASE_URL}s{state.lower()}_w.htm' 
    elif state.upper() in REGION_RATES_LOOKUP.keys():
        return f'{BASE_URL}r{REGION_RATES_LOOKUP[state.upper()]}_w.htm'


if __name__ == '__main__':
    ''' main method for testing/development '''
    print('testing GET of data based on coords...')
    print(lookup_rates('NJ'))
    