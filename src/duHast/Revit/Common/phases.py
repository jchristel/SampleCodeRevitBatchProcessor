"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Model phase functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

from duHast.Revit.Common.parameter_get_utils import get_built_in_parameter_value, get_parameter_value_as_element_id

from Autodesk.Revit.DB import BuiltInParameter


def get_all_phases(doc):
    """
    Returns a dictionary where key is the id and value is the name of the phase.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A dictionary where key is the id and value is the name of the phase. Dictionary will be empty if no phases exist (family doc?)
    :rtype: dic{key Autodesk.Revit.DB.ElementId: value str}
    """

    return_value = {}
    phases = doc.Phases
    if phases.Size > 0:
        for phase in phases:
            return_value[phase.Id] = phase.Name
    return return_value


def get_all_phases_in_order(doc):
    """
    Returns all phases in the order of oldest to newest.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of tuples ordered oldest to newest. Tuple properties are: 0 is the phase id and 1 is the phase name.
    :rtype: [(ElementId, str)]

    """
    return_value = []
    phases = doc.Phases
    if phases.Size > 0:
        for phase in phases:
            return_value.append((phase.Id, phase.Name))
    return return_value


def get_phase_name_by_id(doc, phase_id):
    """
    Returns the name of a phase by Id

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param phase_id: The phase element id.
    :type phase_id: Autodesk.Revit.DB.ElementId

    :return: Name of the phase, otherwise 'No phase in document' if no phase exists or 'Invalid phase id.' if no phase matching the id was found.
    :rtype: str
    """

    return_value = "No phase in document"
    phases = get_all_phases(doc)
    if len(phases) > 0:
        if phase_id in phases:
            return_value = phases[phase_id]
        else:
            return_value = "Invalid phase id."
    return return_value


def get_name_to_phase_dict(rvt_doc):
    """
    Returns a dictionary where key is the name and value is the phase.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A dictionary where key is the name and value is the phase. Dictionary will be empty if no phases exist (family doc?)
    :rtype: dic{key str: value Autodesk.Revit.DB.Phase}
    """
    phases = rvt_doc.Phases
    phase_dict = {}

    for phase in phases:
        phase_dict[phase.Name] = phase

    return phase_dict


def get_phase_id_created(element):
    """
    Returns the id of the phase an element was created in.

    :param element: A Revit element
    :type element: Autodesk.Revit.DB.Element

    :return: Phase id
    :rtype: Autodesk.Revit.DB.ElementId
    """

    id = get_built_in_parameter_value(
        element,
        BuiltInParameter.PHASE_CREATED,
        get_parameter_value_as_element_id,
    )
    return id


def get_phase_id_demolished(element):
    """
    Returns the id of the phase an element was demolished in.

    :param element: A Revit element
    :type element: Autodesk.Revit.DB.Element

    :return: Phase id
    :rtype: Autodesk.Revit.DB.ElementId
    """
    
    id = get_built_in_parameter_value(
        element,
        BuiltInParameter.PHASE_DEMOLISHED,
        get_parameter_value_as_element_id,
    )
    return id
