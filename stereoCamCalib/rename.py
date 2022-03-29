import shutil
import os
from tabnanny import filename_only






numL = 7
numR = 8

datadirL = './caliImg/{}/'.format(numL)
framesL = [f for f in os.listdir(datadirL) if f.endswith(".jpg") ]
camL = 'cam{}'.format(numL)

datadirR = './caliImg/{}/'.format(numR)
framesR = [f for f in os.listdir(datadirR) if f.endswith(".jpg") ]
camR = 'cam{}'.format(numR)

hashMap = {}
for f in framesL:
    hashMap[f.replace(camL, "")] = f

count = 1
for f in framesR:
    name = f.replace(camR, '')
    filename = '{}.jpg'.format(count)
    if name in hashMap:
        os.rename(os.path.join(datadirL,hashMap[name]), os.path.join(datadirL, filename)) 
        os.rename(os.path.join(datadirR, f), os.path.join(datadirR, filename)) 
        count += 1

