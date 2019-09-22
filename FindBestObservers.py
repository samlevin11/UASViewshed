# --------------------------------------------------------
# Final script for running viewshed best observation analysis
# Revised 28 April 2018
# Written by Samuel Levin
# --------------------------------------------------------

import arcpy
from arcpy.sa import *
import pandas as pd

arcpy.CheckOutExtension('Spatial')
arcpy.CheckOutExtension('3D')

def makechunks(lst, n):
    """
    Divides unseen flight points into chunks to make raster summation more efficient.
    :param lst: List of remaining unseen flight points
    :param n: Size of chunks
    :return: Generator object, iterating chunks of unseen flight points
    """
    for i in range(0,len(lst),n):
        yield lst[i:i+n]

def calcVS(unsnfltpts, bldg_veg_mask, ct, datapath):
    """
    Calculates the cumulative viewshed from remaining unseen flight points. Generates Euclidean distance
    to mean center table.
    :param unsnfltpts: List of remaining unseen flight points
    :param bldg_veg_mask: Binary mask to remove invalid observer surfaces from cumulative VS raster
    :param ct: Pass number
    :param datapath:  Path to input/output directory
    """

    print('Calculating cumulative viewshed for {} unseen flight points...'.format(len(unsnfltpts)))
    # Make chunks of flight points
    usfp_chunks = makechunks(unsnfltpts,500)
    print('Flight point chunks generated')
    chunk_sums = []
    chunkpass = 1
    # Sum each chunk of single viewshed rasters
    for chunk in usfp_chunks:
        print('Chunksum operation {} on {} flight points...'.format(chunkpass, len(chunk)))
        # Set null values equal to 0 to avoid NoData holes
        chunkgen = (Con(IsNull(arcpy.Raster(datapath + "vs_" + str(usfp))), 0, 1) for usfp in chunk)
        chunkstats = arcpy.sa.CellStatistics(chunkgen,'SUM','NODATA')
        chunk_sums.append((chunkstats))
        print('...Done.')
        chunkpass += 1
    # Sum chunks
    sumrast = arcpy.sa.CellStatistics(chunk_sums,'SUM','NODATA')
    sumrast.save(datapath + "vs_pass_" + str(ct) + "_unmasked")
    print('Unmasked cumulative viewshed saved.')

    # mask out buildings and vegetation
    # set Bldg_Veg_Mask cells to 0
    unmasked = arcpy.Raster(datapath + "vs_pass_" + str(ct)+"_unmasked")
    cumulative_masked = unmasked * bldg_veg_mask
    print('Invalid observer surfaces masked.')
    # set 0 value cells to Null
    cumulative_masked = SetNull(cumulative_masked == 0,cumulative_masked)
    print('Setting null values.')
    # save to .GDB as cumulative raster
    cumulative_masked.save(datapath + "vs_pass_" + str(ct))
    print('Masked cumulative viewshed saved.')

    # Convert raster to points with number views for VS pass and X Y location
    vs_total_pts_ = datapath + "vs_pass_" + str(ct) + "_pts"
    arcpy.RasterToPoint_conversion(cumulative_masked, vs_total_pts_)
    arcpy.AddGeometryAttributes_management(vs_total_pts_,['POINT_X_Y_Z_M'])
    print('Viewshed points for pass {} generated'.format(ct))
    # Find mean center of cumulative viewshed for pass, save as feature class
    vs_center_ = datapath + "vs_pass_" + str(ct) + "_cntr"
    arcpy.MeanCenter_stats(vs_total_pts_,vs_center_)
    print('Mean center calculated.')
    # Calculate distance of each observation from centroid of observer masspoints
    vs_dist_ = datapath + "vs_pass_" + str(ct) + "_dist"
    arcpy.PointDistance_analysis(vs_total_pts_,vs_center_,vs_dist_)
    print('Observer distances table calculated.')


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

def findvisible(datapath,allfltpts,x,y):
    """

    :param datapath: Path to input/output directory
    :param allfltpts: List of all flight points
    :param x: X coordinate location
    :param y: Y coordinate location
    :return: List of observed flight points
    """
    coord = str(x) + " " + str(y)
    observed = []
    for fp in allfltpts:
        print('Determining visibility of flight point {}'.format(fp))
        cell = arcpy.GetCellValue_management(datapath + "vs_" + str(fp),coord)
        try:
            if int(cell.getOutput(0)) == 1:
                observed.append(fp)
                print('Visible.')
        except:
            print('Not visible.')
    print('Number of visible flight points: {}'.format(len(observed)))
    print(observed)
    return observed



