import os

import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Polygon

from region.p_regions.exact import PRegionsExact

# get path of build-directory
# (a little complicated but this way it works locally as well with readthedocs)
def build_path():
    directory = os.path.abspath(os.path.dirname(__file__))
    while "source" not in os.listdir(directory):  # move to doc directory
        directory = os.path.dirname(directory)
    doc_content = os.listdir(directory)
    doc_content.remove('source')
    directory = os.path.join(directory, doc_content[0])
    subdirs = os.listdir(directory)
    for d in subdirs:
        d_abs = os.path.join(directory, d)
        if any([f.endswith(".html") for f in os.listdir(d_abs)]):
            directory = d_abs
            break
    directory = os.path.join(directory, "users/p-regions")
    return directory

# function for saving image
def save_image(gdf, column, fname):
    fname = os.path.join(build_path(), fname)
    gdf.plot(column=column, cmap='Blues')
    plt.gca().invert_yaxis()
    plt.gca().set_axis_off()
    plt.savefig(fname, bbox_inches='tight')

# define input
geometry = [
    Polygon([(x, y),
             (x, y+1),
             (x+1, y+1),
             (x+1, y)]) for y in range(3) for x in range(3)
]
gdf = gpd.GeoDataFrame(
    {"values": [726.7, 623.6, 487.3,
                200.4, 245.0, 481.0,
                170.9, 225.9, 226.9]},
    geometry=geometry)

# save input as image
save_image(gdf, "values", "input.png")

# generate output and save it as image
cluster_obj = PRegionsExact()
cluster_obj.fit_from_geodataframe(gdf, "values", 2)  # we build two regions
gdf["region"] = cluster_obj.labels_
save_image(gdf, "region", "output.png")

