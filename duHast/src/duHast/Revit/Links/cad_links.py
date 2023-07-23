"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to CAD links.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright © 2023, Jan Christel
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

import Autodesk.Revit.DB as rdb

from duHast.Revit.Common import delete as rDel, transaction as rTran
from duHast.Utilities.Objects import result as res
from duHast.Revit.Links.Utility.link_path import get_link_path


def get_all_cad_link_types(doc):
    """
    Gets all CAD link types in a model.
    Filters by class.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of CAD link types
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = rdb.FilteredElementCollector(doc).OfClass(rdb.CADLinkType)
    return collector


def get_all_cad_link_instances(doc):
    """
    Gets all CAD link instances in a model.
    Filters by class.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of import instances
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = rdb.FilteredElementCollector(doc).OfClass(rdb.ImportInstance)
    return collector


def get_cad_type_imports_only(doc):
    """
    Gets all CAD imports in a model.
    Filters by class and check whether the element is an external file reference (True its a link, False it is an import)
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of all CAD imports in a model.
    :rtype: list Autodesk.Revit.DB.CADLinkType
    """

    cad_imports = []
    collector = rdb.FilteredElementCollector(doc).OfClass(rdb.CADLinkType)
    for cad in collector:
        if cad.IsExternalFileReference() == False:
            cad_imports.append(cad)
    return cad_imports


def sort_cad_link_types_by_model_or_view_specific(doc):
    """
    Returns two lists: First one: cad links types linked by view (2D) , second one cad link types linked into model (3D).
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: Two lists of cad link types.
    :rtype: list Autodesk.Revit.DB.CADLinkType, list Autodesk.Revit.DB.CADLinkType
    """

    cad_links_by_view = []
    cad_links_by_model = []
    collector_cad_types = get_all_cad_link_types(doc)
    collector_cad_instances = get_all_cad_link_instances(doc)
    ids_by_view = []
    # work out through the instance which cad link type is by view
    for c_instance in collector_cad_instances:
        if c_instance.ViewSpecific:
            ids_by_view.append(c_instance.GetTypeId())
    # filter all cad link types by id's identified
    for c_type in collector_cad_types:
        if c_type.Id in ids_by_view and c_type.IsExternalFileReference():
            cad_links_by_view.append(c_type)
        elif c_type.IsExternalFileReference():
            cad_links_by_model.append(c_type)
    return cad_links_by_view, cad_links_by_model


def get_all_cad_link_type_by_view_only(doc):
    """
    Gets all CAD links by view in a model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: Lists of cad link types.
    :rtype: list Autodesk.Revit.DB.CADLinkType
    """

    (
        cad_links_by_view,
        cad_links_by_model,
    ) = sort_cad_link_types_by_model_or_view_specific(doc)
    return cad_links_by_view


def get_all_cad_link_type_in_model_only(doc):
    """
    Gets all CAD links by model in a model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: Lists of cad link types.
    :rtype: list Autodesk.Revit.DB.CADLinkType
    """

    (
        cad_links_by_view,
        cad_links_by_model,
    ) = sort_cad_link_types_by_model_or_view_specific(doc)
    return cad_links_by_model


def delete_cad_links(doc):
    """
    Deletes all CAD links in a model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return:
        Result class instance.
        - .result = True if all CAD links got deleted. Otherwise False.
        - .message will contain status of deletion.
    :rtype: :class:`.Result`
    """

    ids = []
    return_value = res.Result()
    for p in rdb.FilteredElementCollector(doc).OfClass(rdb.ImportInstance):
        ids.append(p.Id)
    # delete all links at once
    return_value = rDel.delete_by_element_ids(
        doc, ids, "Deleting CAD links", "CAD link(s)"
    )
    return return_value


def reload_cad_links(
    doc, link_locations, host_name_formatted, do_something_with_link_name
):
    """
    Reloads CAD links from a given file location based on the original link type name (starts with comparison)
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param link_locations: A list of directories where CAD files can be located.
    :type link_locations: list str
    :param host_name_formatted: Not used yet
    :type host_name_formatted: TBC
    :param do_something_with_link_name: A function which amends the link name prior search for a match in folders.\
        I.e. can be used to truncate the link name i.e. the revision details of a link
    :type do_something_with_link_name: func(str) -> str
    :return: 
        Result class instance.
        - .result = True if all CAD links got reloaded successfully. Otherwise False.
        - .message will contain status of reload and fully qualified file name. On exception it will also include the exception message.
    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    try:
        # get all CAD link types in model
        for p in rdb.FilteredElementCollector(doc).OfClass(rdb.CADLinkType):
            link_type_name = do_something_with_link_name(rdb.Element.Name.GetValue(p))
            new_link_path = "unknown"
            try:
                new_link_path = get_link_path(link_type_name, link_locations, ".dwg")
                if new_link_path != None:
                    # reloading CAD links requires a transaction
                    def action():
                        action_return_value = res.Result()
                        try:
                            result = p.LoadFrom(new_link_path)
                            action_return_value.message = (
                                link_type_name + " :: " + str(result.LoadResult)
                            )
                        except Exception as e:
                            action_return_value.update_sep(
                                False,
                                link_type_name
                                + " :: "
                                + "Failed with exception: "
                                + str(e),
                            )
                        return action_return_value

                    transaction = rdb.Transaction(doc, "Reloading: " + link_type_name)
                    reload_result = rTran.in_transaction(transaction, action)
                    return_value.update(reload_result)
                else:
                    return_value.update_sep(
                        False,
                        link_type_name
                        + " :: "
                        + "No link path or multiple path found in provided locations",
                    )
            except Exception as e:
                return_value.update_sep(
                    False, link_type_name + " :: " + "Failed with exception: " + str(e)
                )
    except Exception as e:
        return_value.update_sep(False, "Failed with exception: " + str(e))
    return return_value
