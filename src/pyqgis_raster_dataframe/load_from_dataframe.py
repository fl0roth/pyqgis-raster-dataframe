from pathlib import Path
from qgis.core import QgsProject, QgsRasterLayerTemporalProperties, QgsDateTimeRange
from qgis.utils import iface
from qgis.PyQt.QtCore import QDateTime
import pandas as pd
from geopathfinder.naming_conventions.yeoda_naming import YeodaFilename
import rasterio


def load_layers(raster_df, time_column=None, group_columns=None, qml_column=None):
    """
    Load, group and style QGIS layers based on a DataFrame containing details of raster files.

    Parameters
    ----------
    raster_df: pd.DataFrame
        DataFrame containing details of raster files including a "filepaths" column.
    time_column: str, optional
        DataFrame column representing the datetime of a raster file (default: None).
    group_columns: list, optional
        List of DataFrame columns to be used to group the layers within the QGIS project (default: None).
    qml_column: str, optional
        DataFrame column which includes the path to the QML file to be applied as style (default: None).
    """
    
    dt_format = '%Y-%m-%d'
    if 'filepaths' not in raster_df.columns:
        raise Exception("The passed DataFrame needs to contain a column called 'filepaths'.")
    
    group_dict = dict()
    for i, raster_details in raster_df.iterrows():
        # create groups based on DataFrame
        if group_columns is not None:
            root = QgsProject.instance().layerTreeRoot()
            for i, col in enumerate(group_columns):
                gn = get_group_name(raster_details, col, dt_format)
                
                if i == 0:
                    if gn not in group_dict:
                        child_group = root.addGroup(gn)
                        group_dict[gn] = child_group
                    else:
                        child_group = group_dict[gn]
                else:
                    prev_cols = group_columns[:i]
                    prev_groups = [get_group_name(raster_details, c, dt_format) for c in prev_cols]
                    parent_key = "/".join(prev_groups)
                    child_key = parent_key + "/" + gn
                    if child_key not in group_dict:
                        child_group = group_dict[parent_key].addGroup(gn)
                        group_dict[child_key] = child_group
                    else:
                        child_group = group_dict[child_key]
                    
            # create QGIS layer
            if not raster_details.filepaths.exists():
                raise FileNotFoundError("File " + raster_details.name + " does not exist.")
            rlayer = iface.addRasterLayer(raster_details.filepaths.as_posix(), raster_details.filepaths.with_suffix('').name,
                                          "gdal")
            if not rlayer.isValid():
                print('Layer not valid: ' + raster_details.filepaths.with_suffix('').name)

            # add time properties
            if time_column is not None:
                raster_df['day'] = raster_df[time_column].dt.strftime(dt_format)
                dt1 = QDateTime.fromString(raster_details[time_column].strftime('%y%m%d'), 'yyyyMMdd')
                dt2 = dt1.addDays(10)
                rlayer.temporalProperties().setMode(QgsRasterLayerTemporalProperties.ModeFixedTemporalRange)
                time_range = QgsDateTimeRange(dt1, dt2)
                rlayer.temporalProperties().setFixedTemporalRange(time_range)
                rlayer.temporalProperties().setIsActive(True)

            # apply style sheet
            if qml_column is not None:
                qml_path = raster_details[qml_column]
                rlayer.loadNamedStyle(qml_path.as_posix())
                rlayer.triggerRepaint()
            
            # move layer to group
            rlyr_node = root.findLayer(rlayer.id())
            clone_lyr = rlyr_node.clone()
            parent_lyr = rlyr_node.parent()
            child_group.insertChildNode(0, clone_lyr)
            parent_lyr.removeChildNode(rlyr_node)
        
        # close layer
        rlayer = None
        clone_lyr = None
        parent_lyr = None

    print('Layers loaded.')
        
        
def get_group_name(fname, col, dtf):
    """Get group name from filename detail."""
    if col == 'day':
        return fname.datetime_1.strftime(dtf)
    else:
        return fname[col]
        
    
def filepaths2dataframe(fpath_list, filenaming_class):
    """
    Puts a list of files into a DataFrame and add the filenaming details as columns.
    
    Parameters
    ----------
    fpath_list: list
        List of paths to GeoTiff files as string or pathlib.Path.
    filenaming_class: geopathfinder.file_naming.SmartFilename
        Filenaming convention class from geopathfinder.
        
    Returns
    -------
    df: pd.DataFrame
        DataFrame containing the path and the filenaming details of the input raster files.
    """
    
    parts_list = list()
    for spath in fpath_list:
        fname = filenaming_class.from_filename(spath.name, convert=True)
        fn_parts = vars(fname.obj)
        fn_parts['filepaths'] = spath
        parts_list.append(fn_parts)
    df = pd.DataFrame.from_records(parts_list)
    if len(fpath_list) != len(df):
        raise Exception('Dataframe creation failed.')

    return df


def add_metadata_to_dataframe(df, meta_field):
    """Adds a content of a metadata field to the passed dataframe."""
    meta_values = list()
    for fpath in df['filepaths']:
        with rasterio.open(fpath, 'r') as src:
            tags = src.tags()
        if meta_field in tags:
            meta_values.append(tags[meta_field])
        else:
            raise ValueError(meta_field + " not found in metadata.")
        
    df[meta_field] = meta_values
    return df
    
    
def get_yeoda_dataframe(root_path: Path, grid_name: str, version_list=None, tile_list=None):
    """Retrieve dataframe based on datacube root path in the Yeoda Filenaming convention."""
    if version_list is None:
        version_list = ['*']
    if tile_list is None:
        tile_list = ['*']
    
    file_list = list()
    for data_version in version_list:
        for tile in tile_list:
            tile_path = root_path / data_version / grid_name / tile
            file_list.extend(list(tile_path.glob('*.tif')))
            
    return filepaths2dataframe(file_list, filenaming_class=YeodaFilename)
