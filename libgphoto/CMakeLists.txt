#[[
    This cmake file only works on Apple computer
]]

cmake_minimum_required(VERSION 3.0)



set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")



project(camera)

include_directories(
    include
    /usr/local/include
)

link_directories(
    /usr/local/lib
)



file(GLOB LIBS "lib/*.c")

add_executable(
    camera
    # src/getCamNamePort.cpp
    src/capture.cpp    
    ${LIBS}
)


target_link_libraries(camera gphoto2) # equal to add -lgphoto2 to flag
target_link_libraries(camera gphoto2_port) # equal to add -lgphoto2_port to flag