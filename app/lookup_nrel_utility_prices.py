import urllib.parse
import urllib.request
import json

# API key
KEY = 'vAvU9ZlrZXVAKd6nKbgUPcIs1yfemIJYmfOFa0N5'
# API URL
BASE_URL = 'https://developer.nrel.gov/api/utility_rates/v3.json?'

def lookup_rates(lat,lon,**kwargs):
    '''Fetch water utility rates from the NREL API
    using the provided coordinates '''
    url_params = {
        'api_key':KEY,
        'lat':lat,
        'lon':lon,
        'format':'json',
    }
    if 'format' in kwargs.keys():
        url_params['format'] = kwargs['format']
    if 'radius' in kwargs.keys():
        url_params['radius'] = kwargs['radius']
    if 'limit' in kwargs.keys():
        url_params['limit'] = kwargs['limit']

    data = urllib.parse.urlencode(url_params)
    # the normal urllib.request.Request defaults to POST, but the 
    # API only supports GET, so we create it as a string
    req = BASE_URL + data
    with urllib.request.urlopen(req) as response:
        result =  json.load(response)

    # convert the result to a dictionary
    prices = result.get('outputs')
    if not prices:
        return None

    # create markdown from the result
    md = f'**Electricity Prices from NREL, 2012** \n'
    md += f'Company: {prices.get("utility_name")} \n'
    md += f'Commercial: {prices.get("commercial")} $/kWh \n'
    md += f'Industrial: {prices.get("industrial")} $/kWh \n'
    md += f'Residential: {prices.get("residential")} $/kWh \n'
    # for price in ['commercial','industrial','residential']:
    #     md += f'{price.title()}: {prices.get(price)}$/kWh \n'
    return(md)

if __name__ == '__main__':
    ''' main method for testing/development '''
    print('testing GET of data based on coords...')
    test = lookup_rates(42,-111)
    # test additional parameters
    # test = lookup_rates(35.45,-82.98,radius=100,limit=2,format='xml')
    # test for no results
    # test = lookup_rates(-55,110)
    print(test)
    