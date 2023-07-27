#!/usr/bin/python
# -*- coding: utf-8 -*-
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

import os

import settings as settings  # sets up all commonly used variables and path locations!
import duHast.Utilities.Objects.result as res
from duHast.Revit.Annotation.independent_tags_modify_properties import update_tag_locations_from_report
from duHast.Utilities.files_io import get_file_name_without_ext

def check_ffe_tags_locations(doc, revit_file_path, output):
    return_value = res.Result()
    output("Moving ffe tag instances back to original location...start")
    file_name = os.path.join(
        settings.OUTPUT_FOLDER,
        get_file_name_without_ext(revit_file_path)
        + settings.REPORT_EXTENSION_FFE_TAG_INSTANCES
        + settings.TEMP_FILE_NAME_EXTENSION,
    )

    task_value = update_tag_locations_from_report(doc, file_name, distance_threshold=50)
    return_value.update(task_value)
    return return_value