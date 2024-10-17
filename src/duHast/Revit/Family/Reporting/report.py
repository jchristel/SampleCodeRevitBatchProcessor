"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module containing reporting functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- families

"""

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

# required for .ToList() on FilteredElementCollector
import clr, os

clr.AddReference("System.Core")
from System import Linq

clr.ImportExtensions(Linq)

# import Autodesk
from Autodesk.Revit.DB import BuiltInCategory, Element
from System.Collections.Generic import List

from duHast.Utilities.Objects.result import Result
from duHast.Revit.Family.Utility import loadable_family_categories as rFamUtilCats
from duHast.Revit.Family.family_utils import (
    get_family_symbols,
    get_family_instances_by_symbol_type_id,
)
from duHast.Revit.Common.parameter_get_utils import get_parameter_value_by_name
from duHast.Utilities.utility import encode_utf8
from duHast.UI.Objects.ProgressBase import ProgressBase

# default list of parameters to report on
FAMILY_PARAMETERS_TO_REPORT = [
    "Sample Parameter One",
    "Sample Parameter Two",
    "Sample Parameter Three",
]


def report_loaded_families(doc, parameter_names_filter = FAMILY_PARAMETERS_TO_REPORT , progress_callback=None ):
    """
    Reports on loaded families:

    - family name
    - family type
    - family category
    - specific family type parameters and their values
    - family instances placed by by type in model


    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: A function piping messages to designated target.
    :type output: func(message)

    :return:
        Result class instance.

        - result.status False if an exception occurred, otherwise True.
        - result.message will contain processing messages.
        - result.result family data array

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.result will be an empty list

    :rtype: :class:`.Result`
    """


    return_value = Result()


    # check callback class
    if(progress_callback and isinstance(progress_callback, ProgressBase)==False ):
        raise TypeError("Output needs to be inheriterd from ProgressBase. Got : {} instead.".format(type(progress_callback)))

    # give some initial update
    if(progress_callback):
        progress_callback.update(0, 1, message="Reporting families...start")
        
    
    # build list of all categories we want families to be reloaded of
    # TODO: add new Revit categories 
    famCats = List[BuiltInCategory](rFamUtilCats.CATEGORIES_LOADABLE_TAGS)
    famCats.AddRange(rFamUtilCats.CATEGORIES_LOADABLE_TAGS_OTHER)
    famCats.AddRange(rFamUtilCats.CATEGORIES_LOADABLE_3D)
    famCats.AddRange(rFamUtilCats.CATEGORIES_LOADABLE_3D_OTHER)

    # get all symbols in file
    family_symbols = get_family_symbols(doc, famCats)
    # get families from symbols and filter out in place families
    # get data in format:
    #   revit file name , family name, family symbol name, instances placed
    data = []
    try:
        revit_project_file_name = doc.Title

        # get some progress data
        fam_counter = 0
        max_fam_counter = len(family_symbols.ToList())
        
        # loop over all family types in the model
        for family_symbol in family_symbols:
            # update progress
            if(progress_callback):
                progress_callback.update(fam_counter, max_fam_counter)
            
            # build new data row
            row_data = []
            if family_symbol.Family.IsInPlace == False:
                custom_parameter_values = []
                for parameter_name in parameter_names_filter:
                    parameter_value = get_parameter_value_by_name(
                        family_symbol, parameter_name
                    )
                    if parameter_value == None:
                        parameter_value = "NA"
                    custom_parameter_values.append(parameter_value)

                family = doc.GetElement(family_symbol.Family.Id)
                collector_instances_placed = get_family_instances_by_symbol_type_id(
                    doc, family_symbol.Id
                )
                count_instances = len(collector_instances_placed.ToList())
                category = family.FamilyCategory

                row_data = [
                    revit_project_file_name,
                    encode_utf8(Element.Name.GetValue(family)),
                    encode_utf8(Element.Name.GetValue(family_symbol)),
                    category.Name,
                    str(count_instances),
                ]

                # insert parameter values at index 4
                if len(custom_parameter_values) > 0:
                    row_data[4:4] = custom_parameter_values

                data.append(row_data)

                # update progress:
                fam_counter =fam_counter + 1

                # check for user cancel
                if progress_callback != None:
                    if progress_callback.is_cancelled():
                        return_value.append_message("User cancelled!")
                        break

    except Exception as e:
        return_value.update_sep(False, "Failed to gather family data with exception: {}".format(e))

    return_value.result = data
    return return_value