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
import clr

clr.AddReference("System.Core")
from System import Linq

clr.ImportExtensions(Linq)

# import Autodesk
from Autodesk.Revit.DB import BuiltInCategory, BuiltInParameter, Element, ElementClassFilter,FamilyInstance
from System.Collections.Generic import List

from duHast.Utilities.Objects.result import Result
from duHast.Utilities.Objects.timer import Timer

from duHast.Revit.Common.revit_version import get_revit_version_number
from duHast.Revit.Family.Utility import loadable_family_categories as rFamUtilCats
from duHast.Revit.Family.family_utils import (
    get_family_symbols,
    get_family_instances_by_symbol_type_id,
    is_shared_from_symbol
)
from duHast.Revit.Common.parameter_get_utils import get_parameter_value_by_name
from duHast.UI.Objects.ProgressBase import ProgressBase

# default list of parameters to report on
FAMILY_PARAMETERS_TO_REPORT = [
    "Sample Parameter One",
    "Sample Parameter Two",
    "Sample Parameter Three",
]

from duHast.Revit.Family.Reporting.Objects.family_report_data import (
    FamilyReportData,
    UNKNOWN_HOST_STATUS,
)


def _get_type_properties_of_interest(
    family_symbol, parameter_names_filter, family_container
):
    """
    Get type properties matching property names in filter.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param parameter_names_filter: List of parameter nams of which to get values.
    :type parameter_names_filter: [str]
    :param family_container: The family data container.
    :type family_container: :class:`.FamilyReportData`
    """

    # get all type parameters of interest
    for parameter_name in parameter_names_filter:
        parameter_value = get_parameter_value_by_name(family_symbol, parameter_name)
        family_container.add_type_property({parameter_name: parameter_value})


def _get_instances_placed(doc, family_symbol):
    """
    Return number of instances in the model

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param family_symbol: A family type
    :type family_symbol: Autodesk.Revit.DB.FamilySymbol

    :return: Number of instances placed.
    :rtype: int
    """

    collector_instances_placed = get_family_instances_by_symbol_type_id(
        doc, family_symbol.Id
    )
    return len(collector_instances_placed.ToList())


def _get_instances_placed_revised(doc, family_symbol):
    """
    Return number of instances in the model ( fast!)

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param family_symbol: A family type
    :type family_symbol: Autodesk.Revit.DB.FamilySymbol

    :return: Number of instances placed.
    :rtype: int
    """

    filter = ElementClassFilter(FamilyInstance)
    dependent_element_ids = family_symbol.GetDependentElements(filter)

    # this is an IList, therefore I should be able to return Count
    return dependent_element_ids.Count


def _get_host_family_status(doc, family_symbol):
    """
    Returns a list of nested shared families within host family

    This will only work if there is an instance placed in the model....

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param family_symbol: A family type
    :type family_symbol: Autodesk.Revit.DB.FamilySymbol

    :return: List of family names and type names in format family name - type name
    :rtype: [str]
    """

    nested_family_names = []
    # get all instances in the model

    filter = ElementClassFilter(FamilyInstance)
    instances_element_ids = family_symbol.GetDependentElements(filter)
    #instances = get_family_instances_by_symbol_type_id(doc, family_symbol.Id)

    # get the first one
    for family_instance_id in instances_element_ids:
        family_instance = doc.GetElement(family_instance_id)
        # check if any nested shared families are in play
        try:
            sub_element_ids = family_instance.GetSubComponentIds()
            if sub_element_ids is not None:
                for sub_element_id in sub_element_ids:
                    try:
                        # get the family name and type name
                        nested_instance = doc.GetElement(sub_element_id)
                        nested_type = nested_instance.Symbol
                        nested_family = nested_type.Family
                        name = "{}-{}".format(
                                Element.Name.GetValue(nested_family),
                                Element.Name.GetValue(nested_type),
                            )
                        if name not in nested_family_names:
                            nested_family_names.append(name)
                    except Exception as e:
                        pass
        except Exception as e:
            # some family categories do not have GetSubComponentIds() available, i.e. Tags
            pass
        
        # get out
        break
        
    return nested_family_names


