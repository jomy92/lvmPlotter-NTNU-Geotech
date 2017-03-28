import numpy as np
import re

def readLVM( filepath ):
    # Open and read file
    with open( filepath ,'r') as f:
        lines = f.readlines()
    
    # Define variables
    numbering   =   []  
    time       =    []
    mode       =    []
    
    # Store ID given in file
    fileID      =   lines.pop(0)   
    
    # Determine buildup of LVM
    for val, id in enumerate(lines):
        if '*Header*' in id:
            numbering.append(val)
        elif '*Calibration data'  in id:
            numbering.append(val)
        elif '\n' == id or '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\n' == id:
            numbering.append(val)
        elif '\t-------\t-------\t-------' in id and val <1000:
            numbering.append(val)
        elif '\t-------\t-------\t-------' in id and val >1000:
            numbering.append(val)   
        
    
    ## Divide up LVM file according to buildup
    
    # Normal case
    if len(numbering) <= 4:
        header      =   lines[numbering[0]+1:numbering[1]]
        calibData   =   lines[numbering[1]+1:numbering[2]]
        columnName  =   lines[numbering[2]+1:numbering[3]]
        data        =   lines[numbering[3]+1:]
        
        # Convert comma to dot in data
        for val, id in enumerate(data):
            data[val] = id.replace(",", ".")   
        
        for val, id in enumerate(calibData):
            calibData[val] = id.replace(",", ".")
            
        # Split string data into lists
        fileID = re.split(r'\t+', fileID.rstrip('\n'))
        
        for i in range(len(header)):
            header[i] = re.split(r'\t+', header[i].rstrip('\n'))
            if  'Depth' in header[i]:
                # Convert comma to dot in depth
                header[i][1] = header[i][1].replace(",", ".") 
            
        for i in range(len(calibData)):
            calibData[i] = re.split(r'\t+', calibData[i].rstrip('\n'))
            
        for i in range(len(columnName)):
            columnName[i] = re.split(r'\t+', columnName[i].rstrip('\n'))
            
        for i in range(len(data)):
            data[i] = re.split(r'\t+', data[i].rstrip('\n'))
        
        # Store time and mode in new lists
        for i in range(len(data)):
            time.append(data[i].pop(0))  # Timestamp
            mode.append(data[i].pop(-1)) # Mode
        
        # Convert timestamp to seconds
        d = []
        for i in range(len(time)):
            h, m, s = time[i].split(':')
            if int(h) == 0 and int(prevTime.split(':')[0]) == 23:
                d.append(i)
            prevTime = time[i]
            time[i] = len(d)*24*3600 + int(h)*3600 + int(m)*60 + int(float(s))
        
        time = np.array(time)
        time = time - time[0]            # Set initial time to zero    
        
        # Convert list to 2D numpy float array
        fileID      =   np.array(fileID)
        header      =   np.array(header)
        columnName  =   np.array(columnName) 
        
        calibData   =   np.array(calibData) 
        
        data = np.array(data)
        data = data.astype(np.float)
            
        
        # Search for changes in modes
        change = mode[0] # Initial value
        modeChange = [change]
        for val, id in enumerate(mode):
            if change != mode[val]:
                change = id
                modeChange.append(id+' '+str(val))
        
        # Return one array for consistency
        bundleAllInfo = [fileID, header, calibData, columnName, time, modeChange, data]
        return bundleAllInfo
    
    
        # TODO: Must fix LVM reader for coldroom triaxial
    ## Adapted to fit with weird triaxial data in cooling room 
    else:
        header      =   lines[numbering[0]+1:numbering[1]]
        calibData   =   lines[numbering[1]+1:numbering[2]]
        columnName  =   lines[numbering[2]+1:numbering[3]]
        dat_1       =   lines[numbering[3]+1:numbering[4]-3] 
        dat_2       =   lines[numbering[4]+1:] 
        data        =   dat_1 + dat_2
        del dat_1, dat_2
    
    
        # Convert comma to dot in data
        for val, id in enumerate(data):
            data[val] = id.replace(",", ".")   
        
        for val, id in enumerate(calibData):
            calibData[val] = id.replace(",", ".")


        # Split stri--ng data into lists
        fileID = re.split(r'\t+', fileID.rstrip('\n'))
        
        for i in range(len(header)):
            header[i] = re.split(r'\t+', header[i].rstrip('\n'))
            if  'Depth' in header[i]:
                # Convert comma to dot in depth
                header[i][1] = header[i][1].replace(",", ".") 
            
        for i in range(len(calibData)):
            calibData[i] = re.split(r'\t+', calibData[i].rstrip('\n'))
            
        for i in range(len(columnName)):
            columnName[i] = re.split(r'\t+', columnName[i].rstrip('\n'))
            
        for i in range(len(data)):
            data[i] = re.split(r'\t+', data[i].rstrip('\n'))
        

        # Make array rectangular    
        if len(data[-1])>len(data[3]):
            extraInfoInData = data[-1].pop(-1) # Label in LVM
        
            
        # Store time and mode in new lists
        for i in range(len(data)):
            time.append(data[i].pop(0))  # Timestamp
            mode.append(data[i].pop(-1))  # Mode
        #     
        # if len(data[0])<len(data[3]):     # Add empty entries
        #     data[0].append(0)
        # 
        for i in range(len(data)):
            if len(data[i])<len(data[5]):     # Add empty entries
                data[i].append(0)
        
        # Convert timestamp to seconds
        d = []
        for i in range(len(time)):
            h, m, s = time[i].split(':')
            if int(h) == 0 and int(prevTime.split(':')[0]) == 23:
                d.append(i)
            prevTime = time[i]
            time[i] = len(d)*24*3600 + int(h)*3600 + int(m)*60 + int(float(s))
        
        time = np.array(time)
        time = time - time[0]            # Set initial time to zero    
        
        # Convert list to 2D numpy float array
        fileID       =   np.array(fileID)
        header       =   np.array(header)
        columnName   =   np.array(columnName) 
        
        calibData    =   np.array(calibData)
        
        data = np.array(data)
        data = data.astype(np.float)
            
        
        # Search for changes in modes
        change = mode[0] # Initial value
        modeChange = [change]
        for val, id in enumerate(mode):
            if change != mode[val]:
                change = id
                modeChange.append(id+' '+str(val))

        # Return one array for consistency
        bundleAllInfo = [fileID, header, calibData, columnName, time, modeChange, data]
        return bundleAllInfo


if __name__ == "__main__":
    import sys
    from PyQt4 import QtGui
    import numpy as np
    
    # # For testing
    filey = ".\\Raw files\\oedometer.lvm" 
    # filey = '.\\Raw files\\Cold Room\\Test4_Unknown.lvm' 
    # filey = '.\\Raw files\\Treax - 2015\\G5-1_CIUc_D9-30m.lvm'

    fileID, header, calibData, columnName, time, modeChange, data = readLVM(filey)


