import app_config as cfg 
import json
import logging
import pickle
import sys
import fiona
import numpy as np

from pathlib import Path
from scipy.spatial import KDTree
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
    'desalPlants':{'point':cfg.gis_query_path / 'USAWeatherStations.shp'},
    'powerPlants':{'point':cfg.gis_query_path / 'USAWeatherStations.shp'},
    'waterPrice':{'point':cfg.gis_query_path / 'USAWeatherStations.shp'},
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
    _setup_logging(verbose=True)

    # check that coord is lat/long 
    logging.debug('Checking point coords...')
    if not -180 < float(pt[0]) < 180:
        logging.error('longitude out of bounds, check point location')
        return None
    if not -90 < float(pt[1]) < 90:
        logging.error('latitude out of bounds, check point location')
        return None

    # get layer dictionary based on theme name
    themeLyrs = _getThemeLayers(mapTheme)
    logging.info(f'finding locations of {len(themeLyrs)} layers.')

    # parse the dictionary, getting intersecting / closest features for each
    closestFeatures = dict()
    logging.info('Performing intersections')
    for key, value in themeLyrs.items():
        if 'point' in value.keys():
            closestFeatures[key] = _findClosestPoint(pt,value['point'])
        elif 'poly' in value.keys():
            closestFeatures[key] = _findIntersectFeatures(pt,value['poly'])

def _getThemeLayers(mapTheme):
    ''' return the list of layers to search based on the map theme '''
    # TODO: read the lists from a JSON file using the helper module

    if mapTheme.lower() == 'default':
        return defaultLayers
    elif mapTheme.lower() == 'restrictions':
        return {**defaultLayers, **restrictionsLayers}

def _findIntersectFeatures(pt,intersectLyr):
    ''' find features in the supplied layers that intersect the provided point 
    @param [pt]: list or tuple of point coordinates in latitude / longitude (x,y)
    @param [lyrs]: list or tuple of polygon layers to find the point
    '''
    # make the point a geometry
    queryPoint = (pt[0], pt[1],pt[0]+.1,pt[1]+.1)
    print(queryPoint)
    # open each layer and find the matches
    logging.info(f'Finding intersections with {intersectLyr}...')
    rtreeFile = Path(f'{intersectLyr.parent}/{intersectLyr.stem}')
    if rtreeFile.exists:
        logging.info('Using pre-built rtree index')
        idx = index.Index(str(rtreeFile.absolute()))
        possibleMatches = [x for x in idx.intersection(queryPoint)]
        print(len(possibleMatches))
    else:
        logging.info('No index found, using slow method')
        # TODO: open & find with slow method
    
    if possibleMatches is None:
        return None
    elif len(possibleMatches) > 1:
        # call the method to do polygon intersection
        print('multiple matches')
    else:
        # single match concept
        print('single match')
        print(possibleMatches)

def _findClosestPoint(pt,lyr,maxDist=150):
    ''' find the closest point or line to the supplied point
    @param [pt]: list or tuple of point coordinates in latitude / longitude (x,y)
    @param [closestLayers]: list of point or line layers
    ''' 
    queryPoint = np.asarray(pt)
    # open each layer and find the matches
    logging.info(f'Finding closes point for {lyr}...')
    # check for kdtree
    kdFile = Path(f'{lyr.parent}/{lyr.stem}.kdtree')
    if kdFile.exists:
        logging.info('using pre-built index')
        with open(kdFile,'rb') as f:
            idx = pickle.load(f)
            closestPt = idx.query(queryPoint)
            logging.info(closestPt)

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


def _paramHelper(dfAtts):
    ''' helper method to write out parameters. Uses the solar dataframe point ID 
    to write out map paramers to  '''
    #TODO: object based in likely to be dict, not pandas data frame! 
    # update the code to reflect this
    logging.debug('updating model params')
    mParams = dict()
    # update dictionary
    weatherPath = cfg.base_path
    mParams['file_name'] = str(weatherPath / 'SAM_flatJSON' / 'solar_resource' / dfAtts.filename.values[0])
    mParams['county'] = dfAtts.CountyName.values[0]
    mParams['state'] = dfAtts.StatePosta.values[0]
    mParams['water_price'] =  dfAtts.WaterPrice.values[0]
    mParams['water_price_res'] = dfAtts.Avg_F5000gal_res_perKgal.values[0]
    mParams['latitude'] = dfAtts.CENTROID_Y.values[0]
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


if __name__ == '__main__':
    ''' main method for testing/development '''
    _setup_logging(False)
    logging.info('starting test...')
    ptCoords = (-116.6,33.2)
    lookupLocation(ptCoords)