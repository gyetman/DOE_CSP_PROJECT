import app_config as cfg 
import json
import logging
import pickle
import sys
import fiona
import numpy as np

from pathlib import Path
from scipy.spatial import KDTree
from shapely.geometry import Point, Polygon, shape
from rtree import index

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

defaultLayers = {
    'county':{'poly':cfg.gis_query_path / 'county.shp'},
    'dni':{'point':cfg.gis_query_path / 'USAWeatherStations.shp'},
    'desalPlants':{'point':cfg.gis_query_path / 'Desalplants.shp'},
    'powerPlants':{'point':cfg.gis_query_path / 'PowerPlantsPotenialEnergy.shp'},
    'waterPrice':{'point':cfg.gis_query_path / 'CityWaterCosts.shp'},
    'weatherFile':{'point':cfg.gis_query_path / 'USAWeatherStations.shp'},
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

    logging.info(f'Clicked point: {pt}')

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

    return(_generateMarkdown(mapTheme,closestFeatures))
    #return(str(closestFeatures))



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
    # make the point a geometry
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
        return _findMatchFromCandidates(pt,intersectLyr,possibleMatches)

        
def _findClosestPoint(pt,lyr,maxDist=10):
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
    mParams['state'] = dfAtts['county']['properties']['STUSPS']
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
    # handle the standard theme layers (all cases)
    mdown = f"### Site properties near {atts['dni']['properties'].get('City')}, {atts['dni']['properties'].get('State')}\n"
    mdown += f"#### Closest desalination plant name: {atts['desalPlants']['properties'].get('Project_Na')}\n"
    
    desal = atts['desalPlants']['properties']
    mdown += f"Capacity: {desal.get('Capacity__')}\n\n"
    mdown += f"Technology: {desal.get('Technology')}\n\n"
    mdown += f"Feedwater:  {desal.get('Feedwater')}\n\n"
    mdown += f"Customer type: {desal.get('Customer_t')}\n\n"
    
    power = atts['powerPlants']['properties']
    mdown += f"#### Closest power plant: {power.get('Plant_name')}\n\n"
    mdown += f"Primary generation: {power.get('Plant_prim')}\n\n"
    mdown += f"Production: {power.get('Plant_tota')}\n\n"
    mdown += f"Annual production: {power.get('Plant_annu')}\n\n"

    water = atts['waterPrice']['properties']
    mdown += f"#### Water Prices"


    return mdown


if __name__ == '__main__':
    ''' main method for testing/development '''
    _setup_logging(False)
    logging.info('starting test...')
    #ptCoords = (-73.988033,41.035572) # matches two counties
    #ptCoords = (-119.0, 26.0) # doesn't match any counties
    ptCoords = (34.0, -115.0) # matches one county
    lookupLocation(ptCoords)