import argparse
import fiona
import pickle
import rtree
from pathlib import Path
from shapely import speedups
from shapely.geometry import shape


if speedups.available:
    speedups.enable()

def buildIndex(inFile,fileType):
    ''' Builds an rtree index and stores it in the same folder as the file '''
    # hey, Path is cool! 
    # print(inFile.parent)
    # print(inFile.name)
    # print(inFile.suffix)
    # print(inFile.stem)
    print('Creating index...')
    idx = rtree.index.Index('{}/{}'.format(inFile.parent,inFile.stem))
    print('Updating index...')
    # open the file and build the rtree
    with fiona.open(inFile) as layer:
        for feat in layer:
            fid = int(feat['id'])
            geom = shape(feat['geometry'])
            idx.insert(fid,geom.bounds)
            
    # persist the rtree to disk
    print('Created index for {}'.format(inFile.name))
    print('Index bounding box:\n{}'.format(idx.bounds))
    idx.close()

    
    # print('Writing {} to disk.'.format(outFile))
    # with open(outFile,'wb') as f:
    #     pickle.dump(index,f)


    # test by opening
    print('testing...')
    idxIn = rtree.index.Index('{}/{}'.format(inFile.parent,inFile.stem))
    print(idxIn.bounds)

if __name__ == '__main__':
    ''' Parse arguments and check inputs '''
    parser = argparse.ArgumentParser(
            description = "Builds rtree indexes for input polygon shapefile (.shp) or geojson.")
    parser.add_argument(
        'input',
        help='Input file (full path, point to .shp for shapefile.)'
    )
    parser.add_argument(
        '--type',
        dest='fileType',
        default='shapefile',
        help='Input file type: shapefile or geojson'
    )

    args = parser.parse_args()
    # check that input exists 
    filePath = Path(args.input).resolve() # resolve gets the absolute path
    if not filePath.is_file():
        print('\nFile {} not found!\n'.format(args.input))
    else:
        buildIndex(filePath, args.fileType)
