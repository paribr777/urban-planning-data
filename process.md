## IBM Granite Model
- Fine-tuned Earth Observation Foundation Model (EOFM)
- Predicts LST from Harmonized Landsat and Sentinel-2 (HLS) L30 optical satellite imagery and ERA5-Land near-surface air temperature 
- (https://github.com/ibm-granite/granite-geospatial-land-surface-temperature)

## HLS L30 Data 
- TIF Files - 30m resolution
- 9 layers/bands per granule
  1) B02, B03, B04 - RGB Visible bands
  2) B05 - NIR Band
  3) B06, B07 - Short Wavelength Infrared Bands
  4) B10, B11 - Thermal Infrared Bands from TIRS
  5) Fmask - cloud mask details (to filter out cloud coverage while processing)
- Using 6 HLS Bands for input, as per model specifications

## ERA5 Data 
- 2020-2026 ERA5 Thermal Data (netcdf format)

## Process
# Downloading Data:
- Used cloud filter to 35% and downloaded ERA5 andHLS data for monsoon and post-monsoon seasons. Sampled and visually analysed the HLS bands data of 18 cities based on
    - 4 seasons (summer, winter, monsoon, post monsoon)
    - Years (2022-2026)

# Preprocessing Data
STACKED INPUT:
- Organised data
- Cleaned ERA5 layers
- Normalised values and scaled appropriately for improved granite IBM model performance.
- Stacked 6 HLS bands + 1 ERA5 Thermal band

TARGET LST / GROUND TRUTH:
- Calculated ground truth aka LST from given data

# Predictions
- Obtained LST values and raster predictions for all 18 cities and seasons, plotted ground truth vs prediction 𝑅2
- Plotted metrics ( score, Mean Absolute Error and RMSE) with difference plots and error distribution histogram.
  
# Postprocessing 
- Utilised mean-subtracted (anomaly) metrics and a standard thermal colour scale for valid comparisons 
- Approximated temperature values on obtained prediction rasters into bins 2 degrees C wide.
- Cropped out a margin of 8px from plots to reduce edge errors. Spatially aggregated 7x7, resulting in 210m resolution as opposed to 30m raw HLS (trade off between improved metrics and spatial resolution) → greatly improved 𝑅2 score and decreased MAE by ~0.1-0.5 degrees C

# Vanilla Model Results
- Further analysed model’s biases and areas where errors might pop up
- Average approximate baseline performance of IBM LST model (not finetuned) so far (for all 18 cities):
      - 𝑅2 score → 0.4 - 0.7
      - MAE (in °C) → 0.6 - 2
      - RMSE (in °C) → 2.15

# Future Predictions
- Created code script to make seasonal future prediction (projection) rasters + LST for years 2028, 2031, 2034, 2037 & 2040, using:
      - Model predicted rasters
      - Pan India CMIP6 Delta values (Moderate Emissions Scenario)
      - Local Urban Heat Island values (from ground truths)
      - Baseline spatial intercept for cities (from ground truths)
- Plotted future rasters + LST based on 4 seasons for 5 years (accuracy unverifiable)

# Alignment and Validation
- Sentinel 2 data for the same bounding boxes (18 cities) to compare and contrast alignment 
- Obtain LULC (Land use land cover) classifications for each city based on sentinel data

# Finetuning (Srinagar Test)
- Fit and finetune vanilla IBM Granite LST model on Srinagar existing raster ground truths to optimise weights, as a test to see if the fitting pipeline is working
- Complete training, obtain new Srinagar Finetunef predictions compare and contrast to check improvements (vanilla model vs finetuned model predictions) → no improvements, performs slightly worse due to high bias, will proceed to improve training and validation splits on 8-9 cities now

# Bigger scale finetuning
- Built pipeline to train on 9 out of 18 widespread cities and obtain predictions for remaining 9 cities to test performance

