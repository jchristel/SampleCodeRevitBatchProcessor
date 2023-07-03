#!/usr/bin/python
# -*- coding: utf-8 -*-
# License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
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