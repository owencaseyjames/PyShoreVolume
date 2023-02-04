#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  4 17:35:27 2023

@author: owenjames
"""

def shorelinechangeenvelope(intersectednew):
                                maxdistancedic = {}
                                val = min(intersectednew['TR_ID'])
                                data = []
                                distances=[]
                                coordx = []
                                coordy = []
                                trid = []
                                distances1 = []
                                for ids in intersectednew['TR_ID']:
                                    if ids == val:            
                                        s = intersectednew.loc[intersectednew['TR_ID'] == ids]
                                        transectsvalx = np.array(s['geometry_x'].x)
                                        transectsvaly = np.array(s['geometry_x'].y)
                                        transectsval = np.vstack((transectsvalx, transectsvaly)).T
                                        distancescdist = cdist(transectsval, transectsval,'euclidean') ##Identifies distances between points
                                        maxds = np.max(distancescdist) ##Identifies max distances  
                                        
                                        
                                        location = np.where(distancescdist == maxds)
                                        # distances = geopy.distance.geodesic(transectsval[location[0][0]],transectsval[location[1][0]]).m
                                         ##Identifies where in the array the max distances are and saves location
                                        
                                        newdatedatadf= pd.DataFrame({'x':[transectsval[location[0][0]][0]],'y':[transectsval[location[0][0]][1]], 'x1':[transectsval[location[1][0]][0]],\
                                                                     'y1':[transectsval[location[1][0]][1]]}, columns=['x','y','x1','y1'])
                                        firstdata = GeoDataFrame(geometry = gpd.points_from_xy(newdatedatadf['x'],newdatedatadf['y']), crs = 4326)
                                        seconddata = GeoDataFrame(geometry = gpd.points_from_xy(newdatedatadf['x1'],newdatedatadf['y1']), crs = 4326)          
                                        

                                        firstdata = firstdata.to_crs(Config.CRS)
                                        seconddata = seconddata.to_crs(Config.CRS)
                                        coordinate1 = (np.array(firstdata['geometry'].x), np.array(firstdata['geometry'].y))
                                        coordinate2 = (np.array(seconddata['geometry'].x), np.array(seconddata['geometry'].y))
                                        distances = geopy.distance.distance(coordinate1,coordinate2, ellipsoid = Config.ellipsoidal).m
                                                                             
                                        firstdata = firstdata.to_crs(3857)
                                        seconddata = seconddata.to_crs(3857)
####This dictionary isnt needed >
                                        # maxdistancedic[ids] = {'coordinatesfirstx':firstdata['geometry'].x,'coordssecondx':seconddata['geometry'].x,\
                                        #                        'coordinatesfirsty':firstdata['geometry'].y, 'coordssecondy':seconddata['geometry'].y, 'distances': distances} ##Saves coords and distances in dictionary
                                    
                                        coordx.append(firstdata['geometry'].x)
                                        coordy.append(firstdata['geometry'].y)
                                        coordx.append(seconddata['geometry'].x)
                                        coordy.append(seconddata['geometry'].y)
                                        distances1.append(distances)
                                        distances1.append(distances)
                                        trid.append(ids)
                                        trid.append(ids)
                                            
                                        val = val + 1
                                
                                norm = matplotlib.colors.Normalize(vmin = min(distances1), vmax= max(distances1), clip = True)
                                cmaps= plt.get_cmap('viridis')
                                c = cmaps(norm(distances1))
                                fig = plt.figure(figsize=(10,20))
                                ax = fig.add_subplot(111)
                                
                                for i in range(0,len(coordx),2):
                                    # print(i)
                                    ax.plot(coordx[i:i+2],coordy[i:i+2],'ro-', marker = None, c=c[i])
                                for ins in range(0,len(trid),100):                    
                                    ax.annotate(trid[ins], (coordx[ins], coordy[ins]))                              
                                
                                
                                divider = make_axes_locatable(ax)
                                cax = divider.append_axes("right", size="5%", pad=0.05)    
                                cbar = fig.colorbar(cm.ScalarMappable(norm=norm, cmap = cmaps), ax = ax, cax = cax)
                                cbar.set_label('Change in Meters', rotation=270, fontsize = 13, labelpad = 12)
                                ctx.add_basemap(ax, source=ctx.providers.Esri.WorldImagery, zoom=15)
                                ax.set_title('Shoreline Change Envelope', fontsize=15)
                                ax.set_ylabel('Latitude', fontsize = 12)
                                ax.set_xlabel('Longitude', fontsize=12)
                                plt.show()
                                fig.savefig(Config.save_to_path+'shorleinechangeenvelope.png')
                                
                                
                                
                                
                            