import cv2




def drawDetectedMarkers(img, corners, detectedIDs = None):
        '''
                Helper function: Draw corners of the aruco markers 

                Parameters:
                        img: image with charuco board
                        corners: either detected marker corners or rejected marker corners.

                Returns:
                        img: image with markers drawn
        '''

        if detectedIDs is None:
                cv2.aruco.drawDetectedMarkers(img, corners, borderColor=(100, 0, 240))
        else:
                cv2.aruco.drawDetectedMarkers(img, corners, detectedIDs, borderColor=(100, 0, 240))
        
        return img

def draw_chorner_axis(img, corners, ids, cam_intrin, distor, board):

        '''
                Helper function: Asxis on the Charuco board

                Parameters:
                        img: image with charuco board
                        corners: either detected marker corners or rejected marker corners.
                        ids: 
                        cam_intrin: camera intrinsic parameter
                        distor: distortion of a camera
                        board: charuco type

                Returns:
                        img: image with axis drawn
        '''

        # use these lines to draw the detected corner and axis
        error, rvec, tvec = cv2.aruco.estimatePoseCharucoBoard(corners,  ids, board, cam_intrin, distor, None, None)
        cv2.aruco.drawAxis(img, cam_intrin, distor, rvec, tvec, 1)
        
        return img

def drawEpiLine(img):

        '''
                Helper function: draw apiline on rectified image (all lines are horizontal)

                Parameters:
                        img: rectified image

                Returns:
                        img: image with epiline drawn
        '''
        height = img.shape[0]
        width = img.shape[1]
        lines = 10
        steps = height // lines
        start = steps
        for i in range(lines):
                img = cv2.line(img, (0, start), (width, start), (255, 0, 0), 3)
                start += steps
        return img