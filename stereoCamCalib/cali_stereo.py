from re import I
import cv2, os
import numpy as np
import draw as dr

'''
        You will have to change those parameter. You could get those info from the web where the charuco board you bought
        Here is the web where we bought from: https://calib.io/collections/products/products/charuco-targets
        We have:
                plate Size (mm): 400 * 300 * 6
                Checker width (mm): 15
                Marker width (mm): 12
                Rows * Columns: 18 * 25
'''

CHARUCOTYPE = cv2.aruco.DICT_5X5_250
BOARDHIGHT = 18
BOARDWIDTH = 25
CHECKERSIZE = 15 # 15mm (you could choose any unit, but have to be consistant. I use mm)
MARKERSIZE = 12 # In OpenCV, marker refers to the Aruco patter. 









def charucoPointsDetection(img, board = None):
        if board == None:
                print("Please provide charuco type")
                exit(-1)
        
        dictionary = board.dictionary        
        
        
        # sub pixel refinement
        arucoParams = cv2.aruco.DetectorParameters_create()
        arucoParams.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX #subpix refinement would improve detecting result
        
        
       
        '''
        Corners: a list of corners of the detected markers (N). 
                For each marker, its four corners are returned in 
                their original order (which is clockwise starting with top left) (4, 2)
        ids: a list of ids of each of the detected markers in markerCorners (N) 
        rejectedImgPoints: a list of potential markers that were found but ultimately rejected (e.g. black tiles)
        '''
        corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(img,dictionary)
        # corners, ids, _, _ = cv2.aruco.refineDetectedMarkers(img, board, corners, ids, rejectedImgPoints)

        '''
                This function receives the detected markers and returns the 2D position of 
                the chessboard corners from a ChArUco board using the detected Aruco markers.
                retval: number of detected corners
        ''' 
        [retval, chessboard_corners_c, chessboard_ids_c] = cv2.aruco.interpolateCornersCharuco(corners, ids, img, board)
        print('\t{} points detected.'.format(retval))
        return chessboard_corners_c, chessboard_ids_c



def readCamParams(camNum):
        '''
            read camera parameter


            Parameters:
                        camNum: unique camera number


            Return:

                        intrin: 3 * 3 camera intrinsic matrix in numpy format
                        distor: ditortion coeffcients
                        size: image size (w, h)

    '''
        name = 'cam{}'.format(camNum)
        fileName = os.path.join('camera/', '{}.cam'.format(name))

        intrin = np.identity(3) # 3 * 3 indentity matrix
        distor = np.zeros((5, 1))
        

        with open(fileName, 'r') as f:
                f.readline().strip() # skip header
                data = f.readline().strip().split(' ')
                
                fx, fy = float(data[1]), float(data[2])
                cx, cy = float(data[3]), float(data[4])
                alpha = float(data[5])
                size = (int(data[6]), int(data[7]))
                k1, k2, k3, k4, k5 = float(data[8]), float(data[9]), float(data[10]), float(data[11]), float(data[12])

        intrin[0][0] = fx
        intrin[1][1] = fy
        intrin[0][2] = cx
        intrin[1][2] = cy
        intrin[0][1] = alpha
        distor = np.array([k1, k2, k3, k4, k5]).reshape((5, 1))
        
        return intrin, distor, size
        

