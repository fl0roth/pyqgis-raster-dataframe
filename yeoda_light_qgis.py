from pathlib import Path
from qgis.core import QgsRasterLayer, QgsProject, QgsRasterLayerTemporalProperties, QgsDateTimeRange
from qgis.utils import iface
from qgis.PyQt.QtCore import QDateTime
import pandas as pd
from geopathfinder.naming_conventions.yeoda_naming import YeodaFilename
import rasterio


def load_layers(eo_df, group_fields=None, qml_path=None):
    dt_format = '%Y-%m-%d'
    eo_df['day'] = eo_df['datetime_1'].dt.strftime(dt_format)
    group_dict = dict()
    for i, eo_file in eo_df.iterrows():
        # create groups based on DataFrame
        if group_fields is not None:
            root = QgsProject.instance().layerTreeRoot()
            for i, col in enumerate(group_fields):
                gn = get_group_name(eo_file, col, dt_format)
                
                if i == 0:
                    if gn not in group_dict:
                        child_group = root.addGroup(gn)
                        group_dict[gn] = child_group
                    else:
                        child_group = group_dict[gn]
                else:
                    prev_cols = group_fields[:i]
                    prev_groups = [get_group_name(eo_file, c, dt_format) for c in prev_cols]
                    parent_key = "/".join(prev_groups)
                    child_key = parent_key + "/" + gn
                    if child_key not in group_dict:
                        child_group = group_dict[parent_key].addGroup(gn)
                        group_dict[child_key] = child_group
                    else:
                        child_group = group_dict[child_key]
                    
            # create QGIS layer
            if not eo_file.filepaths.exists():
                raise FileNotFoundError("File " + eo_file.name + " does not exist.")
            rlayer = iface.addRasterLayer(eo_file.filepaths.as_posix(), eo_file.filepaths.with_suffix('').name,
                                          "gdal")
            if not rlayer.isValid():
                print('Layer not valid: ' + eo_file.filepaths.with_suffix('').name)

            # add time properties
            dt1 = QDateTime.fromString(eo_file.datetime_1.strftime('%y%m%d'), 'yyyyMMdd')
            dt2 = dt1.addDays(10)
            rlayer.temporalProperties().setMode(QgsRasterLayerTemporalProperties.ModeFixedTemporalRange)
            time_range = QgsDateTimeRange(dt1, dt2)
            rlayer.temporalProperties().setFixedTemporalRange(time_range)
            rlayer.temporalProperties().setIsActive(True)
            
            # move layer to group
            rlyr_node = root.findLayer(rlayer.id())
            clone_lyr = rlyr_node.clone()
            parent_lyr = rlyr_node.parent()
            child_group.insertChildNode(0, clone_lyr)
            parent_lyr.removeChildNode(rlyr_node)
            
            # apply style sheet
            if qml_path is not None:
                rlayer.loadNamedStyle(qml_path.as_posix())
                rlayer.triggerRepaint()
        
        # close layer
        rlayer = None
        clone_lyr = None
        parent_lyr = None

        
    print('Layers loaded.')
        
        
def get_group_name(fname, col, dtf):
    if col == 'day':
        return fname.datetime_1.strftime(dtf)
    else:
        return fname[col]
        
    
def filepaths2dataframe(fpath_list):
    """Puts a list of files into a DataFrame and add the filenaming details as columns."""

    parts_list = list()
    for spath in fpath_list:
        fname = YeodaFilename.from_filename(spath.name, convert=True)
        fn_parts = vars(fname.obj)
        fn_parts['filepaths'] = spath
        parts_list.append(fn_parts)
    df = pd.DataFrame.from_records(parts_list)
    if len(fpath_list) != len(df):
        raise Exception('Dataframe creation failed.')

    return df


def add_metadata_to_dataframe(df, meta_field):
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
    
    
def get_eo_dataframe(root_path: Path, grid_name: str, version_list=None, tile_list=None):
    if version_list is None:
        version_list = ['*']
    if tile_list is None:
        tile_list = ['*']
    
    file_list = list()
    for data_version in version_list:
        for tile in tile_list:
            tile_path = root_path / data_version / grid_name / tile
            file_list.extend(list(tile_path.glob('*.tif')))
            
    return filepaths2dataframe(file_list)
