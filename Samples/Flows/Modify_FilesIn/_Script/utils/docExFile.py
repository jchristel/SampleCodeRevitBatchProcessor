"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a class used to retrieve csv file stored file data.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2024, Jan Christel
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

import settings as settings  # sets up all commonly used variables and path locations!

# inherits from base class
from duHast.Utilities.Objects.base import Base

# dictionary containing csv file column mapping
CSV_COLUMN_MAPPING = {
    "existing_file_name": 0,
    "new_file_name": 1,
    "levels_and_grids_workset": 2,
    "revision": 3,
    "file_extension": 4,
    "file_in_filing": 5,
    "save_as_location": 6
}


# a class used to store file date for renaming
class docExFile( Base ) :
    """
    A class used to store file data required to:

    - rename files 
    - move files to new location
    - file files in correct directory
    
    """

    def __init__(self, data): 
        """
        Constructor for docExFile class
        :param data: list of strings containing file data
        :type data: list
        """

        super(docExFile, self).__init__()
        
        try:
            # do some checking first
            if(isinstance(data, list) == False):
                raise Exception("Invalid data format. Expecting a list of strings.")
            if(len(data) < 7):
                raise Exception("Invalid data format. Expecting a list of 7 strings.")
            
            self.existing_file_name = data[CSV_COLUMN_MAPPING["existing_file_name"]]
            self.new_file_name = data[CSV_COLUMN_MAPPING["new_file_name"]]
            self.levels_and_grids_workset = data[CSV_COLUMN_MAPPING["levels_and_grids_workset"]]
            if(len(data[3]) > 0):
                self.revision = data[CSV_COLUMN_MAPPING["revision"]]
            else:
                self.revision = settings.DEFAULT_REVISION
            self.file_extension = data[CSV_COLUMN_MAPPING["file_extension"]]
            self.file_in_filing = data[CSV_COLUMN_MAPPING["file_in_filing"]]
            self.save_as_location = data[CSV_COLUMN_MAPPING["save_as_location"]]
            self.revision_date = settings.DEFAULT_REVISION # assume revision date is unknown at initialization
            self.row_header = data[CSV_COLUMN_MAPPING["new_file_name"]]
        except Exception as e:
            raise e
