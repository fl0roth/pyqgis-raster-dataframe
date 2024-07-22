# pyqgis-raster-dataframe
QGIS layers from pandas DataFrame.

Script to load, group and style raster layers based on a passed DataFrame in QGIS using the `load_layers()` function. 
This aims for a (processing) plugin in the future!

## Installation
Create "pyqgis" conda environment using the provided YAML file:

    mamba env create -f mamba_env.yml
    conda activate pyqgis

Install `pyqgis-raster-dataframe` from source:

    pip install -e .

## Usage
When the installed conda environment is activated, you can start QGIS by running:

    qgis

Now, one can load the input raster files into a pandas `DataFrame` (`filepaths` column containing the input path as 
Python Path object is required!). This can be done by the `filepaths2dataframe` or `get_yeoda_dataframe` function for now. 
The `load_layers()` function will load the raster layers to QGIS with the additional option to group the layers based on selected columns of the DataFrame. 
Optionally, a column can be defined containing style details as well as a time column can be passed to connect to the QGIS temporal control 
(support developed by [marxT](https://github.com/marxt)) can be used.

    from yeoda_light_qgis.yeoda_light_qgis import filepaths2dataframe, load_layers
    
    list_of_files = [...]  # list of files following the Yeoda filenaming convention (available in geopathfinder)
    df = filepaths2dataframe(list_of_files, filenaming_class=YeodaFilenaming)
    load_layers(raster_df=df, group_columns=['var_name', 'day'])

## Note
This package was create using cookiecutter and the following skeleton: https://github.com/TUW-GEO/cookiecutter-tuw-package

