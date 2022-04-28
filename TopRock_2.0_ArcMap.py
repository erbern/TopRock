import os
import arcpy
from arcpy import env
from arcpy.sa import *

arcpy.env.overwriteOutput = True

inputdbf = arcpy.GetParameterAsText(0)
inputshp = arcpy.GetParameterAsText(1)
inputDEM = arcpy.GetParameterAsText(2)
outputLocation = arcpy.GetParameterAsText(3)
TRS = arcpy.GetParameterAsText(4)
outputName = arcpy.GetParameterAsText(5)

arcpy.AddMessage("inputshp to in_memory")	
arcpy.FeatureClassToFeatureClass_conversion(inputshp, "in_memory", "BR_shp")

arcpy.AddMessage("inputdbf to in_memory")
arcpy.CopyRows_management(inputdbf, "in_memory\BR_dbf")
arcpy.AddField_management("in_memory\BR_dbf", 'BR','TEXT')

arcpy.AddMessage("Create list of unique WELLIDs")	
values = [row[0] for row in arcpy.da.SearchCursor("in_memory\BR_shp", 'WELLID')]
WELLIDs = set(values)

arcpy.AddMessage("Pick BR records from inputdbf")	
for Well in WELLIDs:
	'arcpy.AddMessage(Well)'
	with arcpy.da.SearchCursor("in_memory\BR_dbf",['SEQ_NUM', 'WELLID', 'AQTYPE'], "WELLID = '" + str(Well) +"'") as cursor:
		listAllD = []
		for row in sorted(cursor):
			if (row[2] == 'D'):
				listAllD.append(row[0])
		if listAllD:
			maxD = listAllD[-1]
		else:
			maxD = 1
		del listAllD[:]
	with arcpy.da.UpdateCursor("in_memory\BR_dbf",['SEQ_NUM', 'AQTYPE', 'PRIM_LITH', 'WELLID'], "WELLID = '" + str(Well) +"'") as cursor2:
		listAllR = []
		for row in sorted(cursor2):
			if row[0] >= maxD and ((row[1] =='R') or (row[1] == 'U' and row[2] == 'Unidentified Consolidated Fm')):
				listAllR.append(row[0])
		if listAllR:
			minR = listAllR[0]
		else:
			continue
	with arcpy.da.UpdateCursor("in_memory\BR_dbf",['SEQ_NUM', 'BR', 'AQTYPE', 'PRIM_LITH', 'WELLID'], "WELLID = '" + str(Well) +"'") as cursor3:
		for row in cursor3:
			if row[0] >= maxD and ((row[2] =='R') or (row[2] == 'U' and row[3] == 'Unidentified Consolidated Fm')):
				if row[0] == minR:
					row[1] = "BR"
				cursor3.updateRow(row)
		del listAllR[:]

arcpy.AddMessage("Save BR records from in_memory dbf to outputLocation as outputdbf")	
arcpy.TableToTable_conversion("in_memory\BR_dbf", outputLocation, "outputdbf", "BR = 'BR'")

arcpy.AddMessage("Make inputshp into feature layer")
arcpy.MakeFeatureLayer_management("in_memory\BR_shp", "in_shp")

arcpy.AddMessage("Join inputshp to outputdbf")
arcpy.AddJoin_management("in_shp", "WELLID", outputLocation + "\outputdbf", "WELLID", "KEEP_COMMON")

arcpy.AddMessage("Save inputshp feature layer to feature class")
arcpy.FeatureClassToFeatureClass_conversion("in_shp", "in_memory", "outputFC1")

arcpy.AddMessage("Check out spatial extension")
arcpy.CheckOutExtension("Spatial")

arcpy.AddMessage("Extract inputDEM values to points")
ExtractValuesToPoints("in_memory\outputFC1", inputDEM, "in_memory\outputfc")

arcpy.AddMessage("Add field BR_ELEV AND Calculate")
arcpy.AddField_management("in_memory\outputfc", "BR_ELEV", "DOUBLE")

with arcpy.da.UpdateCursor("in_memory\outputfc",['BR_ELEV', 'RASTERVALU', 'outputdbf_DEPTH', 'outputdbf_THICKNESS']) as cursor4:
	for row in cursor4:
		if row[1] == None or row[2] == None:
			row[0] = None
			cursor4.updateRow(row)
		else:
			row[0] = (row[1]-row[2]) + row[3]
			cursor4.updateRow(row)

arcpy.AddMessage("SPATIAL JOIN to TRS to check well locations")	
arcpy.SpatialJoin_analysis("in_memory\outputfc", TRS, outputLocation + "\\" +outputName)

