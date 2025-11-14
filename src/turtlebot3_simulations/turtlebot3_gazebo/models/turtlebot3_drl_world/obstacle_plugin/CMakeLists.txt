################################################################################
# CMake
################################################################################
cmake_minimum_required(VERSION 2.8 FATAL_ERROR)

################################################################################
# Packages
################################################################################
find_package(gazebo REQUIRED)

################################################################################
# Build
################################################################################
link_directories(${GAZEBO_LIBRARY_DIRS})

include_directories(${GAZEBO_INCLUDE_DIRS})

list(APPEND CMAKE_CXX_FLAGS "${GAZEBO_CXX_FLAGS}")
add_library(obstacle12_1 SHARED obstacle12_1.cc)
target_link_libraries(obstacle12_1 ${GAZEBO_LIBRARIES})
add_library(obstacle2 SHARED obstacle2.cc)
target_link_libraries(obstacle2 ${GAZEBO_LIBRARIES})
add_library(obstacle7_1 SHARED obstacle7_1.cc)
target_link_libraries(obstacle7_1 ${GAZEBO_LIBRARIES})
add_library(obstacle3 SHARED obstacle3.cc)
target_link_libraries(obstacle3 ${GAZEBO_LIBRARIES})
add_library(obstacle200 SHARED obstacle200.cc)
target_link_libraries(obstacle200 ${GAZEBO_LIBRARIES})
add_library(obstacle6_1 SHARED obstacle6_1.cc)
target_link_libraries(obstacle6_1 ${GAZEBO_LIBRARIES})
add_library(obstacle5_2 SHARED obstacle5_2.cc)
target_link_libraries(obstacle5_2 ${GAZEBO_LIBRARIES})
add_library(obstacle4 SHARED obstacle4.cc)
target_link_libraries(obstacle4 ${GAZEBO_LIBRARIES})
add_library(obstacle4_1 SHARED obstacle4_1.cc)
target_link_libraries(obstacle4_1 ${GAZEBO_LIBRARIES})
add_library(obstacle8 SHARED obstacle8.cc)
target_link_libraries(obstacle8 ${GAZEBO_LIBRARIES})
add_library(obstacle6 SHARED obstacle6.cc)
target_link_libraries(obstacle6 ${GAZEBO_LIBRARIES})
add_library(obstacle2_1 SHARED obstacle2_1.cc)
target_link_libraries(obstacle2_1 ${GAZEBO_LIBRARIES})
add_library(obstacle7 SHARED obstacle7.cc)
target_link_libraries(obstacle7 ${GAZEBO_LIBRARIES})
add_library(obstacle1 SHARED obstacle1.cc)
target_link_libraries(obstacle1 ${GAZEBO_LIBRARIES})
add_library(obstacle11 SHARED obstacle11.cc)
target_link_libraries(obstacle11 ${GAZEBO_LIBRARIES})
add_library(obstacle2_2 SHARED obstacle2_2.cc)
target_link_libraries(obstacle2_2 ${GAZEBO_LIBRARIES})
add_library(obstacle5 SHARED obstacle5.cc)
target_link_libraries(obstacle5 ${GAZEBO_LIBRARIES})
add_library(obstacle3_2 SHARED obstacle3_2.cc)
target_link_libraries(obstacle3_2 ${GAZEBO_LIBRARIES})
add_library(obstacle12 SHARED obstacle12.cc)
target_link_libraries(obstacle12 ${GAZEBO_LIBRARIES})
add_library(obstacle3_1 SHARED obstacle3_1.cc)
target_link_libraries(obstacle3_1 ${GAZEBO_LIBRARIES})
add_library(obstacle5_1 SHARED obstacle5_1.cc)
target_link_libraries(obstacle5_1 ${GAZEBO_LIBRARIES})
add_library(obstacle8_1 SHARED obstacle8_1.cc)
target_link_libraries(obstacle8_1 ${GAZEBO_LIBRARIES})
add_library(obstacle9 SHARED obstacle9.cc)
target_link_libraries(obstacle9 ${GAZEBO_LIBRARIES})
add_library(obstacle201 SHARED obstacle201.cc)
target_link_libraries(obstacle201 ${GAZEBO_LIBRARIES})
