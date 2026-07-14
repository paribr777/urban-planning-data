import os
import fiona
import geopandas as gpd
from shapely.geometry import shape

# 1. Define file paths
mbtiles_path = r"C:\Users\Dell\Downloads\osm-2020-02-10-v3.11_india_mysore (1).mbtiles"
EPSG_MYSORE_METRIC = "EPSG:32643"  # UTM Zone 43N for precise sq km calculations
MYSURU_TOTAL_AREA_SQKM = 341.0     # Target official area

# 2. Discover available layers
try:
    available_layers = fiona.listlayers(mbtiles_path)
    print(f"Found layers in MBTiles: {available_layers}\n")
except Exception as e:
    print(f"Error reading MBTiles: {e}")
    available_layers = []

# 3. Load and Isolate layers
layers_to_load = ['landuse', 'water', 'building', 'landcover']
gdfs = {}

for layer in layers_to_load:
    if layer in available_layers:
        print(f"Loading layer: {layer}...")
        try:
            gdf = gpd.read_file(mbtiles_path, layer=layer)
            gdf = gdf[gdf.geometry.type.isin(['Polygon', 'MultiPolygon'])]
            if not gdf.empty:
                gdfs[layer] = gdf.to_crs(EPSG_MYSORE_METRIC)
                print(f"-> Loaded {len(gdf)} features.")
        except Exception as e:
            print(f"-> Error loading layer {layer}: {e}")

# 4. Classify raw layers into base categories
# We use geodataframe lists to group geometries before fixing overlaps
infra_geoms = []
green_geoms = []
water_geoms = []
empty_geoms = []

# OpenMapTiles Classification mappings
green_classes = ['forest', 'grass', 'park', 'wood', 'fell', 'golf_course', 'meadow', 'vineyard', 'orchard', 'tundra']
infra_classes = ['commercial', 'industrial', 'residential', 'retail', 'railway', 'quarry', 'military', 'suburban', 'urban']
empty_classes = ['brownfield', 'construction', 'landfill', 'beach', 'sand', 'rock', 'scree']

# Process landuse
if 'landuse' in gdfs:
    lu = gdfs['landuse']
    if 'class' in lu.columns:
        infra_geoms.append(lu[lu['class'].isin(infra_classes)])
        green_geoms.append(lu[lu['class'].isin(green_classes)])
        empty_geoms.append(lu[lu['class'].isin(empty_classes)])

# Process landcover (CRITICAL: This is where OpenMapTiles hides wood/grass/crop fields)
if 'landcover' in gdfs:
    lc = gdfs['landcover']
    if 'class' in lc.columns:
        green_geoms.append(lc[lc['class'].isin(['wood', 'forest', 'grass', 'crop', 'tundra'])])
        empty_geoms.append(lc[lc['class'].isin(['sand', 'rock', 'ice', 'barren'])])

# Process buildings
if 'building' in gdfs:
    infra_geoms.append(gdfs['building'])

# Process water
if 'water' in gdfs:
    water_geoms.append(gdfs['water'])

# Merge categorized data into 4 clean GeoDataFrames
def safe_concat(gdf_list):
    valid_gdfs = [g for g in gdf_list if g is not None and not g.empty]
    if valid_gdfs:
        return gpd.GeoDataFrame(gpd.pd.concat(valid_gdfs, ignore_index=True), crs=EPSG_MYSORE_METRIC)
    return gpd.GeoDataFrame(geometry=[], crs=EPSG_MYSORE_METRIC)

gdf_infra = safe_concat(infra_geoms)
gdf_green = safe_concat(green_geoms)
gdf_water = safe_concat(water_geoms)
gdf_empty = safe_concat(empty_geoms)

# 5. Fix Overlaps (Priority Cascade)
# Water and Buildings take ultimate priority. Landuse/Landcover fill the rest.
print("\nResolving spatial overlaps...")

# Dissolve geometries to get pure surface footprints without overlapping records
geom_water = gdf_water.geometry.unary_union
geom_infra = gdf_infra.geometry.unary_union

# Green space cannot overlap with water or buildings
geom_green = gdf_green.geometry.unary_union
if geom_green and not geom_green.is_empty:
    if geom_water and not geom_water.is_empty:
        geom_green = geom_green.difference(geom_water)
    if geom_infra and not geom_infra.is_empty:
        geom_green = geom_green.difference(geom_infra)

# Empty land cannot overlap with any of the above
geom_empty = gdf_empty.geometry.unary_union
if geom_empty and not geom_empty.is_empty:
    for master_geom in [geom_water, geom_infra, geom_green]:
        if master_geom and not master_geom.is_empty:
            geom_empty = geom_empty.difference(master_geom)

# 6. Calculate Areas (Converted to sq km)
areas = {
    "Infrastructure": (geom_infra.area / 1_000_000) if geom_infra else 0.0,
    "Greenery": (geom_green.area / 1_000_000) if geom_green else 0.0,
    "Water Bodies": (geom_water.area / 1_000_000) if geom_water else 0.0,
    "Empty Land": (geom_empty.area / 1_000_000) if geom_empty else 0.0
}

mapped_footprint = sum(areas.values())

# 7. Normalize metrics to Mysuru's true 341 sq km boundary scale
print("\n" + "="*40)
print("     MYSURU LAND DISTRIBUTION METRICS   ")
print("="*40)
if mapped_footprint > 0:
    print(f"Raw Mapped Footprint in MBTiles: {mapped_footprint:.2f} sq km")
    print(f"Targeting Mysuru Administration Boundary: {MYSURU_TOTAL_AREA_SQKM} sq km\n")
    
    # Calculate proportions based on what was mapped, scaled to full city size
    for classification, raw_area in areas.items():
        ratio = (raw_area / mapped_footprint) * 100
        scaled_area = (ratio / 100) * MYSURU_TOTAL_AREA_SQKM
        print(f"- {classification:<15}: {scaled_area:10.2f} sq km ({ratio:6.2f}%)")
        
    print("-"*40)
    print(f"Total Scaled Footprint : {MYSURU_TOTAL_AREA_SQKM:10.2f} sq km")
else:
    print("Error: No geometries matched. Please check your MBTiles geographic coverage bounds.")
print("="*40)
