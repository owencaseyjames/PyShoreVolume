# PyShoreVolume

A Python Package for the production of shoreline and beach volumetric change statistics and map based graphical outputs. Designed for shoreline and coastal change, this package can be used for multiple environmental purposes where erosion and accretion rates need to be monitored. 

<p align="center" width="100%">
<img align = 'left' width="30%" alt="SCE" src = "https://user-images.githubusercontent.com/103570277/234302550-464bc5bf-f758-4e56-9562-93c6956072a7.png">
<img align = 'center' width="30%" alt="NSMEA" src ="https://user-images.githubusercontent.com/103570277/234302341-4163c9f1-296e-44bb-b2a5-a006be62587e.png">
<img align = 'right' width="30%" alt="NSM" src ="https://user-images.githubusercontent.com/103570277/234302214-5d05cd0b-f005-4eab-ac84-99ccd21cfed9.png">


![DOD Subplots](https://user-images.githubusercontent.com/103570277/229829778-fed9f91b-dc0d-4bd5-b68f-d7d6650b2467.png)

# Functions 

This package offers the ability to perform 5 well established Shoreline Change Analysis functions from transect based shoreline intersection shapefiles (Burningham and Fernandez-Nunez, 2020). The functions produce a full set of associated statistics for each transect in the form of a Pandas DataFrame, along with a graphical production of the shoreline change transects plotted on a satellite image of the region under analysis. 

| Function | Description | Output |
| --- | --- | --- |
| EPR (End Point Rate) | Rates of change between oldest and newest shore position divided by the length of time between the two. | Dictionary of EPR values per transect, graphical output of the EPR rates per transect, Pandas DataFrame of Statistics |
| LRR (Linear Regression Rate)| Fits a linear regression model to the change of each shoreline position along a given transect throughout time. Allows for regression statistics to be used to assess positional trend and the confidence levels of this trend. | Linear regression graphs per transect, Dictionary of Linear Regression statistics, Pandas DataFrame of Statistics. |
| SCE (Shoreline Change Envelope) | Maximum distances found between any of the shorelines. | SCE with graphical output of SCE rates on top of satellite Imagery, Dictionary of SCE rates, Pandas DataFrame of Statistics.|
| NSM (Net Shoreline Movement) | Net movement between the oldest shoreline position and most recent shoreline position. | NSM with graphical output of NSM rates on top of satellite Imagery, Dictionary of NSM rates, Pandas DataFrame of Statistics.|
| NSMEandA (Net Shoreline Movement Erosion and Accretion) | Net movement between the oldest shoreline position and most recent shoreline position with erosion and accretion trends being identified. | NSM with graphical output of NSM rates on top of satellite Imagery, Dictionary of NSMEandA rates, Pandas DataFrame of Statistics. |


The volumetric change functions are performed on a time series of Digitial Elevation Models, where each pixel in the succeeding DEM is taken away from the prior DEM producing a final DEM of accretion or erosion rates  (Carvahlo et al. 2021). In a coastal setting this can allow sediment volumes across the entire shore to measured. The full range of functions are defined below.

| Function | Description | Output |
| --- | --- | --- |
Masking | Crops the DEM’s using prior made polygon vector shapefile (*must be saved as 'VolumePoly.shp' in directory folder) and masks regions outside of the desired area to a set data value. | Masked DEM’s saved in the chosen directory with the name ’YYYYMMmasked.tif’ |
DEMofDifference | Identifies the masked DEM’s in directory and iterates through them in order from youngest to oldest creating elevation models of difference. Allows DEM’s of different sizes within the calculation by cropping the larger DEM to the size of the smaller then performing the difference. | Series of elevation difference models along with model of difference graphs with color scale for change rates.|
OldesttoNewest | Creates a DEM of difference between the oldest DEM and Newest DEM providing elevation change rates across the entire period.| Digital Elevation Model of Difference with graphical production with color scale for elevation change rates. |
| NetVolumeChange | Applies the pixel size parameter to the elevation models to calculate volumetric changes using the Oldest to Newest DEMoD.| Volumetric changes within and outside of limits of detection.|
| Seasonal DOD's: winterDOD, autumnDOD, summerDOD, springDOD| Allows user to perform analysis on DEM’s that fall within the same season. It allows an assessment of the impacts that seasonal conditions may have over elevation and volumetric change rates. |Digital Elevation Model of Difference for DEM’s that share seasons with graphical production including color scale for elevation change rates.| 
|DODSubPlot, DODspringsubplot, DODwintersubplot, DODsummersubplot, DODspringsubplot| Creates one single subplot figure of all Digital Elevation Models of Difference created in the DEM of Difference function.| A combined subplot of elevation of difference models.|

# Data Formatting, Processing and Parameters

For the functions to operate correctly two geodatabase files are needed: 1. Intersections and 2. Transects. The intersection files are the point geometries where the the transect intersects the merged shoreline vector file. The intersection file requires 2 fields with the following field naming conventions; transect number - 'TR_ID' and shoreline date - 'layer', the data of both in integer format.  The transect file also requires the corresponding transect identification numbers under the field name 'TR_ID'. These conventions are completed automatically in QGIS or can be added to data sets produced in an alternate system. 

## QGIS Workflow Example

Below is a workflow example within QGIS to produce the necessary data files for SCA analysis. 

1. Process shoreline vectors form each available date and combine them into one 'Merge Shoreline' shapefile. 
2. Create a 'baseline' polyline shapefile on the seaward side of the shorelines - use spline tool if curved baseline is desired. 
3. Use the QChainage (QGIS Plugin) to create points along the baseline at a desired spacing.

<p align="center" width="100%">
<img align = 'left' width="30%" alt="Merged Shapefile" src="https://user-images.githubusercontent.com/103570277/233672883-4178cefb-fefa-4eaa-9459-1532cf992499.png">
<img align = 'center' width="30%" alt="Baseline" src="https://user-images.githubusercontent.com/103570277/233671156-7fe22018-2b71-4a69-82d6-d92e1960c293.png"> 
<img align = 'right' width="30%" alt="Q Chainage" src="https://user-images.githubusercontent.com/103570277/233670294-563e0c85-6bd3-4453-b387-c6ddd61abdb1.png">
</p>

4. Use the 'Snap Geometries to Layer' tool to assign the 'chain_baseline' points to the baseline. 
5. Use the 'Transect' tool to set perpendicular transects along the new Snapped Geometry line. 
6. Use 'Intersections' tool to create point file of intersections between Transects file and Merged Shoreline Shapefile. 

<p align="center" width="100%">
<img align = 'left' width="30%" alt="Snap Geoms" src="https://user-images.githubusercontent.com/103570277/233671304-a56a5dc6-956e-4724-8720-389998667b23.png"> 
<img align = 'center' width="30%" alt="Transect" src="https://user-images.githubusercontent.com/103570277/233673188-18ea963c-f780-4b47-a83b-ba730a1d3b9b.png">
<img align = 'right' width="30%" alt="Intersection Process" src="https://user-images.githubusercontent.com/103570277/233673213-db17c1f2-d0d8-464e-990d-8de0fa9096c9.png">
 </p>
 
7. Save both Intersection and Transect file to the desired directory. 
<img width="32%" alt="Intersections" src="https://user-images.githubusercontent.com/103570277/233673250-6dacea21-1041-4cfd-9815-5d7f8b944be1.png">
</p>

For the DEM functions a single polygon shapefile is required to define the region under analysis and mask the DEM's to the set region in question. 


## Configuration and Function Parameters 

Initial configuration of the dataset is required to add the coordinates of the starting point of the transects (from the seaward side) to the intersection file, remove any duplicate shoreline contours found further along the transect and set up the results folder. 

There are two transect locator functions - this is as the coordinates of the transect starting points can be misread as starting from the landward side. If this is the case then Erosion and Accretion and End Point Rates will not be calculated correctly. If the transectstartlocator is incorrect, use the other option transectstartlocator2, both functions produce a plot of the coordinates which can be reviewed to see if correct coordinates are obtained. The cleaning function removes any duplicate intersections along each transect, keeping the one nearest to the seaward baseline. This configuration class also provides the option to add the georeferencing and measurement errors to each shoreline date, passed to the function in the form of a list of errors from youngest to oldest allowing error ranges to be calculated in the EPR method. 

| Parameter | Description | Type |
|---|---|---|
| Intersects | Intersection file | GeoDataFrame|
| Transects | Transect file | GeoDataFrame |
| Path | Path to directory | Path name |
| CRS | Sets the Coordinate Reference System of the geometries in the dataframe | Integer|
| georeferror | Margin of error when georeferencing an image or dataset (meters) - used in EPR function | List of Integer or Floats |
| measurementerror | Instrument error ranges (meters) - used in EPR function | List of Integer or Floats |

The two groups of functions to perform the analysis are callable as seperate classes 1. SCA and 2. DOD. Each contain a set of configuration parameters that need to be initially defined when creating an object of said class. 

Shoreline Change Analysis Parameters 

| Parameter | Description | Type |
|---|---|---|
| Intersects | The cleaned and configured intersection file | GeoDataFrame|
| save_to_path | Path to the results folder | Path name | 
| transectplot | Sets the gap between the transect identification numbers on the plot | Integer |
| CRS |  Sets the Coordinate Reference System of the geometries in the dataframe | Integer| 
| ellipsoidal | Ellipsoid model corresponding to the CRS set. Used in the GeoPy distance measurements.| String | 

DEM of Difference Parameters 

| Parameter | Description | Type |
|---|---|---|
| DODCRS | Coordinate reference system code set to the Digital Elevation Models | Integer |
| maskingCRS | CRS set to the DEM's during the masking function | String |
| path | Path to the data directory | Path name |
| save_to_path | Path to the results folder created  | Path name |
| pixelsize | Size of pixels in the DEM's (meters) | Float or Integer |
| titlesize | Size of the titles in each plot | Float or integer | 
| figwidth | Width of the plot | Float or integer | 
| figheight | Height of the plot | Float or integer | 
| subplotcols | Number of columns to be used in the subplot | Integer | 
| measurementerror| Instrument error ranges (meters)| Float or Integer |

## Usage

Import transect and intersection shapefiles into a GeoPandas dataframe.

```
from SCA import SCA
from DOD import DOD
from DataImportandTransectDefinition import DataImportandTransectDefinition 
import Geopandas as gpd

intersects = gpd.read_file(r'intersections.shp')
transects = gpd.read_file(r'transect.shp')

```
Implement the transect definition - decide whether the transect locator one or two is need by assessing the shape of the transects. 

```
#Georeferencing and measurment errors of each shoreline in meters. 
georefs = [1, 0.8, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4]
measurement = [1, 1, 1, 1, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]

#Set the cleaning configuration
Datacleaning = DataImportandTransectDefinition(CRS = 4326, intersects = intersects, transects = transects, path = path, georeferror=georefs, measurementerror=measurement)

#Assign seaward transect coordinates to intersection dataframe (Check coordinates plot)
Datacleaning.transectstartlocator1()

#Remove duplicate shoreline points
Datacleaning.cleaning()

#Add georeferencing and measurement errors for each shorleine to dataframe and save newly configured intersection file to variable. 
intersectiondata = Datacleaning.errors()

#Create and save path to results folder to be set as a parameter in the SCA functions.
results = Datacleaning.results()

```

Setting the configurations for the SCA analysis functions. An instance of this class can the be created and named after the region under analysis. Select which analysis method to use with this beach configuration. The output dataframes will be saved to the variable name of the users choosing.  

```
Saunton = SCA(ellipsoidal = 'WGS-84', save_to_path = results, transectplot = 10, CRS = 4326, measurementerror = 0.4, georeferencingerror = 0, distancemeasureerror = 0,intersectednew = intersectiondata) 

#Shorleine Change Envelope
SauntonSCE = Saunton.SCE()

#Net Shoreline Movement
SauntonNSM = Saunton.NSM()

#Net Shoreline Movement Erososion and Accretion 
SauntonNSMEandA = Saunton.NSMEandA()

Out:
```
<p align="center" width="100%">
<img align = 'left' width="30%" alt="SCE" src = "https://user-images.githubusercontent.com/103570277/234302550-464bc5bf-f758-4e56-9562-93c6956072a7.png">
<img align = 'center' width="30%" alt="NSMEA" src ="https://user-images.githubusercontent.com/103570277/234302341-4163c9f1-296e-44bb-b2a5-a006be62587e.png">
<img align = 'right' width="30%" alt="NSM" src ="https://user-images.githubusercontent.com/103570277/234302214-5d05cd0b-f005-4eab-ac84-99ccd21cfed9.png">

 
Setting the configurations for the DOD analysis functions.  Note that subplots will only work if analysis method that been used 

```
SauntonDOD = DOD(subplotcols =  2, titlesize =  6, pixelsize = 1, DODCRS = 4326, figwidth = 5,
figheight = 10, save_to_path = save_to_path, path = paths, MaskingCRS = 'EPSG:4326', measurementerror = 0.15)

#Mask the DEM's using 'VolumePoly.shp' file present in the data directory. 
SauntonDOD.Masking()
 
#DEM of Difference function. 
SauntonDEMoDResults = PORTHDOD.DEMofDifference()
 
#Subplot DEMofDifference result figures. 
SauntonDOD.DODSubPlot()
Out:
-567871.2 (m3)
+134494.33 (m3)
+4649.84 (m3)
+585515.3 (m3)
-428963.16 (m3)
+39263.8 (m3)
+477597.22 (m3)
-206586.4 (m3)
+51846.69 (m3)
```
![DOD Subplots](https://user-images.githubusercontent.com/103570277/229829778-fed9f91b-dc0d-4bd5-b68f-d7d6650b2467.png)


# References 
 
H. Burningham and M. Fernandez-Nunez. Shoreline change analysis. Sandy Beach Morphodynam- ics, pages 439–460, 1 2020. doi: 10.1016/B978-0-08-102927-5.00019-9.
 
R. C. Carvalho, B. Allan, D. M. Kennedy, C. Leach, S. O’Brien, and D. Ierodiaconou. Quan- tifying decadal volumetric changes along sandy beaches using improved historical aerial photographic models and contemporary data. Earth Surface Processes and Landforms, 46(10):1882–1897, 8 2021. ISSN 1096-9837. doi: 10.1002/ESP.5130.

# Support 

Email: owen.james@kcl.ac.uk

# Licence

The project is licensed under the MIT license.
