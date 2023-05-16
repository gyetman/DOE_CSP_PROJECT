from datetime import date

from dash.dcc.Markdown import Markdown
import app_config as cfg 
import json
import logging
import pickle
import sys
import fiona
import numpy as np
import helpers
import xarray as xr

from dash import html
from dash import dcc

from pathlib import Path
from scipy.spatial import KDTree
from shapely.geometry import Point, Polygon, shape
from rtree import index
from haversine import haversine, Unit
from urllib.parse import urlparse


# GLOBALS
# TODO: move rate lookup globals to JSON
# globals for fuel rate lookups
BASE_FUEL_URL = 'https://www.eia.gov/dnav/pet/pet_pri_gnd_dcus_'
STATE_FUEL_RATES = [
    'CA','CO','FL','MA','MN','NY','OH','TX','WA'
]
REGION_FUEL_RATES_LOOKUP ={
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

# set basic logging for when module is imported 
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

# patch module-level attribute to enable pickle to work
#kdtree.node = kdtree.KDTree.node
#kdtree.leafnode = kdtree.KDTree.leafnode
#kdtree.innernode = kdtree.KDTree.innernode

# TODO: fix lat/longitude written to JSON file


''' GLOBALS '''
# markdown text template

# layer dictionaries. defaultLayers is always queried for model parameters. Other layers are added
# to the defaultLayers in the method call. 
# TODO: need to move to JSON files

# generalized country layer
countryLayer = {
    'country':{'poly':cfg.gis_query_path / 'countries_generalized.shp'}
}

countyLayer = {
    'county':{'poly':cfg.gis_query_path / 'us_county.shp'}
}

# default theme layers for query
defaultLayers = {
    'county':{'poly':cfg.gis_query_path / 'us_county.shp'},
    'dni':{'raster':cfg.gis_query_path / 'DNI.tif'},
    'ghi':{'raster':cfg.gis_query_path / 'GHI.tif'},
    'desalPlants':{'point':cfg.gis_query_path / 'global_desal.shp'},
    #'desalPlants':{'point':cfg.gis_query_path / 'global_desal_plants.geojson'},
    'powerPlants':{'point':cfg.gis_query_path / 'power_plants.geojson'},
    #'waterPrice':{'point':cfg.gis_query_path / 'CityWaterCosts.shp'},
    'waterPrice':{'point':cfg.gis_query_path / 'global_water_prices.geojson'},
    'weatherFile':{'point':cfg.gis_query_path / 'global_weather_file.geojson'},
    #'canals':{'point':cfg.gis_query_path / 'canals-vertices.geojson'},
    # Canals are stored by state, just the base path here
    'canals':{'point':cfg.gis_query_path / 'canals_split_points' / ''},
    'waterProxy':{'point':cfg.gis_query_path / 'roads_shapes_zipped' / ''},
    'tx_county':{'poly':cfg.gis_query_path / 'tx_county_water_prices.shp'},
}

# lookup for URLs of regulatory information by state
regulatory_links = {
    'TX': 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQgOANT2xM5CppPXMk42iBLMJypBpnY-tDaTxYFoibcuF_kaPvjYbJczqu6N5ImNL8d7aXU6WU16iXy/pubhtml?gid=1175080604&single=true',
    'AZ': 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQgOANT2xM5CppPXMk42iBLMJypBpnY-tDaTxYFoibcuF_kaPvjYbJczqu6N5ImNL8d7aXU6WU16iXy/pubhtml?gid=802223381&single=true',
    'FL': 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQgOANT2xM5CppPXMk42iBLMJypBpnY-tDaTxYFoibcuF_kaPvjYbJczqu6N5ImNL8d7aXU6WU16iXy/pubhtml?gid=1153194759&single=true',
    'CA': 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQgOANT2xM5CppPXMk42iBLMJypBpnY-tDaTxYFoibcuF_kaPvjYbJczqu6N5ImNL8d7aXU6WU16iXy/pubhtml?gid=1162276707&single=true',
    'NV': 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQgOANT2xM5CppPXMk42iBLMJypBpnY-tDaTxYFoibcuF_kaPvjYbJczqu6N5ImNL8d7aXU6WU16iXy/pubhtml?gid=736651906&single=true',
    'CO': 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQgOANT2xM5CppPXMk42iBLMJypBpnY-tDaTxYFoibcuF_kaPvjYbJczqu6N5ImNL8d7aXU6WU16iXy/pubhtml?gid=334054884&single=true',
}

restrictionsLayers = {
    'landUse':{'poly':cfg.gis_query_path / 'county.shp'},
}

def _setup_logging(verbose=False):
    if verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    frmt = '%(asctime)s %(levelname)s %(message)s'
    logging.basicConfig(
        stream=sys.stdout,
        level=level,
        format=frmt,
    )


def lookupLocation(pt, mapTheme='default', verbose=False):
    ''' Method to check inputs and lookup parameters based on location. 
    Generates Markdown text (based on theme) and updates the parameters for the 
    model. 
    @param [pt]: list or tuple of point coordinates in latitude / longitude (x,y)
    @param [mapTheme]: name of map theme. '''
    _setup_logging(verbose)

    # check that coord is lat/long 
    logging.debug('Checking point coords...')
    if not -90 < float(pt[0]) < 90:
        logging.error('latitude out of bounds, check point location')
        return None
    if not -180 < float(pt[1]) < 180:
        logging.error('longitude out of bounds, check point location')
        return None

    logging.debug(f'Clicked point: {pt}')

    # get layer dictionary based on theme name
    themeLyrs = _getThemeLayers(mapTheme)
    logging.info(f'finding locations of {len(themeLyrs)} layers.')

    # find out the country (and state, if in the U.S.)
    country = _findIntersectFeatures(pt,countryLayer['country']['poly'])
    # if in the U.S., get the state
    if country is None:
        logging.info('site location outside country land areas')
    elif country['properties']['iso_merged'] == 'US':
        logging.info('getting state / county')
        state = _findIntersectFeatures(pt,countyLayer['county']['poly'])
    else:
        logging.info('international query')
    # parse the dictionary, getting intersecting / closest features for each
    closestFeatures = dict()
    logging.debug('Performing intersections')

    if not country: # outside land areas
        logging.info('water, only getting subset of features')
        # TODO: refactor to use method or better logic, not hard-coded keys! 
        exclude = set(['county','desalPlants','powerPlants','canals','waterProxy','tx_county'])
        for key, value in themeLyrs.items():
            if key in exclude:
                closestFeatures[key] = ''
            else:
                if 'point' in value.keys():
                    closestFeatures[key] = _findClosestPoint(pt,value['point'])
                elif 'poly' in value.keys():
                    closestFeatures[key] = _findIntersectFeatures(pt,value['poly'])
                elif 'raster' in value.keys():
                    tmp = _getRasterValue(pt, value['raster'])
                    # convert to float so it can be serialized as json
                    if tmp:
                        closestFeatures[key] = float(tmp)
                    else:
                        closestFeatures[key] = ''      
    # U.S. case
    elif country['properties']['iso_merged'] == 'US':
        for key, value in themeLyrs.items():
            if 'point' in value.keys():
                # handle state and county-level data
                # canals are by state
                if key == 'canals':
                    st = f"{state['properties']['STATEAB']}.shp"
                    closestFeatures[key] = _findClosestPoint(pt, value['point'] / st)
                #water proxy is by county
                elif key == 'waterProxy':
                    base_name = f"tl_{state['properties']['STCOUNTY']}"
                    st = f"{base_name}_roads_pt.zip/{base_name}_roads_pt.shp"
                    logging.info("st:")
                    logging.info(st)
                    closestFeatures[key] = _findClosestPoint(
                        pt, 
                        f"zip://{value['point']}/{st}", 
                        f"{value['point']}/{base_name}_roads_pt"
                    )
                else:
                    closestFeatures[key] = _findClosestPoint(pt,value['point'])
            elif 'poly' in value.keys():
                closestFeatures[key] = _findIntersectFeatures(pt,value['poly'])
            elif 'raster' in value.keys():
                tmp = _getRasterValue(pt, value['raster'])
                # convert raster value returned to float so it can be serialized as json
                if tmp:
                    closestFeatures[key] = float(tmp)
                else:
                    closestFeatures[key] = ''

                    
    else:
        logging.info('international, only getting subset of features')
        # TODO: refactor to use method or better logic, not hard-coded keys! 
        exclude = set(['county','powerPlants','canals','waterProxy'])
        for key, value in themeLyrs.items():
            if key in exclude:
                closestFeatures[key] = ''
            else:
                if 'point' in value.keys():
                    closestFeatures[key] = _findClosestPoint(pt,value['point'])
                elif 'poly' in value.keys():
                    closestFeatures[key] = _findIntersectFeatures(pt,value['poly'])
                elif 'raster' in value.keys():
                    tmp = _getRasterValue(pt, value['raster'])
                    # convert to float so it can be serialized as json
                    if tmp:
                        closestFeatures[key] = float(tmp)
                    else:
                        closestFeatures[key] = ''
    # update the map data JSON file
    logging.info('Updating map json')
    logging.info(closestFeatures.keys())

    mapJson = _paramsToJson(closestFeatures, pt)
    logging.info('Generating markdown')
    mdown, links = _generateMarkdown(mapTheme,closestFeatures,pt)
    return(mdown, links, mapJson)

    # _updateMapJson(closestFeatures, pt)
    # # return the markdown
    # return(_generateMarkdown(mapTheme,closestFeatures,pt))
    # #return(_generateMarkdown(mapTheme,closestFeatures,pt))

def getClosestInfrastructure(pnt):
    ''' Get the closest desal and power plant locations '''
    logging.info('Getting plant info...')
    # first, check if we are outside the U.S. 
    country = _findIntersectFeatures(pnt,countryLayer['country']['poly'])
    if not country: 
        return None

    if country['properties']['iso_merged'] == 'US':
        # get the state
        state = _findIntersectFeatures(pnt,countyLayer['county']['poly'])
        st = f"{state['properties']['STATEAB']}.shp"
        cnty = f"tl_{state['properties']['STCOUNTY']}"
        w_proxy = f"zip://{defaultLayers['waterProxy']['point']}/{cnty}_roads_pt.zip/{cnty}_roads_pt.shp"
        logging.info("Water Proxy:")
        logging.info(w_proxy)
        desal = _findClosestPoint(pnt,defaultLayers['desalPlants']['point'])
        plant = _findClosestPoint(pnt,defaultLayers['powerPlants']['point'])
        canal = _findClosestPoint(pnt, defaultLayers['canals']['point'] / st)
        #canal = _findClosestPoint(pnt,defaultLayers['canals']['point'])
        # water is zipped, needs the kd_path parameter
        kd = f"{defaultLayers['waterProxy']['point']}/{cnty}_roads_pt"
        logging.info(kd)
        water = _findClosestPoint(pnt,w_proxy,kd_path=kd)
        return {
            'desal':[desal['properties']['Latitude'],desal['properties']['Longitude']],
            'plant':[plant['geometry']['coordinates'][1],plant['geometry']['coordinates'][0]],
            'canal':[canal['geometry']['coordinates'][1],canal['geometry']['coordinates'][0]],
            'water':[water['properties']['POINT_Y'],water['properties']['POINT_X']],
        }
    else:
        desal = _findClosestPoint(pnt,defaultLayers['desalPlants']['point'])
        return {
            'desal':[desal['properties']['Latitude'],desal['properties']['Longitude']]
        }

def _getRasterValue(pt,raster):
    ''' lookup a raster value at a given point. Currently, only works for single-band
    rasters, behaviour for multi-band or time-enabled uncertain. '''
    with xr.open_rasterio(raster) as xarr:
        val = xarr.sel(x=pt[1],y=pt[0], method='nearest')
        return val.data.item(0)

def _calcDistance(start_pnt, end_pnt):
    ''' get the great circle distance from two lat/long coordinate pairs
    using the Haversine method (approximation)'''
    return(haversine(start_pnt,end_pnt,unit=Unit.KILOMETERS))
    return(str(closestFeatures))

def _getThemeLayers(mapTheme):
    ''' return the list of layers to search based on the map theme '''
    # TODO: read the lists from a JSON file using the helper module

    if mapTheme.lower() == 'default':
        return defaultLayers
    elif mapTheme.lower() == 'restrictions':
        return {**defaultLayers, **restrictionsLayers}

def _findMatchFromCandidates(pt,intersectLyr,candidates):
    '''open the layer and search through the candidate matches
    to find the true intersection with the point. '''
    ptGeom = Point([pt[1],pt[0]])
    # open the polygon and subset to the candidates
    with fiona.open(intersectLyr) as source:
        features = list(source)
    #featureSubset = map(features.__getitem__,candidates)
    for candidate in candidates:
        feature = features[candidate]

        if ptGeom.within(Polygon(shape(feature['geometry']))):
            return(feature)

    # if no match found, return the last checked. 
    return(feature)

def _findIntersectFeatures(pt,intersectLyr):
    ''' find features in the supplied layers that intersect the provided point 
    @param [pt]: list or tuple of point coordinates in latitude / longitude (x,y)
    @param [lyrs]: list or tuple of polygon layers to find the point
    '''
    # make the point a poly geometry
    queryPoly = Point(pt).buffer(0.1)
    bounds = list(queryPoly.bounds)
    # rtree uses a different order: left, bottom, right, top
    bounds = (bounds[1],bounds[0],bounds[3],bounds[2])
    # open the layer and find the matches
    logging.info(f'Finding intersections with {intersectLyr.stem}...')
    rtreeFile = Path(f'{intersectLyr.parent}/{intersectLyr.stem}')
    if rtreeFile.exists:
        logging.info('Using pre-built rtree index')
        idx = index.Index(str(rtreeFile.absolute()))
        possibleMatches = [x for x in idx.intersection(bounds)]
    else:
        logging.info('No index found, using slow method!!!')
        # TODO: open & find with slow method
    
    if len(possibleMatches) == 0:
        logging.info(f'No matching feature foound for {intersectLyr.stem}')
        return None
    elif len(possibleMatches) == 1:
        # single match 
        with fiona.open(intersectLyr) as source:
            features = list(source)
            ## TODO: do the intersect! 
            return features[possibleMatches[0]]
    else:
        # call the method to do polygon intersection to 
        # get the exact match from the list of possibles
        # currently not being used...
        return _findMatchFromCandidates(pt,intersectLyr,possibleMatches)
        
def _findClosestPoint(pt,lyr,kd_path=None):
    ''' find the closest point or line to the supplied point
    @param [pt]: list or tuple of point coordinates in latitude / longitude (x,y)
    @param [closestLayers]: list of point or line layers
    @param [kd_path]: is the path and base name for the KD file stored outside
    of a zipped archive
    ''' 
    # TODO: update max dist, I believe it's in DD, not meters or km
    queryPoint = np.asarray([pt[1],pt[0]]) 
    # open each layer and find the matches
    logging.info(f'Finding closest point for {lyr}...')
    # check for kdtree
    if kd_path:

        logging.info(f'KD Path provided: {kd_path}')
        kdFile = Path(f'{kd_path}.kdtree')
    else:
        kdFile = Path(f'{lyr.parent}/{lyr.stem}.kdtree')
        logging.info(kd_path)
    logging.info(kdFile)
    if kdFile.exists:
        logging.info('using pre-built index')
        with open(kdFile,'rb') as f:
            idx = pickle.load(f)
            closestPt = idx.query(queryPoint)
            logging.debug(closestPt)
    # else:
        # with fiona.open(lyr) as source:
        #     features = list(source)
        # pts = np.asarray([feat['geometry']['coordinates'] for feat in features])
        # TODO: finish the search function for non-KDTree points
        
    if not closestPt:
        return None    
    # get the matching point
    with fiona.open(lyr) as source:
        features = list(source)
        match = features[closestPt[1]]
        return(match)


def _getFuelURL(state):
    '''Construct the URL for the EIA web page listing fuel rates
    using the provided state abbreviation '''
    if state.upper() in STATE_FUEL_RATES:
        return f'{BASE_FUEL_URL}s{state.lower()}_w.htm' 
    elif state.upper() in REGION_FUEL_RATES_LOOKUP.keys():
        return f'{BASE_FUEL_URL}r{REGION_FUEL_RATES_LOOKUP[state.upper()]}_w.htm'

def _generateMarkdown(theme, atts, pnt):
    ''' generate the markdown to be returned for the current theme '''
    # TODO: something more elegant than try..except for formatted values that crash on None
    # handle the standard theme layers (all cases)
    links = [] # holds all links to be returned
    mdown = []
    mdown.append(f"Located near {atts['weatherFile']['properties'].get('City').replace('[','(').replace(']', ')')}, {atts['weatherFile']['properties'].get('State')}  ")
    dni = atts.get('dni')
    ghi = atts.get('ghi')
    if all((dni,ghi)):
        mdown.append(f"DNI: {dni:,.1f}   GHI:{ghi:,.1f}   kWh/m2/day  ")
    else:
        mdown.append("DNI: - GHI:- kWh/m2/day  ")
    if atts['desalPlants']:
        desal_pt = [atts['desalPlants']['properties'].get('Latitude'),atts['desalPlants']['properties'].get('Longitude')]
        desal_dist = _calcDistance(pnt,desal_pt)
        mdown.append(f"**Closest desalination plant** ({desal_dist:,.1f} km) name: {atts['desalPlants']['properties'].get('Project na')}  ")
        desal = atts['desalPlants']['properties']
        try:
            mdown.append(f"Capacity: {float(desal.get('Capacity').strip().replace(',','')):,.0f} m3/day  ")
        except Exception as e:
            logging.error(e)
            mdown.append(f"Capacity: -  ")  
        mdown.append(f"Technology: {desal.get('Technology')}  ")
        mdown.append(f"Feedwater:  {desal.get('Feedwater')}  ")
        mdown.append(f"Customer type: {desal.get('Customer t')}  ")

    if atts['canals']:
        canal_pt = [atts['canals']['geometry'].get('coordinates')[1],atts['canals']['geometry'].get('coordinates')[0]]
        canal_dist = _calcDistance(pnt,canal_pt)
        mdown.append(f"**Closest Canal / piped water infrastructure** ({canal_dist:,.1f} km) ")
        canal_name = atts['canals']['properties'].get('Name')
        if canal_name is None:
            mdown.append('  ')
        else:
            mdown.append(f"{canal_name}  ")

    # water proxy
    if atts['waterProxy']:
        water_pt = [atts['waterProxy']['properties'].get('POINT_Y'), atts['waterProxy']['properties'].get('POINT_X')]
        water_dist = _calcDistance(pnt,water_pt)
        mdown.append(f"**Closest Water Proxy Location** ({water_dist:,.1f} km) ")
        water_name = atts['waterProxy']['properties'].get('FULLNAME')
        if water_name is None:
            mdown.append('  ')
        else:
            mdown.append(f"{water_name}  ")
    # power plants
    if atts['powerPlants']:
        power = atts['powerPlants']['properties']
        power_pt = [atts['powerPlants']['geometry']['coordinates'][1],atts['powerPlants']['geometry']['coordinates'][0]]
        power_dist = _calcDistance(pnt,power_pt)
        mdown .append(f"**Closest power plant** ({power_dist:,.1f} km): {power.get('Plant_name')}  ")

        mdown.append(f"Primary Generation: {power.get('Plant_primary_fuel')}  ")
        try:
            mdown.append(f"Nameplate Capacity: {power.get('Plant_nameplate_capacity__MW_'):,.0f} MW  ")
        except:
            mdown.append(f"Production: -  ")
        try:
            mdown.append(f"Number of Generators: {power.get('Number_of_generators')}  ")
        except:
            mdown.append(f"Number of Generators: -  ")
        try: 
            mdown.append(f"Annual Net Generation: {power.get('Plant_annual_net_generation__MW'):,.0f} MWh  ")
        except:
            mdown.append("Annual Net Generation: - MWh  ")
        try:
            mdown.append(f"Year of data: {power.get('Data_Year')}  ")
        except:
            pass


    water = atts['waterPrice']['properties']
    mdown.append("**Residential Water Prices** (2018)  ")
    try:
        mdown.append(f"Utility provider: {water.get('UtilityShortName')}  ")
        mc6 = water.get('CalcTot6M3CurrUSD')
        mc15 = water.get('CalcTot15M3CurrUSD')
        mc50 = water.get('CalcTot50M3CurrUSD')
        mc100 = water.get('CalcTot100M3CurrUSD')
        if not mc6:
            mdown.append(f"Consumption to 6m3: $ - /m3  ")
        elif float(mc6) < 0.005:
            mdown.append(f"Consumption to 6m3: $ - /m3  ")
        else:
            mdown.append(f"Consumption to 6m3: ${float(mc6):,.2f}/m3  ")
        if not mc15:
            mdown.append(f"Consumption to 15m3: $ - /m3  ")
        elif float(mc15) < 0.005:
            mdown.append(f"Consumption to 15m3: $ - /m3  ")
        else:
            mdown.append(f"Consumption to 15m3: ${float(mc15):,.2f}/m3  ")
               
        if not mc50:
            mdown.append(f"Consumption to 50m3: $ - /m3  ")
        elif float(mc50) < 0.005:
            mdown.append(f"Consumption to 50m3: $ - /m3  ")
        else:
            mdown.append(f"Consumption to 50m3: ${float(mc50):,.2f}/m3  ")

        if not mc100:
            mdown.append(f"Consumption to 100m3: $ - /m3  ")
        elif float(mc100) < 0.06:
            mdown.append(f"Consumption to 100m3: $ - /m3  ")
        else:
            mdown.append(f"Consumption to 100m3: ${float(mc100):,.2f}/m3  ")

        address = water.get('WebAddress')
        if address: 
            url_parsed = urlparse(address)
            href_parsed = f'{url_parsed.scheme}://{url_parsed.netloc}{url_parsed.path}'
            logging.info(f'url type: {url_parsed}')
            links.append(html.A("Water Price Source", href=href_parsed, target="_blank"))
            links.append(html.Br())
            
    except Exception as e:
        logging.info(e)
        mdown.append(f"Residential price: -  ")

    if atts['tx_county']:
        tx_prices = atts['tx_county']['properties']
        mdown.append(f'**Texas County Water Prices**  ')
        comm_price = tx_prices.get('comm_avg')
        res_price = tx_prices.get('res_avg')
        if comm_price:
            mdown.append(f'Average Commercial Price: ${comm_price:,.2f}/m3  ')
        else:
            mdown.append("Average Commercial Price: $-  ")
        if res_price:
            mdown.append(f"Average Residential Price: ${res_price:,.2f}/m3  ")
        else:
            mdown.append("Average Residential Prices: $-  ")
    else:
        logging.debug('No Texas County!')

    if atts['county']:
        state = atts['county']['properties'].get('STATEAB')
        #link = f'<a href="{regulatory_links[state]}" target="_blank">{state}</a>'
        if state in regulatory_links.keys():
            #link = f"[Regulatory information for {state}]({regulatory_links.get(state)})"
            link = f"{regulatory_links.get(state)}"
            links.insert(0, html.Br())
            links.insert(0, html.A(f"Regulatory information for {state}", href=link, target='_blank'))
        fuel_url = _getFuelURL(state)
        if fuel_url:
            links.append(html.A('Fuel Prices from EIA',href=fuel_url, target='_blank'))
            links.append(html.Br())
    return(mdown, links)

def _updateMapJson(atts, pnt):
    '''deprecated, use _paramsToJson() instead'''
    mParams = dict()
    # update dictionary
    wx = atts['weatherFile']['properties']
    mParams['file_name'] = str(cfg.weather_path / wx.get('filename'))
    logging.info(atts['waterPrice']['properties'])
    mParams['water_price'] = atts['waterPrice']['properties'].get('CalcTot100M3CurrUSD')
    # mParams['water_price_res'] = dfAtts.Avg_F5000gal_res_perKgal.values[0]
    mParams['latitude'] = pnt[0]
    mParams['longitude'] = pnt[1]
    if atts['desalPlants']:
        desal_pt = [atts['desalPlants']['properties'].get('Latitude'),atts['desalPlants']['properties'].get('Longitude')]
        mParams['dist_desal_plant'] = _calcDistance(pnt,desal_pt)
    else:
        mParams['dist_desal_plant'] = None
    if atts['powerPlants']:
        power_pt = [atts['powerPlants']['geometry']['coordinates'][1],atts['powerPlants']['geometry']['coordinates'][0]]
        mParams['dist_power_plant'] = _calcDistance(pnt,power_pt)
    else:
        mParams['dist_power_plant'] = None

    # mParams['dist_water_network'] = dfAtts.WaterNetworkDistance.values[0] / 1000
    mParams['ghi'] = atts.get('ghi')
    mParams['dni'] = atts.get('dni')
    if atts['waterProxy']:
        water_pt = [atts['waterProxy']['properties'].get('POINT_Y'), atts['waterProxy']['properties'].get('POINT_X')]
        mParams['dist_water_network'] = _calcDistance(pnt,water_pt)
    else:
        mParams['dist_water_network'] = None

    mParams['state'] = wx.get('State')
    mParams['city'] = wx.get('City')
    mParams['Country'] = wx.get('Country')
    mParams['water_price'] = atts['waterPrice']['properties'].get('CalcTot100M3CurrUSD')

    mParams['latitude'] = pnt[0]
    mParams['longitude'] = pnt[1]
    # mParams['water_price_res'] = dfAtts.Avg_F5000gal_res_perKgal.values[0]
    # mParams['dni'] = dfAtts.ANN_DNI.values[0]
    # mParams['ghi'] = dfAtts.GHI.values[0]
    # mParams['dist_desal_plant'] = dfAtts.DesalDist.values[0] / 1000
    # mParams['dist_water_network'] = dfAtts.WaterNetworkDistance.values[0] / 1000
    # mParams['dist_power_plant'] = dfAtts.PowerPlantDistance.values[0] / 1000

    # dump to config file
        # update json file
    logging.info('Writing out JSON...')
    try:
        helpers.json_update(data=mParams, filename=cfg.map_json)
    except FileNotFoundError:
        helpers.initialize_json(data=mParams, filename=cfg.map_json)

def _paramsToJson(atts, pnt):
    ''' takes the results of the lookups, calculates distances, and puts it all in a dictionary'''
    mParams = dict()
    # update dictionary
    wx = atts['weatherFile']['properties']
    mParams['file_name'] = str(cfg.weather_path / wx.get('filename'))
    # logging.info(atts['waterPrice']['properties'])
    mParams['water_price'] = atts['waterPrice']['properties'].get('CalcTot100M3CurrUSD')
    # mParams['water_price_res'] = dfAtts.Avg_F5000gal_res_perKgal.values[0]
    mParams['latitude'] = pnt[0]
    mParams['longitude'] = pnt[1]
    if atts['desalPlants']:
        desal_pt = [atts['desalPlants']['properties'].get('Latitude'),atts['desalPlants']['properties'].get('Longitude')]
        mParams['dist_desal_plant'] = _calcDistance(pnt,desal_pt)
    else:
        mParams['dist_desal_plant'] = None
    if atts['powerPlants']:
        power_pt = [atts['powerPlants']['geometry']['coordinates'][1],atts['powerPlants']['geometry']['coordinates'][0]]
        mParams['dist_power_plant'] = _calcDistance(pnt,power_pt)
    else:
        mParams['dist_power_plant'] = None

    # mParams['dist_water_network'] = dfAtts.WaterNetworkDistance.values[0] / 1000
    mParams['ghi'] = atts.get('ghi')
    mParams['dni'] = atts.get('dni')
    if atts['waterProxy']:
        water_pt = [atts['waterProxy']['properties'].get('POINT_Y'), atts['waterProxy']['properties'].get('POINT_X')]
        mParams['dist_water_network'] = _calcDistance(pnt,water_pt)
    else:
        mParams['dist_water_network'] = None

    mParams['state'] = wx.get('State')
    mParams['city'] = wx.get('City')
    mParams['Country'] = wx.get('Country')
    mParams['water_price'] = atts['waterPrice']['properties'].get('CalcTot100M3CurrUSD')

    mParams['latitude'] = pnt[0]
    mParams['longitude'] = pnt[1]

    return mParams
    

if __name__ == '__main__':
    ''' main method for testing/development '''
    import datetime
    start = datetime.datetime.now()
    _setup_logging(False)
    logging.info('starting test...')
    #ptCoords = (-73.988033,41.035572) # matches two counties
    #ptCoords = (-119.0, 26.0) # doesn't match any counties
    #ptCoords = (34.0, -115.0) # matches one county
    ptCoords = (37.0,-110.0)
    #lookupLocation(ptCoords)

    #print(getClosestPlants(ptCoords))
    #print(_calcDistance([0,0],[1,1]))
    ptCoords = (34.0, -115.0) 
    lookupLocation(ptCoords)
    end = datetime.datetime.now()
    print(f'total process took {end - start}')