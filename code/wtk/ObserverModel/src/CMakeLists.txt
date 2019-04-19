cmake_minimum_required(VERSION 3.12)

SET(SOULIST_SRC main.cc)

ADD_EXECUTABLE(test ${SOULIST_SRC})

# 用以编译shared_ptr
if(UNIX)  
    SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -std=gnu++0x")  
endif()  
