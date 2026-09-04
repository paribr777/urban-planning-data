## IBM Granite Model
- Fine-tuned Earth Observation Foundation Model (EOFM)
- Predicts LST from Harmonized Landsat and Sentinel-2 (HLS) L30 optical satellite imagery and ERA5-Land near-surface air temperature 
- (https://github.com/ibm-granite/granite-geospatial-land-surface-temperature)

## HLS L30 Data 
- Total 3519 TIF Files - 30m resolution
- 391 Granules (including Mysuru region)
- 9 layers/bands per granule
  1) B02, B03, B04 - RGB Visible bands
  2) B05 - NIR Band
  3) B06, B07 - Short Wavelength Infrared Bands
  4) B10, B11 - Thermal Infrared Bands from TIRS
  5) Fmask - cloud mask details (to filter out cloud coverage while processing)

## ERA5 Data 
-


## Data Processing
- Check IPYNB notebooks
