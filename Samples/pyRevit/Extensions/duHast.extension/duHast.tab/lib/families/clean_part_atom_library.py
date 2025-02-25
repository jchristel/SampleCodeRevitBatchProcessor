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


from duHast.Utilities.Objects.result import Result
from duHast.Revit.Family.Utility.xml_remove_obsolete_exports.py import remove_obsolete_part_atom_exports
from duHast.pyRevit.directory_picker import get_process_directories
from duHast.pyRevit.console_output import print_header

def clean_part_atom_exports_in_library_entry(doc, output, forms):
    """
    Removes all xml files in the library location With no associated family files.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output.
    :type output: pyRevit.output
    :param forms: pyRevit forms.
    :type forms: pyRevit.forms
    :return: Result object with status and message.
    :rtype: Result
    """

    # set up a status tracker
    return_value = Result()

    try:

        print_header("Getting directories")

         # get user to select library directories to process
        process_dirs_result = get_process_directories(forms)
        if not process_dirs_result.status:
            print(process_dirs_result.message)
            return_value.update_sep(False, process_dirs_result.message)
            return return_value

        # get the directories to process
        process_dirs = process_dirs_result.result

        # get the clean up result
        clean_up_result = remove_obsolete_part_atom_exports(process_dirs)

        # update the return value
        return_value.update(clean_up_result)
    
    except Exception as e:
        return_value.update_sep(
            False, "Failed to delete files with exception: {}".format(e)
        )

    print("\n{}".format(return_value.message))

    return return_value
