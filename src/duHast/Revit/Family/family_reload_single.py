"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions to load or reload families 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
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
#


import clr


# class used for stats reporting
from duHast.Utilities.Objects import result as res

from duHast.Revit.Family.family_utils import load_family
from duHast.Revit.Common import delete as rDel


def reload_family(doc, family, family_file_path):
    """
    Loads or reloads a single family into a Revit document.

    Will load/ reload family provided in in path. By default the parameter values in the project file will be overwritten
    with parameter values in family.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param family_file_path: The fully qualified file path of the family to be re-loaded.
    :type family_file_path: str
    :raise: None

    :return:
        Result class instance.

        - Reload status (bool) returned in result.status.
        - Reload status returned from Revit in result.message property.
        - Return family reference stored in result.result property on successful reload only

        On exception

        - Reload.status (bool) will be False
        - Reload.message will contain the exception message

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    try:

        # get all symbols attached to this family by name
        prior_load_symbol_ids = family.GetFamilySymbolIds()

        # load the family
        load_result = load_family(doc=doc, family_file_path=family_file_path)
        return_value.append_message(load_result.message)

        # do I need to get that family from the reload or can I get it from the project again??
        if(len(load_result.result)>0):
            fam_loaded = load_result.result[0]
            after_load_symbol_ids = fam_loaded.GetFamilySymbolIds()
            new_symbol_ids =  [item for item in after_load_symbol_ids if item not in prior_load_symbol_ids]
            if len(new_symbol_ids) > 0:
                result_delete = rDel.delete_by_element_ids(
                    doc,
                    new_symbol_ids,
                    "Delete new family types",
                    "Family types",
                )
                return_value.append_message(result_delete.message)
            else:
                return_value.append_message("The reload did not add any new types to the project")

    except Exception as e:
        return_value.update_sep(False, "Failed to load families with exception: " + str(e))
    return return_value