arcpy.AddMessage("Add field LOC_FLAG")	
arcpy.AddField_management(outputLocation + "\\" + outputName, 'LOC_FLAG','TEXT')

arcpy.AddMessage("Check well locations")
with arcpy.da.UpdateCursor(outputLocation + "\\" + outputName,['outputdbf_WELLID', 'TOWN', 'RANGE', 'SEC', 'BR_shp_TOWN', 'BR_shp_RANGE', 'BR_shp_SECTION', 'LOC_FLAG']) as cursor:
	for row in cursor:
		if row[1] == row[4] and row[2] == row[5] and row[3] == row[6]:
			row[7] = "OK"
			cursor.updateRow(row)
		else:
			row[7] = "CHECK"
			cursor.updateRow(row)
		'print row[7]'

arcpy.AddMessage("FIELD MANAGEMENT...")		
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_WELLID", "WELLID")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_COUNTY", "WELL_CO")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_PERMIT_NUM", "PERMIT_NUM")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_TOWNSHIP", "TOWNSHIP")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_TOWN", "WELL_TN")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_RANGE", "WELL_RN")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_SECTION", "WELL_SEC")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_OWNER_NAME", "OWNER_NAME")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_WELL_ADDR", "WELL_ADDR")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_WELL_CITY", "WELL_CITY")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_WELL_ZIP", "WELL_ZIP")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_WELL_DEPTH", "WELL_DEPTH")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_WELL_TYPE", "WELL_TYPE")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_TYPE_OTHER", "TYPE_OTHER")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_WEL_STATUS", "WEL_STATUS")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_STATUS_OTH", "STATUS_OTH")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_WSSN", "WSSN")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_WELL_NUM", "WELL_NUM")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_DRILLER_ID", "DRILLER_ID")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_DRILL_METH", "DRILL_METH")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_METH_OTHER", "METH_OTHER")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_CONST_DATE", "CONST_DATE")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_CASE_TYPE", "CASE_TYPE")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_CASE_OTHER", "CASE_OTHER")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_CASE_DIA", "CASE_DIA")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_CASE_DEPTH", "CASE_DEPTH")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_SCREEN_FRM", "SCREEN_FRM")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_SCREEN_TO", "SCREEN_TO")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_SWL", "SWL")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_FLOWING", "FLOWING")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_AQ_TYPE", "AQ_TYPE")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_TEST_DEPTH", "TEST_DEPTH")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_TEST_HOURS", "TEST_HOURS")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_TEST_RATE", "TEST_RATE")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_TEST_METHD", "TEST_METHD")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_TEST_OTHER", "TEST_OTHER")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_GROUT", "GROUT")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_PMP_CPCITY", "PMP_CPCITY")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_LATITUDE", "LATITUDE")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_LONGITUDE", "LONGITUDE")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_METHD_COLL", "METHD_COLL")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_ELEVATION", "ELEVATION")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "BR_shp_ELEV_METHD", "ELEV_METHD")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "outputdbf_SEQ_NUM", "SEQ_NUM")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "outputdbf_PRIM_LITH", "PRIM_LITH")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "outputdbf_LITH_MOD", "LITH_MOD")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "outputdbf_CLASS", "CLASS")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "outputdbf_EFFECT", "EFFECT")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "outputdbf_MAQTYPE", "MAQTYPE")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "outputdbf_COLOR", "COLOR")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "outputdbf_DEPTH", "DEPTH")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "outputdbf_THICKNESS", "THICKNESS")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "RASTERVALU", "DEM")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "outputdbf_BR", "BR")
arcpy.AlterField_management(outputLocation + "\\" + outputName, "TWNRNGSEC", "WELL_TWNRNGSEC")

arcpy.AddField_management(outputLocation + "\\" + outputName, "BR_Top", "DOUBLE")

arcpy.CalculateField_management(outputLocation + "\\" + outputName, "BR_Top", "!DEPTH! - !THICKNESS!", "PYTHON_9.3")

fieldNameLst = ["outputdbf_WELLID", "outputdbf_AQTYPE", "outputdbf_OBJECTID"]

arcpy.DeleteField_management(outputLocation + "\\" + outputName, fieldNameLst)

arcpy.AddMessage("Adding data to map")
mxd = arcpy.mapping.MapDocument("CURRENT")
df = arcpy.mapping.ListDataFrames(mxd,"*")[0]
newlayer = arcpy.mapping.Layer(outputLocation + "\\" + outputName)
arcpy.mapping.AddLayer(df, newlayer,"BOTTOM")

arcpy.AddMessage("done")
