import argparse
import logging
import fiona
import sys

from pathlib import Path

from shapely.strtree import STRtree
from shapely.geometry import Point, Polygon, shape, box as shapely_box
from shapely.geos import geos_version
from shapely import speedups, wkt

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
    Builds an index for the supplied polygon geometry. 
    Supports geojson and shapefile inputs. 
    @param [shp]: full path to shp or geojson file
    '''
    if speedups.available:
        logging.debug('Enabling GEOS speedups.')
        speedups.enable()
    else:
        logging.info('GEOS speedups not available.')

    bboxes = []
    logging.info(f'Opening {Path(shp).name} for reading.')
    with fiona.open(shp,'r') as source:
        logging.info('Generating indexes for polygons.')
        for item in source:
            print(item['geometry'].keys())
            # need to create a geomtry from the coords in the 
            # geometry, then coerce to bbox
            geom = Polygon(shape(item['geometry']))
            box = shapely_box(*geom.bounds)
            setattr(box, 'uid', item['id'])
            bboxes.append(box)

    logging.debug('Writing out file.')


if __name__ == '__main__':
    # parse input args and check that they exist
    parser = argparse.ArgumentParser(
        description='Build rtree for spatial data (polygons)')
    parser.add_argument('spatial_file',
        help='input spatial file (shp or json)')
    parser.add_argument('-v', '--verbose', action='store_true',
        help='Log more verbosely.')
    args = parser.parse_args()
    _setup_logging(args.verbose)
    if not Path(args.spatial_file).exists():
        logging.error(f'Input file:\n{args.spatial_file}\nnot found!')
        sys.exit(1)
    logging.debug(args)

    build_index(args.spatial_file)

