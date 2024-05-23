# yeoda-light-qgis
Connecting yeoda and QGIS functionalities.

Script to load, group and style raster layers based on a passed DataFrame in QGIS using the `load_layers()` function. This aims for a (processing) plugin in the future.

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

Now, one can load the required raster files into a pandas `DataFrame` using the Yeoda filenaming convention of 
`geopathfinder` as columns and having a `filepaths` column keeping the filepath of each input raster. This can be 
achieved by tools from the `yeoda`, `yeoda-light` package or some simple Python commands. By passing a list of column 
names to the `load_layers()` function, the input rasters are loaded into QGIS and grouped by these columns. Further, 
a style can be passed and the QGIS temporal control (developed by [marxt](https://github.com/marxt)) can be used.
