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

from duHast.Revit.Common.element_id import get_el_id_int
from duHast.Revit.Common.parameter_get_utils import get_built_in_parameter_value, get_parameter_value_as_element_id

from Autodesk.Revit.DB import BuiltInParameter, FilteredElementCollector


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


def get_phase_by_name(doc, phase_name):
    """
    Returns the phase with the given name.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param phase_name: The name of the phase.
    :type phase_name: str

    :return: The phase, None if the document has no phase of that name.
    :rtype: Autodesk.Revit.DB.Phase or None
    """

    for phase in doc.Phases:
        if phase.Name == phase_name:
            return phase
    return None


def is_in_phase_range(created_index, demolished_index, selected_index):
    """
    Revit's phase membership rule on phase sequence indices (position in doc.Phases):
    created <= selected AND (not demolished OR demolished > selected).

    Not 'created == selected': equality would drop every element built in an earlier phase and still standing.

    :param created_index: Sequence index of the phase the element was created in; None if it resolves to no known phase.
    :type created_index: int or None
    :param demolished_index: Sequence index of the phase the element was demolished in; None if never demolished.
    :type demolished_index: int or None
    :param selected_index: Sequence index of the phase of interest.
    :type selected_index: int

    :return: True if the element exists in the selected phase. An element created in no known phase is not in any.
    :rtype: bool
    """

    if created_index is None or created_index > selected_index:
        return False
    return demolished_index is None or demolished_index > selected_index


def get_ids_of_elements_in_phase(doc, phase_name, built_in_category):
    """
    Returns the ids of the elements of a category that exist in a phase (created in or before it and not demolished
    by it). Elements are the instances only, not types.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param phase_name: The name of the phase.
    :type phase_name: str
    :param built_in_category: The category of interest.
    :type built_in_category: Autodesk.Revit.DB.BuiltInCategory

    :raises ValueError: when the document has no phase of that name (a model that cannot be scoped must not pass everything).

    :return: The element ids as integers.
    :rtype: set of int
    """

    order_by_id = {}
    order_by_name = {}
    for index, phase in enumerate(doc.Phases):
        order_by_id[get_el_id_int(phase.Id)] = index
        order_by_name[phase.Name] = index
    if phase_name not in order_by_name:
        raise ValueError(
            "model has no phase named '{}' (it has: {})".format(
                phase_name, ", ".join(sorted(order_by_name))
            )
        )
    selected = order_by_name[phase_name]

    ids = set()
    collector = (
        FilteredElementCollector(doc)
        .OfCategory(built_in_category)
        .WhereElementIsNotElementType()
    )
    for element in collector:
        created = order_by_id.get(get_el_id_int(element.CreatedPhaseId))
        demolished = order_by_id.get(get_el_id_int(element.DemolishedPhaseId))
        if is_in_phase_range(created, demolished, selected):
            ids.add(get_el_id_int(element.Id))
    return ids
