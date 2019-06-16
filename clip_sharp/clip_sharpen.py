import os
import sys
import time
import cv2
import rasterio
import pyproj
import numpy as np
import pycrs
import geopandas as gpd
import json

from rasterio.plot import show
from rasterio.mask import mask
from shapely.geometry import box
from fiona.crs import from_epsg


def getFeatures(gdf):
    """Function to parse features from GeoDataFrame in such
        a manner that rasterio wants them"""
    return [json.loads(gdf.to_json())['features'][0]['geometry']]


def img_check(img):
    """Fucntion to check input image is valid and it has valid CRS

    Parameters:
    img (str): path to satellite image

    Returns:
    Nothing
    """
    with rasterio.open(img) as src:
        if src.crs.is_valid and src.crs.is_projected and src.crs.is_epsg_code:
            print("Input raster is valid and has valid CRS")
        else:
            print("Input raster does not have valid CRS. Exiting the script")
            # exiting from script
            sys.exit()

def clip(img):
    """Fucntion to subset the projected raster with hardcoded coordinates

    Parameters:
    img (str): path to satellite image

    Returns:
    Nothing
    """
    with rasterio.open(img) as src:

        # Ref:https://automating-gis-processes.github.io/CSC18/lessons/L6/clipping-raster.html
        # WGS84 coordinates collected for small part of venice city
        minx, miny = 12.35, 45.44
        maxx, maxy = 12.36, 45.42

        # Converting coordinates to bounding box
        bbox = box(minx, miny, maxx, maxy)

        # Converting bbox to geodataframe
        geo = gpd.GeoDataFrame({'geometry': bbox}, index=[0], crs=from_epsg(4326))

        # Project the Polygon into same CRS as the src
        geo = geo.to_crs(crs=src.crs.data)

        coords = getFeatures(geo)

        # Clip the raster with Polygon
        out_img, out_transform = mask(dataset=src, shapes=coords, crop=True)

        out_meta = src.meta.copy()

        # Parse EPSG code
        epsg_code = int(src.crs.data['init'][5:])

        out_meta.update({"driver": "GTiff",
                    "height": out_img.shape[1],
                    "width": out_img.shape[2],
                    "transform": out_transform,
                    "crs": pycrs.parse.from_epsg_code(epsg_code).to_proj4()}
                            )

        out_tif=("/").join(img.split("/")[:-1])+"/clipped.tif"

        with rasterio.open(out_tif, "w", **out_meta) as dest:
            dest.crs = rasterio.crs.CRS({"init": "epsg:32633"})
            dest.write(out_img)

        print("Clipping is successful and ouput path is "+out_tif)

def sharpen(clip_img):
    """Fucntion to sharpen the image using high pass filter and add crs to it

    Parameters:
    clip_img (str): path to clipped image

    Returns:
    Nothing
    """

    # Sharpen the clip image with opencv laplacian function
    img = cv2.imread(clip_img, cv2.IMREAD_GRAYSCALE)
    laplacian = cv2.Laplacian(img,cv2.CV_32F,ksize=5)
    sharpen=("/").join(clip_img.split("/")[:-1])+"/sharpened.tif"
    sharpen_png=("/").join(clip_img.split("/")[:-1])+"/sharpened.tif"
    cv2.imwrite(sharpen, laplacian)
    cv2.imwrite(sharpen_png, laplacian)


    sharpen_geo=("/").join(clip_img.split("/")[:-1])+"/sharpened_geo.tif"

    # Creating georeferenced sharpen image
    with rasterio.open(clip_img) as src:
        with rasterio.open(sharpen) as sharp:
            metadata= sharp.meta
            metadata["transform"]=src.meta.pop("transform")
            metadata["crs"]=src.meta.pop("crs")
            with rasterio.open(sharpen_geo, 'w', **metadata) as dst:
                dst.write(sharp.read())

    print("Image sharpening is successful and output path is "+sharpen_geo)

def tests(img1, img2, img3):
    """Fucntion to test the clip and sharp

    Parameters:
    img1 (str): path to input satellite image
    img2 (str): path to clipped image
    img3 (str): path to sharpened image

    Returns:
    Nothing
    """
    with rasterio.open(img1) as src:
        with rasterio.open(img2) as clip:
            with rasterio.open(img3) as sharp:
                # clipped image must have smaller dimensions than input image
                if src.height > clip.height and src.width > clip.width:
                    print("clip test passed")
                else:
                    print("clip test is failed")
                # sharpened image must have single band and float 32 type
                if sharp.count == 1 and sharp.dtypes[0] == 'float32':
                    print("sharpen test is passed")
                else:
                    print("sharpen test is failed")

def main(argv):

    img = argv[0]

    img_check(img)

    clip(img)

    clip_path = ("/").join(img.split("/")[:-1])+"/clipped.tif"

    sharpen(clip_path)

    sharp_geo = ("/").join(img.split("/")[:-1])+"/sharpened_geo.tif"

    tests(img, clip_path, sharp_geo)

if __name__ == "__main__":
    main(sys.argv[1:])