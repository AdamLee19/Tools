from re import I
import cv2, os
import numpy as np

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
        # board is 18 * 25, checker size is 15mm, ArUco size is 12mm
        
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






def getCamIntrin(frames = None, board = None):
        
        '''
                Returns the intrinsic parameters of a camera 

                Parameters:
                        frames (list): a list of images contain charuco board
                        board: charuco board, must be intialize first.

                Returns:
                        error: RMS error of calibration
                        intrin: 3 * 3 camera intrinsic parameter
                        distor: camera distortion 
                                Be careful with the distortion parameters. OpenCV could potentially generate upto 14 distortion parameters
                                However, the Thabo Beeler's paper uses k1 - k5 (or k1 k2 p1 p2 k3 in OpenCV). This means it includes both radial and tengential distortion
                                This is the reference of distortion parameters which used by Thabo Beeler: http://www.vision.caltech.edu/bouguetj/calib_doc/htmls/parameters.html
                                Here are some explanations: https://docs.opencv.org/3.4/dc/dbb/tutorial_py_calibration.html
        '''

        if not frames or len(frames) == 0:
                print("No image provided")
                exit(-1)
        if not board:
                print("No charuco board provided")
                exit(-1)
        

        print("INTRINSIC ESTIMATION STARTS:")
        
        img = cv2.imread(frames[0])
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
        imsize = gray.shape[::-1] # width, height

        # allCorners: stores detected CHESSBOARD board corners
        # allIds: stores the ids accossiated with the detected CHESSBOARD corners
        allCorners = []
        allIds = []

        for f in frames:
                print("=> Processing image {}".format(f))
                i = cv2.imread(f)
                c, id  = charucoPointsDetection(i, board)
                allCorners.append(c)
                allIds.append(id) 
        
       
        """
        Calibrates the camera using the dected corners.
        """
        print("CAMERA CALIBRATION")

        
        cameraMatrixInit = np.array([[ 100000.,    0., imsize[0]/2.],
                                        [    0., 100000., imsize[1]/2.],
                                        [    0.,    0.,           1.]])

        distCoeffsInit = np.zeros((5,1))

        
        # Thabo Beeler's paper didn't set the principal point at the center of the image
        # TODO: Test if set the pp at the center would improve the calibration percision. 
        #flags = (cv2.CALIB_FIX_PRINCIPAL_POINT) 
        flags = 0

        # the distCoeffs could be 4, 5, 8, or 12 elements based on the flag
        # Since Thabo Beeler only used up to 5 parameters, so k1 - k5 is enough
        (ret, camera_matrix, distortion_coefficients0,
        _, _) = cv2.aruco.calibrateCameraCharuco(
                        charucoCorners=allCorners,
                        charucoIds=allIds,
                        board=board,
                        imageSize=imsize,
                        cameraMatrix=cameraMatrixInit,
                        distCoeffs=distCoeffsInit,
                        flags=flags,
                        criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 1000000, 1e-9))
        
        return ret, camera_matrix, distortion_coefficients0




def saveCamParams(camNum, intrin, distor, size):
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
    
    fileName = os.path.join('camera/', '{}.cam'.format(name))
    with open(fileName, 'w') as f:
        header = 'name fx fy cx cy alpha nx ny k1 k2 k3 k4 k5 tx ty tz rx ry rz zn zf'
        data = '{} {} {} {} {} {} {} {} {} {} {} {} {} 0 0 0 0 0 0 0 0'.format(
                name,
                fx, fy,
                cx, cy,
                alpha,
                nx, ny,
                k1, k2, k3, k4, k5
            )
        
        f. writelines('\n'.join([header, data]))
        






if __name__ == '__main__':
        # set up charuco tyep        
        dictionary = cv2.aruco.Dictionary_get(CHARUCOTYPE)
        board = cv2.aruco.CharucoBoard_create(BOARDWIDTH, BOARDHIGHT, CHECKERSIZE, MARKERSIZE, dictionary)
       

        caliFolder = 'caliImg'

        camFolders = [os.path.join(caliFolder, f) for f in os.listdir(caliFolder) if os.path.isdir(os.path.join(caliFolder, f))]
        

        for cf in camFolders:
            camNum = int(cf.split('/')[-1])
            frames = [os.path.join(cf, f) for f in os.listdir(cf) if f.endswith(".JPG") ] 
            # OpenCV 'requires' at least 14 images to get a good calibration
            # if len(frames) == 0 or len(frames) < 14: exit(0)

            img =  cv2.imread(frames[0]) 
            grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
            error, cam_intrin, distor = getCamIntrin(frames, board)
            print('\tCalibration Error: {}'.format(error))
            saveCamParams(camNum, cam_intrin, distor, grey.shape[::-1])

        