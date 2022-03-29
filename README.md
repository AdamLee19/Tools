# Tools
Some Tools for Various Purposes

## stereoCamCalib
For stereo camera calibration
-- cali_intrin.py: compute camera intrinsic parameters
-- cali_stereo.py: compute rotation matrix between two cameras
-- caliImg: images for camera calibration
    |-- 1: camera 1
        |--: 1.jpg: first camera of camera 1
        |--: 2.jpg: second camera of camera 1
        ...
    |-- 2: camera 2
        |--: 1.jpg: first camera of camera 2
        ...
    ... 
-- camera: parameters for each camera ([Format] (https://cgl.ethz.ch/publications/papers/paperBee10.php))