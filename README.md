# pyqgis-raster-dataframe
QGIS layers from pandas DataFrame.

Script to load, group and style raster layers based on a passed DataFrame in QGIS using the `load_layers()` function. 
This aims for a (processing) plugin in the future!

## Installation
Create conda environment with Python 3.9:

    mamba create -n qgis python=3.9

Install `QGIS` and `geopandas` to the environment using mamba:

    conda activate qgis
    mamba install -c conda-forge qgis rioxarray

Install `geopathfinder` using pip:

    pip install geopathfinder

## Usage
When the installed conda environment is activated, you can start QGIS by running:

    qgis

Now, one can load the input raster files into a pandas `DataFrame` (`filepaths` column containing the input path as 
Python Path object is required!). This can be done by the `filepaths2dataframe` or `get_eo_dataframe` function for now. 
The `load_layers()` function will load the raster layers to QGIS with the additional option to group the layers based on 
the columns of the DataFrame. Further, a style can be passed and the QGIS temporal control 
(developed by [marxT](https://github.com/marxt)) can be used.

    from yeoda_light_qgis.yeoda_light_qgis import filepaths2dataframe, load_layers
    
    list_of_files = [...]  # list of files following the Yeoda filenaming convention (available in geopathfinder)
    df = filepaths2dataframe(list_of_files)
    load_layers(eo_df=df, group_fields=['var_name', 'day'])

A script, which makes use of the yeoda-light-qgis functionality should be put to the same folder as the 
load_from_dataframe.py script and is expected to be called within the Python Console of QGIS.
