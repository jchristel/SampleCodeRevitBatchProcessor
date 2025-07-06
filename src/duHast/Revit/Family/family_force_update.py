"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit families helper functions forcing revit to recognize changes in families and reload it
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is achieved by creating a dummy type, saving the file, deleting the dummy type and saving the file again

"""

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

from duHast.Utilities.Objects.result import Result
from duHast.Revit.Family.family_types import create_family_type, delete_family_type
from duHast.Revit.Common.file_io import save_file

def force_family_update_on_reload(doc, output):
    """
    Forces revit to recognise a change in the family and do a full reload.
    This is achieved by creating a dummy type, saving the file, deleting the dummy type and saving the file again.

    :param doc: Revit Document
    :type doc: Document
    :param output: pyRevit output
    :type output: Output
   

    :return: Result
    """

    # set up a status tracker
    return_value = Result()

    dummy_type_name = "DummyType"

    try:

        # check output, needs to be a function accepting a string
        if not callable(output):
            message = "Output must be a callable function that accepts a string."
            return_value.update_sep(
                False,
                message,
            )
            return return_value

        # check if this is a family document
        if not doc.IsFamilyDocument:
            message = "This is not a family document. Aborting operation."
            output(message)
            return_value.update_sep(
                False,
                message,
            )
            return return_value

        # create a new dummy family type
        create_result = create_family_type(doc, dummy_type_name)
        # check if type was created successfully
        if not create_result.status:
            message =  "Failed to create a dummy family type. Aborting operation."
            output(message)
            return_value.update_sep(
                False,
                message,
            )
            return return_value
        else:
            message = "Successfully created a dummy family type."
            output(message)
            return_value.append_message(message)
        
        # save the family
        save_result = save_file(doc, True)
        # check if family was saved successfully
        if not save_result.status:
            message = "Failed to save the family. Aborting operation."
            output(message)
            return_value.update_sep(
                False,
                message,
            )
            return return_value
        else:
            message = "Successfully saved the family."
            output(message)
            return_value.append_message(message)
        
        # delete the family type
        delete_result = delete_family_type(doc, dummy_type_name)
        # check if type was deleted successfully
        if not delete_result.status:
            message = "Failed to delete the dummy family type. Aborting operation."
            output(message)
            return_value.update_sep(
                False,
                message,
            )
            return return_value
        else:
            message = "Successfully deleted the dummy family type."
            output(message)
            return_value.append_message(message)
       
        # save the family again
        save_again_result = save_file(doc, True)
        # check if family was saved successfully
        if not save_again_result.status:
            message = "Failed to save the family. Aborting operation."
            output(message)
            return_value.update_sep(
                False,
                message,
            )
            return return_value
        else:
            message = "Successfully saved the family."
            output(message)
            return_value.append_message(message)
        
        message = "Successfully forced update to family."
        output(message)
        return_value.append_message(message)

    except Exception as e:
        output("An exception occurred: {}".format(e))
        return_value.update_sep(
            False, "Failed to force update to family with exception: {}".format(e)
        )

    return return_value