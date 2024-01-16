'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains post reporting clean up functions:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

'''
#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2023, Jan Christel
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

# --------------------------
# Imports
# --------------------------


import settings as utilData # sets up all commonly used variables and path locations!
import Post_Output as pOut
# import common library
import Utility as util


# -------------
# my code here:
# -------------

def DeleteFileInInputDir():
    '''
    Deletes any files in the input directory.
    '''
    files = util.GetFilesSingleFolder(utilData.INPUT_DIRECTORY, '', '', utilData.REPORT_FILE_EXTENSION)
    if(len(files) > 0):
        for f in files:
            flagDelete = util.FileDelete(f)
            pOut.Output('Deleted marker file: ' + f+ ' [' + str(flagDelete) +']')
    else:
        pOut.Output('Input directory did not contain any files.')

def DeleteWorkingDirectories():
    '''
    Deletes the session ID directories in which all the single reports are saved.
    '''
    
    # clean up. get directories in output folder and delete them
    dirs = util.GetChildDirectories(utilData.OUTPUT_FOLDER)
    for dir in dirs:
        flagDelete = util.DirectoryDelete(dir)
        pOut.Output('Deleted directory: ' + str(dir) + ' [' + str(flagDelete) +']')