import cv2 as cv, os, shutil

def readRaw(path, rawpyGammaParams=None, original_dimension = (4000, 6000), noAutoBright=True):
    import rawpy
    rawpyGammaParams=(20,20)
    orig_w, orig_h = original_dimension
    with rawpy.imread(path) as raw:
        if rawpyGammaParams is not None:
            img = raw.postprocess(gamma=rawpyGammaParams, no_auto_bright=noAutoBright)
        else:
            img = raw.postprocess(no_auto_bright=noAutoBright)
    img = cv.cvtColor(img, cv.COLOR_RGB2BGR)
    h, w, _ = img.shape
    # according to: https://stackoverflow.com/questions/59848795/reading-in-raw-image-is-larger
    # Camera sensors include extra pixels on the borders that are intended for black level detection and algorithms that require extra overreach.
    # I decide to just simply crop images
    start_h = int((h - orig_h) / 2)
    start_w = int((w - orig_w) / 2) 
    
    return img[start_h:h - start_h, start_w:w - start_w]


# copyFrom = './converted/'
# copyTo = './caliImg/'

# frames = [os.path.join(copyFrom, f) for f in os.listdir(copyFrom) if f.endswith(".png") ] 

# for f in frames:
   
#     fName = f.split('/')[-1][:-4]
#     folderNum = fName.split('_')[-1]
#     charucoNum = fName.split('_')[-2][7:]
#     shutil.copy(f, os.path.join(copyTo, folderNum,charucoNum +'.jpg')) 



im = readRaw('5.nef')
cv.imwrite('5.jpg', im)