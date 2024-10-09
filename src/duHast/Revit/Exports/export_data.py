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

from Autodesk.Revit.DB import Element, StorageType

from duHast.Revit.Common.parameter_get_utils import (
    getter_double_as_double_converted_to_metric,
    getter_int_as_int,
    getter_string_as_UTF8_string,
    getter_element_id_as_element_int,
    getter_none,
    get_all_parameters_and_values_wit_custom_getters,
    get_built_in_parameter_value,
)
from duHast.Revit.Common.design_set_options import get_design_set_option_info
from duHast.Utilities.utility import encode_utf8
from duHast.Data.Objects.Properties.data_property import DataProperty
from duHast.Revit.Common.phases import (
    get_phase_id_created,
    get_phase_id_demolished,
    get_phase_name_by_id,
)
from duHast.Revit.Common.Objects.design_set_property_names import DesignSetPropertyNames
from duHast.Data.Objects.Properties.data_phasing import DataPhasing
from duHast.Data.Objects.Properties.data_revit_model import DataRevitModel
from duHast.Data.Objects.Properties.data_level import DataLevel
from duHast.Data.Objects.Properties.data_type_properties import DataTypeProperties
from duHast.Data.Objects.Properties.data_instance_properties import (
    DataInstanceProperties,
)
from duHast.Data.Objects.Properties.data_design_set_option import DataDesignSetOption


def get_element_properties(element):
    """
    Converts properties on a Revit element into data_property instances

    :param element: A Revit element
    :type element: Autodesk.Revit.DB.Element

    :return: A list of data_property instances
    :rtype: [:class:`.DataProperty`]
    """
    # custom parameter value getters
    value_getter = {
        StorageType.Double: getter_double_as_double_converted_to_metric,
        StorageType.Integer: getter_int_as_int,
        StorageType.String: getter_string_as_UTF8_string,  # encode ass utf 8 just in case
        StorageType.ElementId: getter_element_id_as_element_int,  # needs to be an integer for JSON encoding
        str(None): getter_none,
    }

    # convert properties from Revit into data_property instances
    properties = []
    for revit_prop in get_all_parameters_and_values_wit_custom_getters(
        element, value_getter
    ).items():
        data_p = DataProperty()
        data_p.name = revit_prop[0]
        data_p.value = revit_prop[1]
        properties.append(data_p)

    return properties


def get_type_properties(doc, element):
    """
    Returns a populated data type property instance.

    :param doc: The current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param element: A Revit element
    :type element: Autodesk.Revit.DB.Element

    :return: A data type properties instance
    :rtype: [:class:`.DataTypeProperties`]
    """
    type_p = DataTypeProperties()

    # get element properties
    type_p.id = element.GetTypeId().IntegerValue
    type_p.name = encode_utf8(Element.Name.GetValue(element))
    element_type = doc.GetElement(element.GetTypeId())

    # get the elements type properties
    type_properties = get_element_properties(element=element_type)
    type_p.properties = type_properties

    return type_p


def get_instance_properties(element):
    """
    Returns a populated data instance property instance.

    :param element: A Revit element
    :type element: Autodesk.Revit.DB.Element

    :return: A data instance properties instance
    :rtype: [:class:`.DataInstanceProperties`]
    """
    instance_p = DataInstanceProperties()

    # get instance properties
    instance_p.id = element.Id.IntegerValue
    instance_properties = get_element_properties(element=element)
    instance_p.properties = instance_properties

    return instance_p


def get_level_data(doc, element, built_in_parameter_def):
    """
    Returns a populated data level instance.

    :param doc: The current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param element: A Revit element
    :type element: Autodesk.Revit.DB.Element
    :param built_in_parameter_def: The build in parameter containing the offset from level
    :type built_in_parameter_def: Autodesk.Revit.DB.BuiltInParameter

    :return: A data level instance
    :rtype: [:class:`.DataLevel`]
    """

    level_d = DataLevel()

    # get level properties
    level_d.name = encode_utf8(Element.Name.GetValue(doc.GetElement(element.LevelId)))
    level_d.id = element.LevelId.IntegerValue
    level_d.offset_from_level = get_built_in_parameter_value(
        element=element, built_in_parameter_def=built_in_parameter_def
    )  # offset from level

    return level_d


def get_design_set_data(doc, element):
    """
    Returns a populated data design set option instance.

    :param doc: The current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param element: A Revit element
    :type element: Autodesk.Revit.DB.Element

    :return: A data design set instance
    :rtype: [:class:`.DataDesignSetOption`]
    """

    design_set_d = DataDesignSetOption()

    # get design set data
    design_set_data = get_design_set_option_info(doc, element)
    design_set_d.option_name = design_set_data[
        DesignSetPropertyNames.DESIGN_OPTION_NAME
    ]
    design_set_d.set_name = design_set_data[DesignSetPropertyNames.DESIGN_SET_NAME]
    design_set_d.is_primary = design_set_data[
        DesignSetPropertyNames.DESIGN_OPTION_IS_PRIMARY
    ]

    return design_set_d


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
    phase_d.created = get_phase_name_by_id(
        doc=doc, phase_id=get_phase_id_created(element=element)
    )
    phase_d.demolished = get_phase_name_by_id(
        doc=doc, phase_id=get_phase_id_demolished(element=element)
    )

    return phase_d


def get_model_data(doc):
    """
    Returns a revit_model instance with the name populated. If detached and not saved yet it will be named "Detached Model"

    :param doc: The current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A data revit model instance
    :rtype:  [:class:`.DataRevitModel`]
    """

    model_d = DataRevitModel()
    # set a default value in case the model is detached
    model_name = "Detached Model"
    # get the model name
    if doc.IsDetached == False:
        model_name = doc.Title
    model_d.name = model_name
    return model_d
