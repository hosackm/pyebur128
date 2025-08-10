cmake_minimum_required(VERSION 3.10)
project(pyebur128)

set(BUILD_SHARED_LIBS ON CACHE BOOL "" FORCE)

set(PY_IMPORT_NAME pyebur128)

add_subdirectory(extern/libebur128)

message(INFO "Running your CMAKE")

if(TARGET ebur128)
  if(APPLE)
    set_target_properties(
      ebur128 PROPERTIES INSTALL_RPATH "@loader_path/${CMAKE_INSTALL_LIBDIR}")
  else()
    set_target_properties(ebur128 PROPERTIES INSTALL_RPATH "$ORIGIN/${CMAKE_INSTALL_LIBDIR}")
  endif()
else()
  message(FATAL_ERROR "Expected target 'ebur128' not found. Run: git submodule update --init --recusive")
endif()

# might be able to get rid of this because it automatically copies include/ and lib/
# install(TARGETS ebur128
#   LIBRARY DESTINATION .
#   RUNTIME DESTINATION .
#   ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
# )
#

