# --------------------------------------------------------
# Find best observation based on potential observation points views and distances from mean center
# Adjust list of unseen flight points
# Revised 28 April 2018
# Written by Samuel Levin
# --------------------------------------------------------

import arcpy
import pandas as pd

def feature_class_to_pandas_data_frame(feature_class, field_list):
    """
    Load data into a Pandas Data Frame for subsequent analysis.
    :param feature_class: Feature class.
    :param field_list: Desired fields.
    :return: Pandas DataFrame object.
    """
    return pd.DataFrame(arcpy.da.FeatureClassToNumPyArray(in_table=feature_class,field_names=field_list,
                                                          skip_nulls=False,null_value=-99999))


# Set return of this function to bestloc variable in findvisible()
def findbestobs(ct,datapath,best_df):
    """
    Find best observer by merging raster points to distance table, sorting by grid_code and distance
    :param ct: Pass number
    :param datapath: Path to input/output directory
    :param best_df: Pandas DataFrame of best observers
    :return: Pandas DataFrame of best observers
    """
    vspts = datapath + "vs_pass_" + str(ct) + "_pts"
    vsfields =  ['OBJECTID', 'POINT_X','POINT_Y','grid_code']
    vs_df = feature_class_to_pandas_data_frame(vspts, vsfields)
    dst = datapath + "vs_pass_" + str(ct) + "_dist"
    dstfields = ['OBJECTID','DISTANCE']
    dst_df = feature_class_to_pandas_data_frame(dst,dstfields)
    vsdist = vs_df.merge(dst_df, on='OBJECTID')
    vsdist.sort_values(['grid_code', 'DISTANCE'], ascending=[False, True],inplace=True)
    x = vsdist.iloc[0]['POINT_X']
    y = vsdist.iloc[0]['POINT_Y']
    # Append X Y cooridnates of best observation to DataFrame of all best
    best_df = best_df.append(vsdist.iloc[0],ignore_index=True)
    print('Best observer for pass {} located'.format(ct))
    print(best_df)
    # Return X Y coordinates of best observation for the current pass
    print('\n')
    return best_df

def findvisible(datapath,unseenfltpts,x,y):
    """

    :param datapath: Path to input/output directory
    :param unseenfltpts: List of remaining unseen flight points
    :param x: X coordinate location
    :param y: Y coordinate location
    :return: List of observed flight points
    """
    coord = str(x) + " " + str(y)
    observed = []
    for usfp in unseenfltpts:
        print('Determining visibility of flight point {}'.format(usfp))
        cell = arcpy.GetCellValue_management(datapath + "vs_" + str(usfp),coord)
        try:
            if int(cell.getOutput(0)) == 1:
                observed.append(usfp)
                print('Visible.')
        except:
            print('Not visible.')
    print('Number of visible flight points: {}'.format(len(observed)))
    print(observed)
    return observed
