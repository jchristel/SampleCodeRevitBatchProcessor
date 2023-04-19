'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit links, CAD links and image links.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

import clr
import System

# import common library modules
from duHast.APISamples.Common import RevitDeleteElements as rDel
from duHast.Utilities import Result as res
from duHast.APISamples.Links.Utility.LinkPath import get_link_path

# import Autodesk
import Autodesk.Revit.DB as rdb


def get_all_revit_link_instances(doc):
    '''
    Gets all Revit link instances in a model.

    Filters by class.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of revit link instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfClass(rdb.RevitLinkInstance)
    return collector

def get_all_revit_link_types(doc):
    '''
    Gets all Revit link types in a model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of revit link types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfClass(rdb.RevitLinkType)
    return collector
    
def get_revit_link_type_from_instance(doc, linkInstance):
    '''
    Gets the Revit link type from a given revit link instance.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param linkInstance: The link instance the type of is to be returned
    :type linkInstance: Autodesk.Revit.DB.RevitLinkInstance

    :return: The matching revit link type.
    :rtype: Autodesk.Revit.DB.RevitLinkType
    '''
    
    revitLinkTypes = get_all_revit_link_types(doc)
    for lt in revitLinkTypes:
        if(lt.Id == linkInstance.GetTypeId()):
            return lt

def delete_revit_links(doc):
    '''
    Deletes all revit links in a file.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: 
        Result class instance.
        
        - .result = True if all revit links got deleted successfully. Otherwise False.
        - .message will contain deletion status. On exception it will also include the exception message.
    
    :rtype: :class:`.Result`
    '''

    ids = []
    returnValue = res.Result()
    for p in rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_RvtLinks):
        ids.append(p.Id)
    # delete all links at once
    returnValue = rDel.delete_by_element_ids(doc, ids, 'Deleting Revit links', 'Revit link(s)')
    return returnValue

def reload_revit_links(doc, linkLocations, hostNameFormatted, doSomethingWithLinkName, worksetConfig):
    '''
    Reloads Revit links from a given file location based on the original link type name (starts with comparison)

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param linkLocations: A list of directories where CAD files can be located.
    :type linkLocations: list str
    :param hostNameFormatted: Not used yet
    :type hostNameFormatted: TBC
    :param doSomethingWithLinkName: A function which amends the link name prior search for a match in folders.\
        I.e. can be used to truncate the link name i.e. the revision details of a link
    :type doSomethingWithLinkName: func(str) -> str
    :param worksetConfig: To use the previously applied workset config use None, otherwise provide custom config.
    :type worksetConfig: Autodesk.Revit.DB.WorksetConfiguration

    :return: 
        Result class instance.
        
        - .result = True if all revit links got reloaded successfully. Otherwise False.
        - .message will contain status of reload and fully qualified file name. On exception it will also include the exception message.
    
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    try:
        # get all revit link types in model
        for p in rdb.FilteredElementCollector(doc).OfClass(rdb.RevitLinkType):
            linkTypeName = doSomethingWithLinkName(rdb.Element.Name.GetValue(p))
            newLinkPath = 'unknown'
            try:
                newLinkPath = get_link_path(linkTypeName, linkLocations, '.rvt')
                if(newLinkPath != None):
                    mp = rdb.ModelPathUtils.ConvertUserVisiblePathToModelPath(newLinkPath)
                    # attempt to reload with worksets set to last viewed
                    # wc = WorksetConfiguration(WorksetConfigurationOption.OpenLastViewed)
                    # however that can be achieved also ... According to Autodesk:
                    # If you want to load the same set of worksets the link previously had, leave this argument as a null reference ( Nothing in Visual Basic) .
                    wc = worksetConfig()
                    result = p.LoadFrom(mp,  wc)
                    # store result in message 
                    returnValue.append_message('{} :: {}'.format(linkTypeName ,result.LoadResult))
                else:
                    returnValue.update_sep(False, '{} :: No link path or multiple path found in provided locations'.format(linkTypeName))
            except Exception as e:
                returnValue.update_sep(False, '{} :: Failed with exception: {}'.format(linkTypeName ,e))
    except Exception as e:
        returnValue.update_sep(False, 'Failed with exception: '.format(e))
    return returnValue

def reload_revit_links_from_list(doc, linkTypesTobReloaded, linkLocations, hostNameFormatted, doSomethingWithLinkName, worksetConfig):
    '''
    Reloads Revit links from a given file location based on the original link type name (starts with comparison)

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param linkTypesTobReloaded: List of link type elements to be reloaded.
    :type linkTypesTobReloaded: list Autodesk.Revit.DB.RevitLinkType
    :param linkLocations: A list of directories where CAD files can be located.
    :type linkLocations: list str
    :param hostNameFormatted: Not used yet
    :type hostNameFormatted: TBC
    :param doSomethingWithLinkName: A function which amends the link name prior search for a match in folders.\
        I.e. can be used to truncate the link name i.e. the revision details of a link
    :type doSomethingWithLinkName: func(str) -> str
    :param worksetConfig: To use the previously applied workset config use None, otherwise provide custom config.
    :type worksetConfig: Autodesk.Revit.DB.WorksetConfiguration

    :return: 
        Result class instance.
        
        - .result = True if all revit links got reloaded successfully. Otherwise False.
        - .message will contain status of reload and fully qualified file name. On exception it will also include the exception message.
    
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    try:
        # loop over links supplied
        for p in linkTypesTobReloaded:
            linkTypeName = doSomethingWithLinkName(rdb.Element.Name.GetValue(p))
            newLinkPath = 'unknown'
            try:
                newLinkPath = get_link_path(linkTypeName, linkLocations, '.rvt')
                if(newLinkPath != None):
                    mp = rdb.ModelPathUtils.ConvertUserVisiblePathToModelPath(newLinkPath)
                    # attempt to reload with worksets set to last viewed
                    # wc = WorksetConfiguration(WorksetConfigurationOption.OpenLastViewed)
                    # however that can be achieved also ... According to Autodesk:
                    # If you want to load the same set of worksets the link previously had, leave this argument as a null reference ( Nothing in Visual Basic) .
                    wc = worksetConfig()
                    result = p.LoadFrom(mp,  wc)
                    # store result in message 
                    returnValue.append_message('{} :: {}'.format(linkTypeName,result.LoadResult))
                else:
                    returnValue.update_sep(False,'{} :: No link path or multiple path found in provided locations'.format(linkTypeName))
            except Exception as e:
                returnValue.update_sep(False, '{} :: Failed with exception: '.format(linkTypeName ,e))
    except Exception as e:
        returnValue.update_sep(False, 'Reload Revit links Failed with exception: '.format(e))
    return returnValue

def default_link_name(name):
    '''
    Default 'do something with link name' method. Returns the link name unchanged.

    Could be replaced with something which i.e. truncates the revision...

    :param name: The link name.
    :type name: str

    :return: the link name unchanged.
    :rtype: str
    '''

    return name

def default_workset_config_for_reload():
    '''
    Default method returning an 'open previous worksets' configuration. (None)

    :return: None: which is use the previous workset configuration.
    :rtype: None
    '''

    return None
