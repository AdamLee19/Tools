import shutil
import os


imDir = 'calib-xiang'

imgFrames = [f for f in os.listdir(imDir) if f.endswith('.jpg')]



for f in imgFrames:
    
    if 'cam1' in f:
        shutil.copy(os.path.join(imDir, f), os.path.join('caliImg', '1', f))
    elif 'cam2' in f:
        shutil.copy(os.path.join(imDir, f), os.path.join('caliImg', '2', f))
    elif 'cam3' in f:
        shutil.copy(os.path.join(imDir, f), os.path.join('caliImg', '3', f))
    elif 'cam4' in f:
        shutil.copy(os.path.join(imDir, f), os.path.join('caliImg', '4', f))
    elif 'cam5' in f:
        shutil.copy(os.path.join(imDir, f), os.path.join('caliImg', '5', f))
    elif 'cam6' in f:
        shutil.copy(os.path.join(imDir, f), os.path.join('caliImg', '6', f))
    elif 'cam7' in f:
        shutil.copy(os.path.join(imDir, f), os.path.join('caliImg', '7', f))
    elif 'cam8' in f:
        shutil.copy(os.path.join(imDir, f), os.path.join('caliImg', '8', f))