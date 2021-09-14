import glob
import json
import fiona
# import app_config as cfg
from pathlib import Path
from importlib.machinery import SourceFileLoader

SEARCH_PATTERN = r'../SAM_flatJSON/solar_resource/*.csv'

# read the schema from the existing weather index file, 
# which is in the GISQUERY folder. This should be read from
# the config file, but hard coded here. 

with fiona.open('../GISQueryData/global_weather_file.geojson') as source:
    out_schema = source.schema
    print(out_schema['properties'])



wlist = glob.glob(SEARCH_PATTERN)

print(f'{len(wlist)} csv files')

rows = []

for wfile in wlist:
    meta = {}
    with open(wfile, 'r') as f:
        line = f.readline()
        for val in line.split(','):
            meta[val.strip()] = ''
        line = f.readline()
        #print(line)
        i = 0
        for item in meta:
            meta[item] = line.split(',')[i].strip()
            i+=1
        meta['filename'] = Path(wfile).name
        rows.append(meta)

print(rows[0])
print(out_schema['properties'])
print(set(out_schema['prope']) - set(rows[0].keys()))
# with open('./new_weather_file.geojson', 'w') as f:
#     f.write(json.dumps(data))

print('...done')