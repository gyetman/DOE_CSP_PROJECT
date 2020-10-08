import app_config as cfg 
import json
import logging
import pickle
import sys
import fiona
import numpy as np
import helpers

from pathlib import Path
from scipy.spatial import KDTree
from shapely.geometry import Point, Polygon, shape
from rtree import index
from haversine import haversine, Unit

# patch module-level attribute to enable pickle to work
#kdtree.node = kdtree.KDTree.node
#kdtree.leafnode = kdtree.KDTree.leafnode
#kdtree.innernode = kdtree.KDTree.innernode

''' Module to lookup features based on a point location. Uses rtrees if they exist. '''

''' GLOBALS '''
# markdown text template

# layer dictionaries. defaultLayers is always queried for model parameters. Other layers are added
# to the defaultLayers in the method call. 
# TODO: need to move to JSON files
# TODO: calculate distances to water plants, desal & power plant

defaultLayers = {
    'county':{'poly':cfg.gis_query_path / 'us_county.shp'},
    'dni':{'point':cfg.gis_query_path / 'USAWeatherStations.shp'},
    'desalPlants':{'point':cfg.gis_query_path / 'Desalplants.shp'},
    'powerPlants':{'point':cfg.gis_query_path / 'PowerPlantsPotenialEnergy.shp'},
    'waterPrice':{'point':cfg.gis_query_path / 'CityWaterCosts.shp'},
    'weatherFile':{'point':cfg.gis_query_path / 'USAWeatherStations.shp'},
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


def lookupLocation(pt, mapTheme='default'):
    ''' Method to check inputs and lookup parameters based on location. 
    Generates Markdown text (based on theme) and updates the parameters for the 
    model. 
    @param [pt]: list or tuple of point coordinates in latitude / longitude (x,y)
    @param [mapTheme]: name of map theme. '''
    _setup_logging(verbose=False)

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
    logging.debug(f'finding locations of {len(themeLyrs)} layers.')

    # parse the dictionary, getting intersecting / closest features for each
    closestFeatures = dict()
    logging.debug('Performing intersections')
    for key, value in themeLyrs.items():
        if 'point' in value.keys():
            closestFeatures[key] = _findClosestPoint(pt,value['point'])
        elif 'poly' in value.keys():
            closestFeatures[key] = _findIntersectFeatures(pt,value['poly'])

    # update the map data JSON file
    _updateMapJson(closestFeatures, pt)
    # return the markdown
    return(_generateMarkdown(mapTheme,closestFeatures))
    #return(str(closestFeatures))

def getClosestPlants(pnt):
    ''' Get the closest desal and power plant locations '''
    logging.info('Getting plant info...')
    desal = _findClosestPoint(pnt,defaultLayers['desalPlants']['point'])
    plant = _findClosestPoint(pnt,defaultLayers['powerPlants']['point'])
    return {
        'desal':[desal['properties']['Latitude'],desal['properties']['Longitude']],
        'plant':[plant['geometry']['coordinates'][1],
        plant['geometry']['coordinates'][0]]
    }

def _calcDistance(start_pnt, end_pnt):
    ''' get the great circle distance from two lat/long coordinate pairs
    using the Haversine method (approximation)'''
    return(haversine(start_pnt,end_pnt,unit=Unit.KILOMETERS))
    _updateMapJson(closestFeatures)
    # return the markdown
    #return(_generateMarkdown(mapTheme,closestFeatures))
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
    ptGeom = Point(pt)
    # open the polygon and subset to the candidates
    with fiona.open(intersectLyr) as source:
        features = list(source)
    featureSubset = map(features.__getitem__,candidates)
    for poly in featureSubset:
        if ptGeom.within(Polygon(shape(poly['geometry']))):
            return(poly)
    pass

def _findIntersectFeatures(pt,intersectLyr):
    ''' find features in the supplied layers that intersect the provided point 
    @param [pt]: list or tuple of point coordinates in latitude / longitude (x,y)
    @param [lyrs]: list or tuple of polygon layers to find the point
    '''
    # make the point a poly geometry
    queryPoly = Point(pt).buffer(0.01)
    bounds = list(queryPoly.bounds)
    # rtree uses a different order: left, bottom, right, top
    bounds = (bounds[1],bounds[0],bounds[3],bounds[2])
    # open the layer and find the matches
    logging.info(f'Finding intersections with {intersectLyr}...')
    rtreeFile = Path(f'{intersectLyr.parent}/{intersectLyr.stem}')
    if rtreeFile.exists:
        logging.info('Using pre-built rtree index')
        idx = index.Index(str(rtreeFile.absolute()))
        print(idx.get_bounds())
        possibleMatches = [x for x in idx.intersection(bounds)]
    else:
        logging.info('No index found, using slow method!!!')
        # TODO: open & find with slow method
    
  
    queryPoint = (pt[1], pt[0],pt[1]+.01,pt[0]+.01)
    # open each layer and find the matches
    logging.info(f'Finding intersections with {intersectLyr}...')
    rtreeFile = Path(f'{intersectLyr.parent}/{intersectLyr.stem}')
    if rtreeFile.exists:
        logging.debug('Using pre-built rtree index')
        idx = index.Index(str(rtreeFile.absolute()))
        possibleMatches = [x for x in idx.intersection(queryPoint)]
    else:
        logging.debug('No index found, using slow method')
        # TODO: open & find with slow method
    
    print(len(possibleMatches))
    if len(possibleMatches) == 0:
        return None
    elif len(possibleMatches) > 1:
        # single match 
        with fiona.open(intersectLyr) as source:
            features = list(source)
            return features[possibleMatches[0]]
    else:
        # call the method to do polygon intersection to 
        # get the exact match from the list of possibles
        # currently not being used...
        #return _findMatchFromCandidates(pt,intersectLyr,possibleMatches)
        return None

        
def _findClosestPoint(pt,lyr):
    ''' find the closest point or line to the supplied point
    @param [pt]: list or tuple of point coordinates in latitude / longitude (x,y)
    @param [closestLayers]: list of point or line layers
    ''' 
    # TODO: update max dist, I believe it's in DD, not meters or km
    queryPoint = np.asarray([pt[1],pt[0]]) # is this backwards? 
    # open each layer and find the matches
    logging.info(f'Finding closes point for {lyr}...')
    # check for kdtree
    kdFile = Path(f'{lyr.parent}/{lyr.stem}.kdtree')
    if kdFile.exists:
        logging.debug('using pre-built index')
        with open(kdFile,'rb') as f:
            idx = pickle.load(f)
            closestPt = idx.query(queryPoint)
            logging.debug(closestPt)
    else:
        with fiona.open(lyr) as source:
            features = list(source)
        pts = np.asarray([feat['geometry']['coordinates'] for feat in features])
        # TODO: finish the search function for non-KDTree points
        
    if not closestPt:
        return None    
    # get the matching point
    with fiona.open(lyr) as source:
        features = list(source)
        match = features[closestPt[1]]
        return(match)


def _paramHelper(dfAtts,pt):
    ''' helper method to write out parameters. Uses the solar dataframe point ID 
    to write out map paramers to  '''
    #TODO: object based in likely to be dict, not pandas data frame! 
    # update the code to reflect this
    logging.debug('updating model params')
    mParams = dict()
    # update dictionary
    weatherPath = cfg.base_path
    mParams['file_name'] = str(weatherPath / 'SAM_flatJSON' / 'solar_resource' / dfAtts['weatherFile']['properties']['filename'])
    mParams['county'] = dfAtts['county']['properties']['NAME']
    mParams['state'] = dfAtts['county']['properties']['STUSAB']
    mParams['water_price'] =  dfAtts.WaterPrice.values[0]
    mParams['water_price_res'] = dfAtts.Avg_F5000gal_res_perKgal.values[0]
    mParams['latitude'] = pt[1]
    mParams['dni'] = dfAtts.ANN_DNI.values[0]
    mParams['ghi'] = dfAtts.GHI.values[0]
    mParams['dist_desal_plant'] = dfAtts.DesalDist.values[0] / 1000
    mParams['dist_water_network'] = dfAtts.WaterNetworkDistance.values[0] / 1000
    mParams['dist_power_plant'] = dfAtts.PowerPlantDistance.values[0] / 1000

    # update json file
    try:
        helpers.json_update(data=mParams, filename=cfg.map_json)
    except FileNotFoundError:
        helpers.initialize_json(data=mParams, filename=cfg.map_json)

def _generateMarkdown(theme, atts):
    ''' generate the markdown to be returned for the current theme '''
    # TODO: something more elegant than try..except for formatted values that crash on None
    # handle the standard theme layers (all cases)
    mdown = f"### Site properties near {atts['weatherFile']['properties'].get('City').replace('[','(').replace(']', ')')}, {atts['weatherFile']['properties'].get('State')}\n"
    mdown += f"#### Closest desalination plant name: {atts['desalPlants']['properties'].get('Project_Na')}\n"
    
    desal = atts['desalPlants']['properties']
    try:
        mdown += f"Capacity: {desal.get('Capacity__'):,.0f} m3/day\n\n"
    except:
        mdown += f"Capacity: -\n\n"    
    mdown += f"Capacity: {desal.get('Capacity__'):,.1f} m3/day\n\n"
    mdown += f"Technology: {desal.get('Technology')}\n\n"
    mdown += f"Feedwater:  {desal.get('Feedwater')}\n\n"
    mdown += f"Customer type: {desal.get('Customer_t')}\n\n"
    
    power = atts['powerPlants']['properties']
    mdown += f"###### Closest power plant: {power.get('Plant_name')}\n\n"
    mdown += f"Primary generation: {power.get('Plant_prim')}\n\n"
    try:
        mdown += f"Production: {power.get('Plant_tota'):,.0f} MWh\n\n"
    except:
        mdown += f"Production: -\n\n"

    mdown += f"Total Annual Production: {power.get('Plant_annu'):,.1f} GJ\n\n"
    try:
        mdown += f"Exhaust Residual Heat: {power.get('Exhaust_Re'):,.0f} MJ (91 C < T < 128 C)\n\n"
    except:
        mdown += f"Exhaust Residual Heat: -\n\n"
    try:
        mdown += f"Condenser Heat: {power.get('Total_Pote'):,1f} MJ (29 C < T < 41 C)\n\n"
    except:
        mdown += f"Condenser Heat: -\n\n"

    water = atts['waterPrice']['properties']
    mdown += f"##### Water Prices\n\n"
    try:
        mdown += f"Residential price: ${water.get('Water_bill'):,.2f}/m3\n\n"
    except:
        mdown += f"Residential price: -\n\n"
    mdown += f"Residential provider: {water.get('Utility_na')}\n\n"
    # add legal info
    mdown += f"##### Regulatory Framework\n\n"
    state = atts['county']['properties'].get('STATEAB')
    #link = f'<a href="{regulatory_links[state]}" target="_blank">{state}</a>'
    link = f"[Regulatory information for {state}]({regulatory_links.get(state)})"
    mdown += link + '\n\n'
    return mdown

def _updateMapJson(atts, pnt):

    mParams = dict()
    # update dictionary
    wx = atts['weatherFile']['properties']
    mParams['file_name'] = str(cfg.weather_path / wx.get('filename'))
    mParams['water_price'] = atts['waterPrice']['properties'].get('Water_bill')
    # mParams['water_price_res'] = dfAtts.Avg_F5000gal_res_perKgal.values[0]
    mParams['latitude'] = pnt[0]
    mParams['longitude'] = pnt[1]
    # mParams['dni'] = dfAtts.ANN_DNI.values[0]
    # mParams['ghi'] = dfAtts.GHI.values[0]
    desal_pt = [atts['desalPlants']['properties'].get('Latitude'),atts['desalPlants']['properties'].get('Longitude')]
    mParams['dist_desal_plant'] = _calcDistance(pnt,desal_pt)
    power_pt = [atts['powerPlants']['geometry']['coordinates'][1],atts['powerPlants']['geometry']['coordinates'][0]]
    #mParams['dist_power_plant'] = _calcDistance(pnt,power_pt)

    # mParams['dist_water_network'] = dfAtts.WaterNetworkDistance.values[0] / 1000


    mParams['state'] = wx.get('State')
    mParams['water_price'] = atts['waterPrice']['properties'].get('Water_bill')
    # mParams['water_price_res'] = dfAtts.Avg_F5000gal_res_perKgal.values[0]
    # mParams['dni'] = dfAtts.ANN_DNI.values[0]
    # mParams['ghi'] = dfAtts.GHI.values[0]
    # mParams['dist_desal_plant'] = dfAtts.DesalDist.values[0] / 1000
    # mParams['dist_water_network'] = dfAtts.WaterNetworkDistance.values[0] / 1000
    # mParams['dist_power_plant'] = dfAtts.PowerPlantDistance.values[0] / 1000

    # dump to config file
        # update json file
    print('Writing out JSON...')
    try:
        helpers.json_update(data=mParams, filename=cfg.map_json)
    except FileNotFoundError:
        helpers.initialize_json(data=mParams, filename=cfg.map_json)

if __name__ == '__main__':
    ''' main method for testing/development '''
    _setup_logging(False)
    logging.info('starting test...')
    #ptCoords = (-73.988033,41.035572) # matches two counties
    #ptCoords = (-119.0, 26.0) # doesn't match any counties
    #ptCoords = (34.0, -115.0) # matches one county
    ptCoords = (37.0,-110.0)
    lookupLocation(ptCoords)
    #print(getClosestPlants(ptCoords))
    #print(_calcDistance([0,0],[1,1]))
    ptCoords = (34.0, -115.0) # matches one county
    lookupLocation(ptCoords)
