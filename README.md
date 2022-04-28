# TopRock

TopRock v2.0 – 2020.09.02
This tool was developed to pick the top of bedrock in water wells obtained from Wellogic, the Michigan Department of Environment, Great Lakes, and Energy Statewide Ground Water Database. 
In general, the tool does the following:
1. Determine the lowest drift recorded for each WELLID.  Accomplished by using SEQ_NUM and AQTYPE.
2. Determine the highest rock recorded below the lowest drift for each WELLID. Accomplished by using SEQ_NUM and AQTYPE.
3. Adds BR field, and records 'BR' for first encountered bedrock beneath lowest drift.
4. Joins .dbf to .shp and exports to new feature class.
5. Add surface elveation data to new feature class.
6. Adds BR_ELEV field and calculates bedrock elevation using surface elevation and depth information.
How to run the tool:
Inputs:
*_lith.dbf
*_WaterWells.shp
DEM (units must be in feet)
Output:
BR_TOPS feature class (must be saved in geodatabase)

Steps:
1. Download water wells by county from here:
	https://www.michigan.gov/som/0,4669,7-192-78943_78944_78955-427312--,00.html
2. Download Michigan PLSS from here (if you don't already have it):
	https://gis-michigan.opendata.arcgis.com/datasets/public-land-survey-sections?geometry=-140.283%2C49.326%2C88.057%2C75.563	
3. Open tool using either ArcMap or ArcCatalog.
4. Add inputs:
	inputdbf = *_lith.dbf
	inputshp = *_WaterWells.shp
	DEM = DEM (feet)
5. Select output location (where do you want to save the output):
	outputfc = Wherever you want so long as it is in a geodatabase.
6. Click OK.

Note: If background geoprocesing is turned off, several messages will be displayed indicating the status of the tool. Each WELLID will be displayed as it is being processed.

Note: AQTYPE U (Unidentified) are not included in this process and will be returned as NULL.

If you have questions concerning this tool, please contact:
Nathan Erber
email: nathan.r.erber@wmich.edu
