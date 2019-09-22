# --------------------------------------------------------
# Calculate cumulative viewshed and generate potential observer points
# Revised 28 April 2018
# Written by Samuel Levin
# --------------------------------------------------------
import arcpy
from arcpy.sa import *
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
    print(len(chunk) for chunk in usfp_chunks)
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
