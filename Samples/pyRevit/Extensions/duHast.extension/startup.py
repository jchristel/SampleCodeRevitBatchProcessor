# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2025, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed.
# In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits;
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
#


import clr
import System
from System.IO import File
from System.IO import MemoryStream
from System.Reflection import Assembly
import traceback


# set up a debug flag 
DEBUG = False

# get the revit version to load the correct assemblies
REVIT_VERSION = None
try:
    # get the ui application provided by pyRevit
    uiapp = __revit__

    # get the application from the ui application
    app = uiapp.Application

    # get the version number from the application
    REVIT_VERSION = app.VersionNumber

    # print the version number if debug is enabled
    if DEBUG:
        print("Running Revit: {REVIT_VERSION}".format(REVIT_VERSION=REVIT_VERSION))
except Exception as e:
    print("Exception: {e}".format(e=e))

# do not load these, since they are the external command and dont need to be loaded
ignore_dlls = [
]

# Load the DLLs required for the extension
# build the bin path
bin_directory_within_extension=r"bin"
# file path of this file
startup_file_path = __file__
# get the directory of the startup file
startup_directory = System.IO.Path.GetDirectoryName(startup_file_path)

# build the full path to the bin directory\
bin_directory = System.IO.Path.Combine(startup_directory, bin_directory_within_extension)

# get all dlls in the bin directory
dlls_to_load  = System.IO.Directory.GetFiles(bin_directory, "*.dll")


for dll in dlls_to_load:

    try:
        # get the file name from the path
        dll_name_only = System.IO.Path.GetFileName(dll)
        
        # check if the dll should be ignored
        if dll_name_only in ignore_dlls:
            if DEBUG:
                print("Ignoring: {dll}".format(dll=dll_name_only))
            continue

        if DEBUG:
            print("Attempting to load: {dll}".format(dll=dll_name_only))
        
        # Check if the file exists
        if not File.Exists(dll):
            print("File not found: {dll}".format(dll=dll))
            continue

        dll_bytes = File.ReadAllBytes(dll)

        if DEBUG:
            # Should print <class 'bytearray'>
            print("bytes array is of type: {}".format(type(dll_bytes)))
    
        # Load assembly into the default AppDomain
        stream = MemoryStream(dll_bytes)
        assembly = Assembly.Load(stream.ToArray())

        # Ensure it's registered for other add-ins
        System.AppDomain.CurrentDomain.Load(assembly.GetName())

        if DEBUG:
            print("loaded successfully: {dll}".format(dll=dll_name_only))

    except Exception as e:
        print("Failed to load {dll} with exception: {e}".format(dll=dll, e=e))
        print(traceback.format_exc())
        continue

