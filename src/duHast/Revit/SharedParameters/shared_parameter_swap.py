"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a function to swap out one shard parameter for another.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The swap is done by:
- changing current shared parameter to a family parameter (dummy)
- deleting the old shared parameter definition
- swapping the family parameter (dummy) to the new shared parameter.

Note: storage types of old and new shared parameter need to be identical.

Parameter change directives are read from a .csv file:

- header row: yes
- column 1: current shared parameter name
- column 2: new shared parameter name
- column 3: fully qualified file path of shared parameter file
- column 4: Is parameter instance (True / False)
- column 5: parameter grouping name ( refer to module: RevitParameterGrouping)

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

import clr
import System

# import common library modules
# from duHast.APISamples.Common import RevitCommonAPI as com
from duHast.Utilities.Objects import result as res
from duHast.Utilities import files_csv as fileCSV
from duHast.Utilities.files_io import file_exist
from duHast.Revit.SharedParameters import shared_parameter_add as rSharedPAdd
from duHast.Revit.SharedParameters import shared_parameters_tuple as rSharedT
from duHast.Revit.Common import parameter_grouping as rPG
from duHast.Revit.SharedParameters import shared_parameters as rSharedPara
from duHast.Revit.SharedParameters import shared_parameters_delete as rSharedParaDelete
from duHast.Revit.SharedParameters import (
    shared_parameter_type_change as rSharedTypeChange,
)

from collections import namedtuple


"""
Tuple containing settings data on how to swap a shared parameter retrieved from a file.
"""

PARAMETER_SETTINGS_DATA = namedtuple(
    "parameterSettingsData", "oldParameterName newParameterData sharedParameterPath"
)


def _load_shared_parameter_data_from_file(file_path):
    """
    _summary_

    :param file_path: Fully qualified file path to shared parameter change directive file.
    :type file_path: str

    :return: A dictionary in format; key: current parameter name, value: named tuple of type parameterSettingsData
    :rtype: {str:named tuple}
    """

    parameter_mapper = {}
    file_data = fileCSV.read_csv_file(file_path)
    for i in range(1, len(file_data)):
        row = file_data[i]
        if len(row) == 5:
            flag = False
            if row[3].upper() == "TRUE":
                flag = True
            t = rSharedT.PARAMETER_DATA(
                row[1], flag, rPG.PRAMETER_GROPUING_TO_BUILD_IN_PARAMETER_GROUPS[row[4]]
            )
            parameter_mapper[row[0]] = PARAMETER_SETTINGS_DATA(row[0], t, row[2])
    return parameter_mapper


def swap_shared_parameters(doc, change_directive_file_path):
    """
    Swaps out a shared parameter for another. (refer to module header for details)

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param change_directive_file_path: Fully qualified file path to shared parameter change directive.
    :type change_directive_file_path: str

    :return:
        Result class instance.

        - False if an exception occurred, otherwise True.
        - result.message will contain the names of the changed shared parameter(s).
        - result status will contain lists of new shared parameters

        On exception (handled by optimizer itself!):

        - result.status (bool) will be False.
        - result.message will contain exception message.

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    _parameter_prefix_ = "_dummy_"

    # check if file exists
    if file_exist(change_directive_file_path) == False:
        return_value.update_sep(
            False,
            "Change directive file does not exist: {}".format(
                change_directive_file_path
            ),
        )
        return return_value

    # load change directive
    parameter_directives = _load_shared_parameter_data_from_file(
        change_directive_file_path
    )

    # check if there are any directives
    if len(parameter_directives) == 0:
        return_value.update_sep(False, "No parameter directives in file.")
        return return_value

    # loop over directive and
    for p_directive in parameter_directives:
        # load shared para file
        shared_para_def_file = rSharedPAdd.load_shared_parameter_file(
            doc, parameter_directives[p_directive].sharedParameterPath
        )
        return_value.append_message(
            "Read shared parameter file: {}".format(
                parameter_directives[p_directive].sharedParameterPath
            )
        )

        if shared_para_def_file != None:
            #   - swap shared parameter to family parameter
            status_change_to_fam_para = (
                rSharedTypeChange.change_shared_parameter_to_family_parameter(
                    doc, p_directive, _parameter_prefix_
                )
            )
            return_value.update(status_change_to_fam_para)
            if status_change_to_fam_para.status:
                #   - delete all shared parameter definition
                status_delete_old_shared_para_def = (
                    rSharedParaDelete.delete_shared_parameter_by_name(doc, p_directive)
                )
                return_value.update(status_delete_old_shared_para_def)
                if status_delete_old_shared_para_def.status:
                    # get shared parameter definition
                    s_para_def = rSharedPara.get_shared_parameter_definition(
                        parameter_directives[p_directive].newParameterData.name,
                        shared_para_def_file,
                    )
                    #   - add new shared parameter
                    if s_para_def != None:
                        return_value.append_message(
                            "Retrieved shared parameter definition for: {}".format(
                                parameter_directives[p_directive].newParameterData.name
                            )
                        )
                        #   - swap family parameter to shared parameter
                        status_swap_fam_to_shared_p = rSharedTypeChange.change_family_parameter_to_shared_parameter(
                            doc,
                            _parameter_prefix_ + p_directive,  # add prefix
                            parameter_directives[p_directive].newParameterData,
                            s_para_def,
                        )
                        return_value.update(status_swap_fam_to_shared_p)
                    else:
                        return_value.update_sep(
                            False,
                            "Failed to get shared parameter definition from file.",
                        )
                else:
                    return_value.update(status_delete_old_shared_para_def)
            else:
                return_value.update(status_change_to_fam_para)
        else:
            return_value.update_sep(
                False,
                "Failed to load shared parameter def file from: {}".format(
                    parameter_directives[p_directive].sharedParameterPath
                ),
            )

    return return_value
