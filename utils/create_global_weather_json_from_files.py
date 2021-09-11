import glob
import json
from pathlib import Path
search = r'/Users/gyetman/DOE/DOE_CSP_PROJECT/SAM_flatJSON/solar_resource/*.csv'

HEADER = {
    "type": "FeatureCollection",
    "name": "global_weather_file",
    "crs": { "type": "name","properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" }}
}

flist = glob.glob(search)

print(f'{len(flist)} csv files')

with open('/Users/gyetman/DOE/DOE_CSP_PROJECT/GISQueryData/global_weather_file.geojson', 'r') as f:
    data = json.load(f)

file_names = set()
for record in data['features']:
    file_names.add(record['properties']['filename'])

print(len(file_names))

new_file_names = set()
for f in flist:
    new_file_names.add(Path(f).name)

removed = file_names - new_file_names

for record in data['features']:
    if record['properties']['filename'] in removed:
        data['features'].remove(record)

with open('./new_weather_file.geojson', 'w') as f:
    f.write(json.dumps(data))

print('...done')