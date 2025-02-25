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

import os

from duHast.Utilities.Objects.result import Result
from duHast.Utilities.files_get import get_files_from_directory_walker_with_filters_simple
from duHast.Utilities.files_io import file_exist, file_delete

def remove_obsolete_part_atom_exports(process_dirs):
    """
    Removes all xml files in the process directories with no associated family files.

    :param process_dirs: List of directories to process.
    :type process_dirs: list
    :return: Result object with status and message.
    :rtype: Result
    """

    # set up a status tracker
    return_value = Result()

    try:

        # build list of xml files in process directories
        xml_files = []

        for d in process_dirs:
            return_value.append_message("Processing directories: {}".format(d))
        
            # get all xml files in the library location
            xml_in_directory = get_files_from_directory_walker_with_filters_simple(d, ".xml")
            if xml_in_directory and len(xml_in_directory) > 0:
                xml_files = xml_files + xml_in_directory
        
        xml_files_delete = []
        # check if any files are missing their matching family file
        for xml in xml_files:
            rfa_file = os.path.splitext(xml)[0] + ".rfa"
            if not file_exist(rfa_file):
                xml_files_delete.append(xml)
               
        # delete the xml files
        for xml in xml_files_delete:
            deleted_flag = file_delete(xml)
            if not deleted_flag:
                return_value.update_sep(
                    False, "Failed to delete xml file: {}".format(xml)
                )
            else:
                return_value.append_message(
                    "Deleted: {}".format(xml)
                )
    
    except Exception as e:
        return_value.update_sep(
            False, "Failed to delete files with exception: {}".format(e)
        )

    return_value.append_message("Finished")
    return return_value