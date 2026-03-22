#----------------------------------------------------------------
# Generated CMake target import file.
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "feetechlib::feetechlib" for configuration ""
set_property(TARGET feetechlib::feetechlib APPEND PROPERTY IMPORTED_CONFIGURATIONS NOCONFIG)
set_target_properties(feetechlib::feetechlib PROPERTIES
  IMPORTED_LOCATION_NOCONFIG "${_IMPORT_PREFIX}/lib/libfeetechlib.so"
  IMPORTED_SONAME_NOCONFIG "libfeetechlib.so"
  )

list(APPEND _IMPORT_CHECK_TARGETS feetechlib::feetechlib )
list(APPEND _IMPORT_CHECK_FILES_FOR_feetechlib::feetechlib "${_IMPORT_PREFIX}/lib/libfeetechlib.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