def saveCamParams(camNum, intrin, distor, size, rot, trans):
    '''
            Save camera to a file


            Parameters:
                        camNum: unique camera number
                        intrin: 3 * 3 camera intrinsic matrix in numpy format
                                The description of camera matrix could be found: https://docs.opencv.org/3.4/d9/d6a/group__aruco.html#ga54cf81c2e39119a84101258338aa7383
                        distor: distortion coefficients. 
                        size: image size (w, h)



            The format is followed with Thabo Beeler's website: https://cgl.ethz.ch/publications/papers/paperBee10.php

            It consists of two lines; a header and the actual parameters. 
            The header describes the content of the parameters, possible values are:


            name: name of the camera
            fx, fy: focal length
            cx, cy: principal point
            alpha: skew
            nx, ny
            k1 ... k5: distortion parameters as described by Bouguet (it is k1 k2 p1 p2 k3 in OpenCV)
            
            
            --- The Following parameters are all 0 for now. They will be set after setero calibration for each pair ---
            tx, ty, tz: extrinsic translation
            rx, ry, rz: extrinsic rotation (given in Rodrigues notation)
            zn, zf: near and far planes of the working volume (don't know how to get this from OpenCV) TODO

    '''
    
    name = 'cam{}'.format(camNum)
    fx = intrin[0][0]
    fy = intrin[1][1]
    cx = intrin[0][2]
    cy = intrin[1][2]
    # OpenCV always sets alpha (skew) to 0
    alpha = intrin[0][1]
    (nx, ny) = size
    k1, k2, k3, k4, k5 = distor.flatten()
    rx, ry, rz = rot.flatten()
    tx, ty, tz = trans.flatten()
    
    fileName = os.path.join('camera/', '{}.cam'.format(name))
    with open(fileName, 'w') as f:
        header = 'name fx fy cx cy alpha nx ny k1 k2 k3 k4 k5 tx ty tz rx ry rz zn zf'
        data = '{} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} 0 1500'.format(
                name,
                fx, fy,
                cx, cy,
                alpha,
                nx, ny,
                k1, k2, k3, k4, k5,
                tx, ty, tz,
                rx, ry, rz,
            )
        
        f. writelines('\n'.join([header, data]))
        



def getObjsAndImgPtsFromLR(cornersL, idsL, cornersR, idsR, checkerSize = (17, 24)):
        '''
                Here is how OpenCV contructs 3D objct points: 
                contruct a 3D points from Charuco board (We can say chess board was kept stationary at XY plane, (so Z=0 always) and camera was moved accordingly)
                for X,Y values, we can simply pass the points as (0,0), (1,0), (2,0), ... which denotes the location of points. 
                In this case, the results we get will be in the scale of size of chess board square. 
                But if we know the square size, (say 30 mm), we can pass the values as (0,0), (30,0), (60,0), ... . 
                Thus, we get the results in mm. (In this case, we don't know square size since we didn't take those images, so we pass in terms of square size).

                Find correspondent chessboard corners from left and right images and construct a fake 3D object points in 3D


                Side Notes:
                Inner corner size is (17, 24), Original (18, 25)
                ids*: (# points, 1)
                corners*: (# points, 1, 2)
                contruct 3D obj points from both left image and right image


                Parameters:
                        corners*: a list of chessboard corners detected in different frames 
                        ids*: the correspond ids for chessboard corners
                        checkerSize: Inner corner size of Charuco board





        '''
        # total: total points should have
        total = checkerSize[0] * checkerSize[1]
        objp = np.zeros((total, 3), np.float32)
        objp[:,:2] = np.mgrid[0:checkerSize[1],0:checkerSize[0]].T.reshape(-1,2)
        objp = objp * CHECKERSIZE 
        
        # put everything in a hashTable (fast access)
        left, right = {}, {}

        id = idsL.flatten()
        for i, c in enumerate(cornersL): left[id[i]] = c
        id = idsR.flatten()
        for i, c in enumerate(cornersR): right[id[i]] = c
        
        

        objs, imgsL, imgsR = [], [], []
        for i in range(total):
                if i in left and i in right:
                        objs.append(objp[i])
                        imgsL.append(left[i])
                        imgsR.append(right[i])
                        
        return np.array(objs), np.array(imgsL), np.array(imgsR)


def detectCorners(frames, board):
        '''
                get Charuco corner points from a list of frames

                Parameters:
                        frames: a list of frames' paths
                        board: charuco board type
                Return:
                        allCorners: a list of chessboard corners of each frame
                        allIds: a list of chessboard ids accossiate with corners

        '''
        allCorners = []
        allIds = []
        for f in frames:
                print("=> Processing image {}".format(f))
                i = cv2.imread(f)
                c, id  = charucoPointsDetection(i, board)
                allCorners.append(c)
                allIds.append(id)
        return allCorners, allIds
        
