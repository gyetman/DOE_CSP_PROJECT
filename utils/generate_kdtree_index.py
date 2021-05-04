import argparse
import fiona
import logging
import numpy as np
import pickle
import sys

from pathlib import Path
from shapely.geometry import Polygon, shape
from shapely.geos import geos_version
from shapely import speedups
from scipy.spatial import KDTree

# patch module-level attribute to enable pickle to work
#kdtree.node = kdtree.KDTree.node
#kdtree.leafnode = kdtree.KDTree.leafnode
#kdtree.innernode = kdtree.KDTree.innernode

# handle large set of points
sys.setrecursionlimit(20000)

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

def build_index(shp):
    '''
    Builds an index for the supplied point geometry. 
    Supports geojson and shapefile inputs. 
    @param [shp]: full path to shp or geojson file
    '''
    if speedups.available:
        logging.debug('Enabling GEOS speedups.')
        speedups.enable()
    else:
        logging.info('GEOS speedups not available.')

    logging.info(f'Opening {Path(shp).name} for reading.')
    with fiona.open(shp,'r') as source:
        logging.info(f'Generating indexes for {len(source):,} points.')
        features = list(source)
        logging.info('converting points to numpy array')
        pts = np.asarray([feat['geometry']['coordinates'] for feat in features])
        try:
            tree = KDTree(pts)

        except Exception as e:
            logging.error('Error generating spatial index.')
            print(e)
            sys.exit(1)
        return tree
 
def write_index(idx, fullPath):
    '''
    Writes out the index to the specified path. 
    @param [idx]: rtree object
    @param [fullPath]: Path where object should be written
    '''
    logging.debug(f'Writing out file {fullPath}')

    with open(fullPath, 'wb') as f:
        pickle.dump(idx,f)


if __name__ == '__main__':
    # parse input args and check that they exist
    parser = argparse.ArgumentParser(
        description='Build kdtree for spatial data (points)')
    parser.add_argument('spatial_file',
        help='input spatial file (shp or json)')
    parser.add_argument('-v', '--verbose', 
        action='store_true',
        help='Log more verbosely.')
    args = parser.parse_args()
    _setup_logging(args.verbose)
    inFile = Path(args.spatial_file)
    if not inFile.exists():
        logging.error(f'Input file:\n{inFile}\nnot found!')
        sys.exit(1)
    logging.debug(args)
    # build the index
    idx = build_index(args.spatial_file)
    logging.info('Writing index...')
    outPath = inFile.resolve().parent
    write_index(idx,outPath/(inFile.stem + '.kdtree'))
