import rasterio as rio
from rasterio.windows import Window

gtiff = '/users/gyetman/DOE/DOE_CSP_PROJECT/GISQueryData/DNI.tif'

pnt = 38.75,-112.0

with rio.open(gtiff) as dataset: 
    px, py = dataset.index(pnt[0],pnt[1])
    wdw = Window(px, py, 2,2)
    test = dataset.read(1, window=Window(px,py,2,2))

    print(test.shape)
    print(test)