def report_loaded_families(
    doc, parameter_names_filter=FAMILY_PARAMETERS_TO_REPORT, progress_callback=None
):
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
    if progress_callback and isinstance(progress_callback, ProgressBase) == False:
        raise TypeError(
            "Output needs to be inherited from ProgressBase. Got : {} instead.".format(
                type(progress_callback)
            )
        )

    # give some initial update
    if progress_callback:
        progress_callback.update(0, 1, message="Reporting families...start")

    # build list of all categories we want families to be reloaded of
    famCats = List[BuiltInCategory](rFamUtilCats.CATEGORIES_LOADABLE_TAGS)
    famCats.AddRange(rFamUtilCats.CATEGORIES_LOADABLE_TAGS_OTHER)
    famCats.AddRange(rFamUtilCats.CATEGORIES_LOADABLE_3D)
    famCats.AddRange(rFamUtilCats.CATEGORIES_LOADABLE_3D_OTHER)

    #set up a timer
    t=Timer()
    t.start()
    # check Revit version and if 2022 and later, add new categories
    revit_version = get_revit_version_number(doc=doc)

    # log progress
    return_value.append_message("Retrieved Revit version {}. {}".format(revit_version, t.stop()))

    if revit_version >= 2022:
        famCats.AddRange(rFamUtilCats.CATEGORIES_LOADABLE_3D_REVIT_2022)
        famCats.AddRange(rFamUtilCats.CATEGORIES_LOADABLE_TAGS_REVIT_2022)

    t.start()
    # get all symbols in file
    family_symbols = get_family_symbols(doc, famCats)

    # log progress
    return_value.append_message("Got symbols in model. {}".format(t.stop()))
    
    # get families from symbols and filter out in place families
    data = []

    try:
        revit_project_file_name = doc.Title

        # get some progress data
        fam_counter = 0
        max_fam_counter = len(family_symbols.ToList())


        # loop over all family types in the model
        for family_symbol in family_symbols:
            # update progress
            if progress_callback:
                progress_callback.update(fam_counter, max_fam_counter)

            # build new data entry
            family_container = FamilyReportData()
            
            if family_symbol.Family.IsInPlace == False:
                 # get the project name
                family_container.project_name = revit_project_file_name
                # get the family name
                family_container.family_name = Element.Name.GetValue(family_symbol.Family)
                # get the type name
                family_container.family_type_name = Element.Name.GetValue(family_symbol)

                t_symbol = Timer()
                t_symbol.start()

                # get type properties
                _get_type_properties_of_interest(
                    family_symbol=family_symbol,
                    parameter_names_filter=parameter_names_filter,
                    family_container=family_container,
                )

                # log progress
                return_value.append_message("{} {} Got properties of interest: {}".format(family_container.family_name, family_container.family_type_name, t_symbol.stop()))
                t_symbol.start()

                # get number of instances placed
                family_container.family_instances_placed = _get_instances_placed_revised(
                    doc=doc, family_symbol=family_symbol
                )
                # log progress
                return_value.append_message("{} {} Got number of instances placed: {}".format(family_container.family_name, family_container.family_type_name, t_symbol.stop()))
                
                # get the family category
                family = doc.GetElement(family_symbol.Family.Id)
                family_container.family_category = family.FamilyCategory.Name

                t_symbol.start()
                # shared
                family_container.is_shared = is_shared_from_symbol(
                    family_symbol=family_symbol
                )

                # log progress
                return_value.append_message("{} {} Got is shared: {}".format(family_container.family_name, family_container.family_type_name,t_symbol.stop()))
                t_symbol.start()

                # check if this is a host family
                # this works only if a family instance is placed in the model :(
                if family_container.family_instances_placed > 0:
                    nested_shared_family_names = _get_host_family_status(
                        doc=doc,
                        family_symbol=family_symbol,
                    )
                    if len(nested_shared_family_names) > 0:
                        # record the nested family names
                            for fam_name in nested_shared_family_names:
                                family_container.add_nested_family(family_name=fam_name)
                elif (
                    family_container.family_instances_placed == 0
                ):
                    # put up note that status could not be determined...
                    # for now...
                    family_container.add_nested_family(UNKNOWN_HOST_STATUS)
                
                # log progress
                return_value.append_message("{} {} Got nested fams: {}".format(family_container.family_name, family_container.family_type_name,t_symbol.stop()))

                # add to return list
                data.append(family_container)

                # update progress:
                fam_counter = fam_counter + 1

                # check for user cancel
                if progress_callback != None:
                    if progress_callback.is_cancelled():
                        return_value.append_message("User cancelled!")
                        break

    except Exception as e:
        return_value.update_sep(
            False, "Failed to gather family data with exception: {}".format(e)
        )

    return_value.result = data
    return return_value
