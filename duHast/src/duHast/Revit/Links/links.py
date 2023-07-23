"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit links, CAD links and image links.
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

import clr
import System

# import common library modules
from duHast.Revit.Common import delete as rDel
from duHast.Utilities.Objects import result as res
from duHast.Revit.Links.Utility.link_path import get_link_path

# import Autodesk
import Autodesk.Revit.DB as rdb


def get_all_revit_link_instances(doc):
    """
    Gets all Revit link instances in a model.

    Filters by class.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of revit link instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = rdb.FilteredElementCollector(doc).OfClass(rdb.RevitLinkInstance)
    return collector


def get_all_revit_link_types(doc):
    """
    Gets all Revit link types in a model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of revit link types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = rdb.FilteredElementCollector(doc).OfClass(rdb.RevitLinkType)
    return collector


def get_revit_link_type_from_instance(doc, link_instance):
    """
    Gets the Revit link type from a given revit link instance.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param link_instance: The link instance the type of is to be returned
    :type link_instance: Autodesk.Revit.DB.RevitLinkInstance

    :return: The matching revit link type.
    :rtype: Autodesk.Revit.DB.RevitLinkType
    """

    revit_link_types = get_all_revit_link_types(doc)
    for lt in revit_link_types:
        if lt.Id == link_instance.GetTypeId():
            return lt


def delete_revit_links(doc):
    """
    Deletes all revit links in a file.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return:
        Result class instance.

        - .result = True if all revit links got deleted successfully. Otherwise False.
        - .message will contain deletion status. On exception it will also include the exception message.

    :rtype: :class:`.Result`
    """

    ids = []
    return_value = res.Result()
    for p in rdb.FilteredElementCollector(doc).OfCategory(
        rdb.BuiltInCategory.OST_RvtLinks
    ):
        ids.append(p.Id)
    # delete all links at once
    return_value = rDel.delete_by_element_ids(
        doc, ids, "Deleting Revit links", "Revit link(s)"
    )
    return return_value


def reload_revit_links(
    doc,
    link_locations,
    host_name_formatted,
    do_something_with_link_name,
    workset_config,
):
    """
    Reloads Revit links from a given file location based on the original link type name (starts with comparison)

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param link_locations: A list of directories where CAD files can be located.
    :type link_locations: list str
    :param host_name_formatted: Not used yet
    :type host_name_formatted: TBC
    :param do_something_with_link_name: A function which amends the link name prior search for a match in folders.\
        I.e. can be used to truncate the link name i.e. the revision details of a link
    :type do_something_with_link_name: func(str) -> str
    :param workset_config: To use the previously applied workset config use None, otherwise provide custom config.
    :type workset_config: Autodesk.Revit.DB.WorksetConfiguration

    :return: 
        Result class instance.
        
        - .result = True if all revit links got reloaded successfully. Otherwise False.
        - .message will contain status of reload and fully qualified file name. On exception it will also include the exception message.
    
    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    try:
        # get all revit link types in model
        for p in rdb.FilteredElementCollector(doc).OfClass(rdb.RevitLinkType):
            link_type_name = do_something_with_link_name(rdb.Element.Name.GetValue(p))
            new_link_path = "unknown"
            try:
                new_link_path = get_link_path(link_type_name, link_locations, ".rvt")
                if new_link_path != None:
                    mp = rdb.ModelPathUtils.ConvertUserVisiblePathToModelPath(
                        new_link_path
                    )
                    # attempt to reload with worksets set to last viewed
                    # wc = WorksetConfiguration(WorksetConfigurationOption.OpenLastViewed)
                    # however that can be achieved also ... According to Autodesk:
                    # If you want to load the same set of worksets the link previously had, leave this argument as a null reference ( Nothing in Visual Basic) .
                    wc = workset_config()
                    result = p.LoadFrom(mp, wc)
                    # store result in message
                    return_value.append_message(
                        "{} :: {}".format(link_type_name, result.LoadResult)
                    )
                else:
                    return_value.update_sep(
                        False,
                        "{} :: No link path or multiple path found in provided locations".format(
                            link_type_name
                        ),
                    )
            except Exception as e:
                return_value.update_sep(
                    False, "{} :: Failed with exception: {}".format(link_type_name, e)
                )
    except Exception as e:
        return_value.update_sep(False, "Failed with exception: ".format(e))
    return return_value


def reload_revit_links_from_list(
    doc,
    link_types_tob_reloaded,
    link_locations,
    host_name_formatted,
    do_something_with_link_name,
    workset_config,
):
    """
    Reloads Revit links from a given file location based on the original link type name (starts with comparison)

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param link_types_tob_reloaded: List of link type elements to be reloaded.
    :type link_types_tob_reloaded: list Autodesk.Revit.DB.RevitLinkType
    :param link_locations: A list of directories where CAD files can be located.
    :type link_locations: list str
    :param host_name_formatted: Not used yet
    :type host_name_formatted: TBC
    :param do_something_with_link_name: A function which amends the link name prior search for a match in folders.\
        I.e. can be used to truncate the link name i.e. the revision details of a link
    :type do_something_with_link_name: func(str) -> str
    :param workset_config: To use the previously applied workset config use None, otherwise provide custom config.
    :type workset_config: Autodesk.Revit.DB.WorksetConfiguration

    :return: 
        Result class instance.
        
        - .result = True if all revit links got reloaded successfully. Otherwise False.
        - .message will contain status of reload and fully qualified file name. On exception it will also include the exception message.
    
    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    try:
        # loop over links supplied
        for p in link_types_tob_reloaded:
            link_type_name = do_something_with_link_name(rdb.Element.Name.GetValue(p))
            new_link_path = "unknown"
            try:
                new_link_path = get_link_path(link_type_name, link_locations, ".rvt")
                if new_link_path != None:
                    mp = rdb.ModelPathUtils.ConvertUserVisiblePathToModelPath(
                        new_link_path
                    )
                    # attempt to reload with worksets set to last viewed
                    # wc = WorksetConfiguration(WorksetConfigurationOption.OpenLastViewed)
                    # however that can be achieved also ... According to Autodesk:
                    # If you want to load the same set of worksets the link previously had, leave this argument as a null reference ( Nothing in Visual Basic) .
                    wc = workset_config()
                    result = p.LoadFrom(mp, wc)
                    # store result in message
                    return_value.append_message(
                        "{} :: {}".format(link_type_name, result.LoadResult)
                    )
                else:
                    return_value.update_sep(
                        False,
                        "{} :: No link path or multiple path found in provided locations".format(
                            link_type_name
                        ),
                    )
            except Exception as e:
                return_value.update_sep(
                    False, "{} :: Failed with exception: ".format(link_type_name, e)
                )
    except Exception as e:
        return_value.update_sep(
            False, "Reload Revit links Failed with exception: ".format(e)
        )
    return return_value


def default_link_name(name):
    """
    Default 'do something with link name' method. Returns the link name unchanged.

    Could be replaced with something which i.e. truncates the revision...

    :param name: The link name.
    :type name: str

    :return: the link name unchanged.
    :rtype: str
    """

    return name


def default_workset_config_for_reload():
    """
    Default method returning an 'open previous worksets' configuration. (None)

    :return: None: which is use the previous workset configuration.
    :rtype: None
    """

    return None
