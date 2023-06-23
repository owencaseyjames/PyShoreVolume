#Allows the creation of folders that contain files with similar name types.
#Useful if files have dates - allowing the creation of folders named after
#and containing files according to dates given.

import os 
import re
import shutil

#Change directories accordingly
dir_name = os.chdir('---')
##Make sure the below code line has ' / ' at the end to indicate this is where the files are located.
file_names = os.listdir('---')

#Need to look at the file names to extract the characters to be matched.
pattern = "[0-9][0-9][0-9][0-9][0-9][0-9]"

#Iterate through file names directory
for file_name in file_names:
    #Search to match the pattern given between filenames and extract into 'dates'.
    dates = re.search(pattern, file_name)
    print(dates)
    #create folder names  by converting to string
    folder_name = str(dates)
    print(folder_name)
    
    #If path of folder name doesnt exist then create new path with given name. Index 
    # the values to be used as the name. 
    if not os.path.exists(folder_name[-8:-2]):
            os.mkdir(folder_name[-8:-2])
    #Move the files into the folder of corresponding name type.        
    shutil.move(file_name, folder_name[-8:-2])
