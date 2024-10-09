"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of functions around exporting from Revit to data objects.
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

from Autodesk.Revit.DB import StorageType
from duHast.Revit.Common.parameter_get_utils import getter_double_as_double_converted_to_metric,getter_int_as_int, getter_string_as_UTF8_string, getter_element_id_as_element_int, getter_none, get_all_parameters_and_values_wit_custom_getters
from duHast.Data.Objects.Properties.data_property import DataProperty
from duHast.Revit.Common.phases import get_phase_id_created, get_phase_id_demolished, get_phase_name_by_id
from duHast.Data.Objects.Properties.data_phasing import DataPhasing
from duHast.Data.Objects.Properties.data_revit_model import DataRevitModel


def get_element_properties(element):
    """
    Convertes properties on a Revit element into data_property instances

    :param element: A Revit element
    :type element: Autodesk.Revit.DB.Element

    :return: A list of data_propert instances
    :rtype: [:class:`.DataProperty`]
    """
    # custom parameter value getters
    value_getter = {
        StorageType.Double: getter_double_as_double_converted_to_metric,
        StorageType.Integer:getter_int_as_int,
        StorageType.String: getter_string_as_UTF8_string,  # encode ass utf 8 just in case
        StorageType.ElementId: getter_element_id_as_element_int,  # needs to be an integer for JSON encoding
        str(None): getter_none,
    }

    # convert properties from Revit into data_property instances
    properties = []
    for revit_prop in get_all_parameters_and_values_wit_custom_getters(element, value_getter).items():
        data_p = DataProperty()
        data_p.name = revit_prop[0]
        data_p.value = revit_prop[1]
        properties.append(data_p)
    
    return properties


def get_phasing_data(doc, element):
    """
    Returns a data phase instance with names for created and demolished populated.

    :param doc: The current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param element: A Revit element
    :type element: Autodesk.Revit.DB.Element

    :return: A data phase instance
    :rtype:  [:class:`.DataPhasing`]
    """

    phase_d = DataPhasing()
    phase_d.created=get_phase_name_by_id(doc=doc, phase_id =get_phase_id_created(element=element))
    phase_d.demolished = get_phase_name_by_id(doc=doc, phase_id =get_phase_id_demolished(element=element))
    
    return phase_d


def get_model_data(doc):
    """
    Returns a revit_model instance with the name populated. If detached and not saved yet it will be named "Detached Model"

    :param doc: The current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A data revit model instance
    :rtype:  [:class:`.DataRevitModel`]
    """

    model_name = "Detached Model"
    # get the model name
    if doc.IsDetached == False:
        model_name = doc.Title
    
    model_d = DataRevitModel()
    model_d.name = model_name
    return model_d