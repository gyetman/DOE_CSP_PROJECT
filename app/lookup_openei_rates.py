from html import parser
import urllib.parse
import urllib.request
import certifi
import json
import dash_html_components as html

# API key
KEY = 'NrYesSRYplmSurhuPtNPqbqC0CwAKtifeBQ7dXX0'
# API URL
BASE_URL = 'https://api.openei.org/utility_rates?'


# TODO: 
# find industrial (failing that, commercial)
# write out link to map-data.json as a new 
# entry: utility rates

## Also: if in the U.S., query the U.S. database,
# otherwise, query international data 

    
def lookup_rates(lat,lon,**kwargs):
    '''Fetch water utility rates from the open_ei API
    using the provided coordinates '''
    url_params = {
        'api_key':KEY,
        'version':'8',
        'lat':lat,
        'lon':lon,
        'format':'json',
        'is_default':'false',
    }
    if 'format' in kwargs.keys():
        url_params['format'] = kwargs['format']
    if 'radius' in kwargs.keys():
        url_params['radius'] = kwargs['radius']
    if 'limit' in kwargs.keys():
        url_params['limit'] = kwargs['limit']
    if 'version' in kwargs.keys():
        url_params['version'] = kwargs['version']

    results = {}
    md = ''
    for sector in ('Industrial','Commercial'):
        url_params['sector'] = sector

        data = urllib.parse.urlencode(url_params)
        # the normal urllib.request.Request defaults to POST, but the 
        # API only supports GET, so we create it as a string
        req = BASE_URL + data
        #print(req)
        with urllib.request.urlopen(req, cafile=certifi.where()) as response:
            result =  json.load(response)

        items = result.get('items')
        if not items:
            # print(f'No matches for {sector}')
            continue
        
        print(f'retrieved {len(items)} records...')
        # get the URIs for each utility
        results = items[0]

        # print(results)
        link = results.get('uri')
        if link: 
            # update markdown based on the result
            #md = html.Div(html.A(f'<b>{sector} Electricity Prices from OpenEI</b>', href=f'{link}', target='_blank'))
            #md = f'<a href="{link}", target="_blank">Electricity Prices from OpenEI</a> \n'
            # md = f'[**{sector} Electricity Prices from OpenEI**]({link}#3__Energy) \n\n'
            energy_link = html.A("Electricity Prices from OpenEI", href=f"{link}#3__Energy", target="_blank")

            return energy_link
        else:
            return None

        # md += f'Commercial: {prices.get("commercial")} $/kWh \n'
        # md += f'Industrial: {prices.get("industrial")} $/kWh \n'
        # md += f'Residential: {prices.get("residential")} $/kWh \n'
        # # for price in ['commercial','industrial','residential']:
        # #     md += f'{price.title()}: {prices.get(price)}$/kWh \n'
        # return(md)
    # if len(results) > 0:
    #     for key, value in results.items():
    #         print(value)
    # else:
    #     return None

if __name__ == '__main__':
    ''' main method for testing/development '''
    print('testing GET of data based on coords...')
    test = lookup_rates(40.89,-74.01)
    # test additional parameters
    # test = lookup_rates(35.45,-82.98,radius=100,limit=2,format='xml')
    # test for no results
    # test = lookup_rates(-55,110)
    print(test)
    print('test complete')
    