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

from duHast.Revit.SharedParameters.shared_parameters import (
    get_all_shared_parameters,
    param_binding_exists_2023,
)
from duHast.Revit.Common.parameter_set_utils import (
    set_parameter_without_transaction_wrapper_by_name,
)
from duHast.Utilities.Objects.result import Result

from Autodesk.Revit.DB import Element


def get_parameter_name_by_guid(parameters, guid):
    """
    Returns the parameter name by guid

    :param parameters: The parameters.
    :type parameters: Autodesk.Revit.DB.ParameterSet
    :param guid: The guid of the parameter.
    :type guid: str

    :return: The parameter name.
    :rtype: str
    """

    for parameter in parameters:
        if parameter.GuidValue.ToString() == guid:
            return parameter.GetDefinition().Name

    return None


def get_shared_parameter_data(doc, room):
    """
    Returns shared parameter data for a room

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param room: The room.
    :type room: Room

    :return: Shared parameter data.
    :rtype: [dict]
    """

    data = []

    # get shared parameters from revit document
    shared_parameters = get_all_shared_parameters(doc)

    id_parameter_name = get_parameter_name_by_guid(
        shared_parameters, room.id.parameter_guid
    )
    data.append({id_parameter_name: room.id.parameter_guid})

    area_briefed_parameter_name = get_parameter_name_by_guid(
        shared_parameters, room.area_briefed.parameter_guid
    )
    data.append({area_briefed_parameter_name: room.area_briefed.parameter_guid})

    area_design_parameter_name = get_parameter_name_by_guid(
        shared_parameters, room.area_designed.parameter_guid
    )
    data.append({area_design_parameter_name: room.area_designed.parameter_guid})

    room_name_short_parameter_name = get_parameter_name_by_guid(
        shared_parameters, room.room_name_short.parameter_guid
    )
    data.append({room_name_short_parameter_name: room.room_name_short.parameter_guid})

    department_parameter_name = get_parameter_name_by_guid(
        shared_parameters, room.department.parameter_guid
    )
    data.append({department_parameter_name: room.department.parameter_guid})

    sub_department_parameter_name = get_parameter_name_by_guid(
        shared_parameters, room.sub_department.parameter_guid
    )
    data.append({sub_department_parameter_name: room.sub_department.parameter_guid})

    for prop in room.other_properties:
        prop_name = get_parameter_name_by_guid(shared_parameters, prop.parameter_guid)
        data.append({prop_name: prop.parameter_guid})

    return data


def check_shared_parameters_are_in_document(doc, room, category_names):
    """
    Checks if shared parameter are in the Revit document and bound to the categories required

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param room: The room.
    :type room: Room

    :return: True if shared parameter data is valid, False otherwise.
    :rtype: bool
    """

    return_value = Result()

    try:
        # get shared parameters from revit document
        shared_parameters = get_all_shared_parameters(doc)
        # print("Shared parameters in document:")
        # for p in shared_parameters:
        #     print("{} {}".format(p.GuidValue.ToString(), p.Name))

        # get all shared parameters used by data model
        shared_parameter_guids = [
            room.id.parameter_guid,
            room.area_briefed.parameter_guid,
            room.area_designed.parameter_guid,
            room.room_name_short.parameter_guid,
            room.sub_department.parameter_guid,
            room.department.parameter_guid,
        ]

        print("Looking for shared paras with guids:")
        print(shared_parameter_guids)
        # add other properties
        for prop in room.other_properties:
            shared_parameter_guids.append(prop.parameter_guid)

        # check if shared parameters are in the document
        for shared_parameter_guid in shared_parameter_guids:
            shared_parameter_found = False
            for shared_parameter in shared_parameters:
                if shared_parameter_guid == shared_parameter.GuidValue.ToString():
                    shared_parameter_found = True

                    # check if shared parameter is bound to the correct categories
                    category_binding_names = param_binding_exists_2023(
                        doc,
                        Element.Name.GetValue(shared_parameter),
                        shared_parameter.GetDefinition().GetDataType(),  # forge type id
                    )

                    parameters_are_all_bound = True
                    for category_name in category_names:
                        if category_name not in category_binding_names:
                            return_value.update_sep(
                                False,
                                "Shared parameter with guid: {} is not bound to category: {}.".format(
                                    shared_parameter_guid, category_name
                                ),
                            )
                            parameters_are_all_bound = False
                            
                    if parameters_are_all_bound is True:
                        return_value.append_message(
                            "Shared parameter with guid: {} is bound to all required categories.".format(
                                shared_parameter_guid
                            )
                        )
                    break

            if not shared_parameter_found:
                return_value.update_sep(
                    False,
                    "Shared parameter with guid: {} not found in document.".format(
                        shared_parameter_guid
                    ),
                )
    except Exception as e:
        return_value.update_sep(
            False, "Failed to check shared parameters. Error: {}".format(str(e))
        )
        print("exception in shared parameter checker: {}".format(e))
    return return_value


def set_shared_parameter_value_by_guid(doc, element, guid, value):
    """
    Sets a shared parameter value by guid

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param element: The element.
    :type element: Autodesk.Revit.DB.Element
    :param guid: The guid of the parameter.
    :type guid: str
    :param value: The value to set.
    :type value: object
    """

    return_value = Result()
    try:
        # get shared parameters from revit document
        shared_parameters = get_all_shared_parameters(doc)

        # get the parameter name
        parameter_name = get_parameter_name_by_guid(shared_parameters, guid)

        # set the parameter value
        set_parameter_without_transaction_wrapper_by_name(
            element, parameter_name, value
        )

        return_value.append_message(
            "Set shared parameter: {} value: {} for element with id: {}.".format(
                parameter_name, value, element.Id.Value
            )
        )
    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to set shared parameter value for element with id: {}. Error: {}".format(
                element.Id.Value, str(e)
            ),
        )

    return return_value