#=====================================================================================


surface = "C:\\Users\\sjl170230\\Documents\\UTD_Viewshed_V3\\UTD_Viewshed_NEV1.gdb\\Surface_NE_2m"
mask = "C:\\Users\\sjl170230\\Documents\\UTD_Viewshed_V3\\UTD_Viewshed_NEV1.gdb\\BldgVegMask_V3_bin_exp1"
flightpts = "C:\\Users\\sjl170230\\Documents\\UTD_Viewshed_V3\\UTD_Viewshed_NEV1.gdb\\FlightPts_NE"
path = "C:\\Users\\sjl170230\\Documents\\UTD_Viewshed_V3\\UTD_Viewshed_NEV1.gdb\\"

n_pts = int(arcpy.GetCount_management(flightpts).getOutput(0))

all_fltpts = list(range(1,n_pts+1))
unseen_fltpts = all_fltpts

count = 0
best = pd.DataFrame()

numfltpts = len(all_fltpts)

obsvis = {}
totalvis = []
passleft = []
cumlviewed = []

while len(unseen_fltpts) > 0 and count < 10:
    print('\n')
    print('PASS {}'.format(count))
    passleft.append(len(unseen_fltpts))
    calcVS(unseen_fltpts,mask,count,path)
    best = findbestobs(count,path,best)
    best_x= best.iloc[count]['POINT_X']
    best_y= best.iloc[count]['POINT_Y']
    passviewed = findvisible(path,all_fltpts,best_x,best_y)
    totalvis.append(len(passviewed))
    cumlviewed.append(best['grid_code'].sum())
    obsvis[count] = passviewed
    unseen_fltpts = [us for us in unseen_fltpts if us not in passviewed]
    print('REMAINING UNSEEN: {}'.format(len(unseen_fltpts)))
    count += 1

best['passleft'] = passleft
best['PASS_CVRG'] = (best['grid_code']/best['passleft'])*100

best['OBSRVR_VIS'] = totalvis
best['OBSRVR_CVRG'] = (best['OBSRVR_VIS']/numfltpts)*100

cumlviewed = [(n/numfltpts)*100 for n in cumlviewed]
best['CUMULATIVE_CVRG'] = cumlviewed

print(best)

best['grid_code'] = best['grid_code'].apply(lambda x: int(x))
best.rename(columns={'grid_code':'PASS_VIS'},inplace=True)
best.drop(['DISTANCE','OBJECTID','passleft'],axis=1,inplace=True)

print(best)

savebest = "C:\\Users\\sjl170230\\Documents\\UTD_Viewshed_V3\\OutTables\\bestobservers.csv"
best.to_csv(savebest)
print('Best observers CSV exported to: {}'.format(savebest))
print('\n')
print('PROCESS COMPLETE.')
print('BEST OBSERVERS: ')
print(best)

print("NEW PART!!!!!!!!!!!!!!!")
# Get spatial reference from surface
spatialref = arcpy.Describe(arcpy.Raster(surface)).spatialReference
# Make layer and save to feature class from bestobservers.csv
arcpy.MakeXYEventLayer_management(savebest,'POINT_X','POINT_Y',"BestObs_Lyr",spatialref)
arcpy.FeatureClassToFeatureClass_conversion("BestObs_Lyr",path,"BestObservers")
print("Best Observers feature class saved.")

# Add blank text field to flight points for observers
arcpy.AddField_management(flightpts,"Observers","TEXT")
arcpy.CalculateField_management(flightpts,"Observers", "\"\"", "PYTHON_9.3")
print('Observers field added.')

# For each pass...
for c in range(0,count):
    print(c)
    # For each row in original flight points
    with arcpy.da.UpdateCursor(flightpts,['OBJECTID','Observers']) as cursor:
        for row in cursor:
            # if OID of flight point is in list of observed flight points for a best observer
            if row[0] in obsvis[c]:
                # Append text of observer number to 'Observers' field
                row[1] = row[1] + str(c)
                cursor.updateRow(row)

print('DONE.')