if __name__ == '__main__':
        # set up charuco tyep        
        dictionary = cv2.aruco.Dictionary_get(CHARUCOTYPE)
        board = cv2.aruco.CharucoBoard_create(BOARDWIDTH, BOARDHIGHT, CHECKERSIZE, MARKERSIZE, dictionary)
        imgExt = '.png'

        camL = 4
        datadir = './caliImg/cam{}/'.format(camL)
        framesL = [datadir + f for f in os.listdir(datadir) if f.endswith(imgExt) ]
        
        framesL.sort(key = lambda name: int(name[ name.rfind('/') + 1 : name.rfind('.')])) # sort image by the number

        left_img = cv2.imread(framesL[0])
        left_grey = cv2.cvtColor(left_img, cv2.COLOR_BGR2GRAY)
        
        cam_intrinL, distorL, sizeL = readCamParams(camL)
        allCornersL, allIdsL = detectCorners(framesL, board) 
  
       

        camR = 5 
        datadir =  './caliImg/cam{}/'.format(camR)
        framesR = [datadir + f for f in os.listdir(datadir) if f.endswith(imgExt) ]
        framesR.sort(key = lambda name: int(name[ name.rfind('/') + 1 : name.rfind('.')])) # sort image by the number
        right_img = cv2.imread(framesR[0])
        right_grey = cv2.cvtColor(right_img, cv2.COLOR_BGR2GRAY)
        
        cam_intrinR, distorR, sizeR = readCamParams(camR)
        allCornersR, allIdsR = detectCorners(framesR, board) 



        # Stereo Calibration
        finalObjs = []
        finalPointsL = []
        finalPointsR = []
        for i in range(len(allIdsL)):
                o, l, r = getObjsAndImgPtsFromLR(allCornersL[i], allIdsL[i], allCornersR[i], allIdsR[i])
                if len(o) > 4:
                        finalObjs.append(o)
                        finalPointsL.append(l)
                        finalPointsR.append(r)


        
        
        ret, K1, D1, K2, D2, R, T, E, F  = cv2.stereoCalibrate(finalObjs, finalPointsL, finalPointsR, 
                cam_intrinL, distorL, cam_intrinR, distorR, sizeR,
                flags = cv2.CALIB_FIX_INTRINSIC | 0, 
                
                criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 10000, 1e-9))
        print("Stereo Calibration Error: {}".format(ret))        

        RT1 = np.eye(3)

        T1 = np.array([[0],[0],[0]]) 
        rt1, _ = cv2.Rodrigues(RT1)
        
        saveCamParams(4, K1, D1, sizeL, rt1, T1)
        RT2 = R @ RT1
        T2 = R @ T1 + T

        rt2, _ = cv2.Rodrigues(RT2) 

        saveCamParams(5, K2, D2, sizeR, rt2, T2)
        exit(0)
       
        rectL, rectR, projMatrixL, projMatrixR, Q, roi_L, roi_R = cv2.stereoRectify(K1, D1, K2, D2,
						sizeR, R, T, alpha = -1, flags =cv2.CALIB_FIX_INTRINSIC + cv2.CALIB_RATIONAL_MODEL + cv2.CALIB_FIX_PRINCIPAL_POINT )

   


        

        stereoMapL = cv2.initUndistortRectifyMap(K1, D1, rectL, projMatrixL, sizeL, cv2.CV_16SC2)
        undistortedL= cv2.remap(left_img, stereoMapL[0], stereoMapL[1], cv2.INTER_LANCZOS4, cv2.BORDER_CONSTANT, 0)
        undistoredL = dr.drawEpiLine(undistortedL)
        cv2.imwrite('left_test.jpg', undistortedL)


        stereoMapR = cv2.initUndistortRectifyMap(K2, D2, rectR, projMatrixR, sizeR, cv2.CV_16SC2)
        undistortedR= cv2.remap(right_img, stereoMapR[0],  stereoMapR[1], cv2.INTER_LANCZOS4, cv2.BORDER_CONSTANT, 0)
        undistoredR = dr.drawEpiLine(undistortedR)
        cv2.imwrite('right_test.jpg', undistortedR)

        