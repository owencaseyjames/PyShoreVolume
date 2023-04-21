# PyShoreVolume

A Python Package for the production of shoreline change and volumetric change statistics with graphical and database outputs with a limited amount of pre-processing in QGIS. Designed for shoreline and coastal change, this package can be used for multiple puproses such as assessing glacial retreat and volumetric change rates, depostion and erosion within fluvial envrionments. 
![shorleinechangeenvelope](https://user-images.githubusercontent.com/103570277/229756967-e0fdaede-57e7-4b3a-ba17-1da875539251.png)
![netshorelinemovement](https://user-images.githubusercontent.com/103570277/229757084-0e69bb95-7892-4495-ae91-84460d1654c6.png)
![NetShorelineMovementErosionandAccretion](https://user-images.githubusercontent.com/103570277/229799392-d8049410-7d93-404c-8f60-df2c8784a27a.png)


![DOD Subplots](https://user-images.githubusercontent.com/103570277/229829778-fed9f91b-dc0d-4bd5-b68f-d7d6650b2467.png)

# Functions 

This package offers the ability to perform 5 Shoreline Change Analysis functions (EPR, NSM, SCE, Erosion and Accretion and Linear Regression Rate) from transect based shoreline intersection shapefiles. The functions produce a full set of associated statistics for each transect in the form of a Pandas DataFrame, along with a graphical production of the shoreline change transects plotted on a satellite image of the region under analysis. 

| Function | Description | Output |
| --- | --- | --- |
| End Point Rate | Rates of change between oldest and newest shore position divided by the length of time between the two. | Dictionary of EPR values per transect, graphical output of the EPR rates per transect, Pandas DataFrame of Statistics |
| Linear Regression Rate | Fits a linear regression model to the change of each shoreline position along a given transect throughout time. Allows for regression statistics to be used to assess positional trend and the confidence levels of this trend. | Linear regression graphs per transect, Dictionary of Linear Regression statistics, Pandas DataFrame of Statistics. |
| Shoreline Change Envelope | Maximum distances found between any of the shorelines. | SCE with graphical output of SCE rates on top of satellite Imagery, Dictionary of SCE rates, Pandas DataFrame of Statistics.|
| Net Shoreline Movement | Net movement between the oldest shoreline position and most recent shoreline position. | NSM with graphical output of NSM rates on top of satellite Imagery, Dictionary of NSM rates, Pandas DataFrame of Statistics.|
| Net Shoreline Movement Erosion and Accretion | Net movement between the oldest shoreline position and most recent shoreline position with erosion and accretion trends being identified. | NSM with graphical output of NSM rates on top of satellite Imagery, Dictionary of NSMEandA rates, Pandas DataFrame of Statistics. |


The volumetric change functions are performed on a time series of Digitial Elevation Models, where each pixel in the succeeding DEM is taken away from the prior DEM producing a final DEM of accretion or erosion rates. In a coastal setting this can allow sediment volumes across the entire shore to measured. The full range of functions are defined below. 

| Function | Description | Output |
| --- | --- | --- |
Masking | Crops the DEM’s using prior made vector shapefile and masks regions outside of the desired area to set data value. | Masked DEM’s saved in the chosen directory with the name ’YYYYMMmasked.tif’ |
DEM of Difference | Identifies the masked DEM’s in directory and iterates through them in order from youngest to oldest creating elevation models of difference. Allows DEM’s of different sizes within the calculation by cropping the larger DEM to the size of the smaller then performing the difference. | Series of elevation difference models along with model of difference graphs with color scale for change rates.|
|DOD Subplot | Creates one single subplot figure of all Digital Elevation Models of Difference created in the DEM of Difference function. | A combined subplot of elevation of difference models.|
Oldest to Newest | Creates a DEM of difference between the oldest DEM and Newest DEM providing elevation change rates across the entire period.| Digital Elevation Model of Difference with graphical production with color scale for elevation change rates. |
|Net Volume Change | Applies the pixel size parameter to the elevation models to calculate volumetric changes using the Oldest to Newest DEMoD.| Volumetric changes within and outside of limits of detection. 
Limit of Detection | Produces elevation model of differences that exlcudes the measurement error ranges from the remote sensing tool used to collate the data. | Sum of all pixel values producing net elevation changes that are higher than the error ranges that have been set. Also produces graphical output of results. |
Seasonal DOD | Allows user to perform analysis on DEM’s that fall within the same season. It allows an assessment of the impacts that seasonal conditions may have over elevation and volumetric change rates. |Digital Elevation Model of Difference for DEM’s that share seasons with graphical production including color scale for elevation change rates.|


# Data Formatting and Processing Procedure

For the functions to operate correctly two geodatabase files are needed: 1. Intersections and 2. Transects. The intersection files are the points where the the transect intersects the merged shoreline vector file. The intersection file requires 2 fields with the following field naming conventions; Transect number - 'TR_ID' and shoreline date - 'layer', the data of both in integer format.  The transect file also requires the corresponding transect identification numbers under the field name 'TR_ID'. The process below shows how to create these files in QGIS, however is possible to add these fields to files not created within the QGIS environment. 

<img align = 'left' width="33%" alt="Q Chainage" src="https://user-images.githubusercontent.com/103570277/233670294-563e0c85-6bd3-4453-b387-c6ddd61abdb1.png"> 1. Process shoreline vectors form each available date and combine them into one 'Merge Shoreline' shapefile. 
2. Create a 'baseline' polyline shapefile on the seaward side of the shorelines - use spline tool if curved baseline is desired. 
3. Use the QChainage (QGIS Plugin) to create points along the baseline at a desired spacing. 
4. Use the 'Snap Geometries to Layer' tool to assign the 'chain_baseline' points to the baseline. 
5. Use the 'Transect' tool to set perpendicular transects along the new Snapped Geometry line. 
6. Use 'Intersections' tool to create point file of intersections between Transects file and Merged Shoreline Shapefile. 
7. Save both Intersection and Transect file. 


An additional polygon shapefile that defines the coastal area to be analysed must be saved under name 'Volumepoly' in the data directory in order for the masking procedure to work. 

# Usage
```
from SCA import SCA
from DOD import DOD
from DataImportandTransectDefinition import DataImportandTransectDefinition 
import Geopandas and geopandas 

intersectdata = geopandas.read_file(r'intersections.shp')
baseline = geopandas.read_file(r'transect.shp')

directory = 'results/'
save_to_path = os.path.join(paths, directory)   
os.makedirs(save_to_path, exist_ok = True)  
```
Import transect and intersection shapefiles into a GeoPandas dataframe object and create a results folder. 

```
Datacleaning = DataImportandTransectDefinition(CRS = 4326, intersects = intersectdata, transects = baseline)
intersected = Datacleaning.transectstartlocator()
intersected = Datacleaning.cleaning()
```

Data Cleaning and Transect definition is designed to add the coordinates of the starting point of the transects (from the seaward side) to the intersection file and remove any duplicate shoreline positions that may be found along the same transect. Create an object of this class with configurations set - CRS, Intersect data and transect data. There two transect locator functions - this is as the coordinates of the transect stating points can some time be read on the landward side. If this is the case then Erosion and Accretion  will not be calculated correctly. If the transectstartlocator is incorrect, use the other option transectstartlocator2, both functions produce a plot of the coordinates which can be reviewed to see if correct coordinates are obtained. The cleaning function removes any duplicate intersections along each transect, keeping the one nearest to the seaward baseline.

```
PORTH = SCA(ellipsoidal = 'WGS-84', save_to_path = save_to_path, transectplot = 10, CRS = 4326, measurementerror = 0.4, georeferencingerror = 0, distancemeasureerror = 0,intersectednew = intersectdata) 

Porthlrr = PORTH.LRR()
PorthSCE = PORTH.SCE()
PorthEPR = PORTH.EPR()
Porthnsm = PORTH.NSM()
Porthnsmeanda = PORTH.NSMEandA()
```
Set the configurations for the SCA analysis functions, taking 8 arguments to be set. The elliposdal model defines what ellipsoid will be used in the distance measurements (https://geopy.readthedocs.io/en/stable/#module-geopy.distance), this corresponds to the CRS measurement set. save_to_path is the path to the results folder created in the prior code segment. Transect plot defines how often the transect number is plotted on to the final figure. CRS is the Coordinate Reference System to be used to perform the distance measurements. The error parameters are used to define the error ranges in the EPR plot and calculations. Finally intersectednew is where the intersection geopandas database is added to  the model. 

An instance of this class can the be created and named after the region under analysis. Each of the methods provide a graphical output and the output results dataframe can be saved as a variable in the Python Interface as well as getting automatically saved in the results folder. 

```
PORTHDOD = DOD(subplotcols =  2, titlesize =  6, pixelsize = 1, DODCRS = 4326, figwidth = 5,
figheight = 10, save_to_path = save_to_path, path = paths, MaskingCRS = 'EPSG:4326', measurementerror = 0.15)

PORTHDOD.Masking()
PORTHDOD.DEMofDifference()
PORTHDOD.DODSubPlot()
PORTHDOD.winterDOD()
PORTHDOD.OldesttoNewest()
PORTHDOD.NetVolumeChange()
```

Configuration of the Digital Elevation Model of Difference functions takes 10 arguments. subplotcols defines number of columns in the subplot, titlesize adjusts the titlesize according matplotlib sizing conventions, pixelsize is the size of each pixel in m2, DODCRS the coordinate reference system given to the newly made DEM models, figurewidth and figureheight are plot dimensions sizes, path and save_to_path are the paths to the data directory folders and results folder repectively, MaskingCRS requires a Proj4 EPSG code and applies it to the masked DEM's meta data, measurement error is the error ranges of the elevation data to calcuate Limit of detection. 

Again an instance of the class with these specifed parameters can be created. The masking method needs to be deployed prior any other method being used. The DEMofDifference and Seasonal methods need to be performed prior to any subplot method being used. The Oldest to Newest method also needs to be performed prior to the Net Volume Change method. 

# Licence

The project is licensed under the MIT license.
