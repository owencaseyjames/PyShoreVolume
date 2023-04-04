# PyShoreVolume

A Python Package for the production of shoreline change and volumetric change statistics with graphical and database outputs with a limited amount of pre-processing in QGIS. Designed for shoreline and coastal change, this package can be used for multiple puproses such as assessing glacial retreat and volumetric change rates, depostion and erosion within fluvial envrionments. 

# Functions 
This package offers the ability to perform 5 Shoreline Change Analysis functions (EPR, NSM, SCE, Erosion and Accretion and Linear Regression Rate) from transect based shoreline intersection shapefiles. The functions produce a full set of associated statistics for each transect in the form of a Pandas DataFrame, along with a graphical production of the shoreline change transects plotted on a satellite image of the region under analysis. 

![shorleinechangeenvelope](https://user-images.githubusercontent.com/103570277/229756967-e0fdaede-57e7-4b3a-ba17-1da875539251.png)
![netshorelinemovement](https://user-images.githubusercontent.com/103570277/229757084-0e69bb95-7892-4495-ae91-84460d1654c6.png)
![NetShorelineMovementErosionandAccretion](https://user-images.githubusercontent.com/103570277/229799392-d8049410-7d93-404c-8f60-df2c8784a27a.png)
![End Point Rate](https://user-images.githubusercontent.com/103570277/229799462-eb4c512d-3f29-49fc-94b2-97af069c2000.png)

The volumetric change functions are performed on a time series of Digitial Elevation Models, where each pixel in the succeeding DEM is taken away from the prior DEM producing a final DEM of accretion or erosion rates. In a coastal setting this can allow sediment volumes across the entire shore to measured. There are multiple functions that can be utilised:
- DEMofDifference  - differences across each DEM in the time series order.
- Seasonality - Identifies DEM's which were measured within the same season and performs DEMofDifference functions. 
- Limit of Detection - Identifies the volumetric change rates after exlusion of measurement errors from the calculations
- Oldest to Newest - Produces a DEM of the Net Elevation differences between the Oldest DEM and the Neweset. 
- Masking - Masks the DEMs using a polygon shapefile over the region of interests, setting no data values over pixel outside of this region. 

![DOD Subplots](https://user-images.githubusercontent.com/103570277/229829778-fed9f91b-dc0d-4bd5-b68f-d7d6650b2467.png)
