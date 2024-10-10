"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit area separation lines reports functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2024, Jan Christel
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

from duHast.Revit.Areas.areas import get_area_schemes
from duHast.Revit.Areas.area_lines import get_area_lines_by_scheme_and_level_name
from duHast.Revit.Levels.levels import get_levels_list_ascending
from duHast.Revit.Warnings.warning_guids import AREA_LINE_OFF_AXIS, AREA_SEPARATION_LINES_OVERLAP
from duHast.Revit.Warnings.warnings import get_unique_warnings_elements_by_guid

from Autodesk.Revit.DB import Element


def area_lines_by_schemes_and_by_levels (doc):
    """
    Reports all area separation line by area schemes and level they belong too. 

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: dictionary where key is the area scheme name and value is a list of are line ids, or empty list if no area lines are associated with the scheme
    :rtype: {str: Autodesk.Revit.DB.ElementId]}
    """


    line_by_area_scheme_and_level = {}

    all_area_schemes = get_area_schemes(doc=doc)
    levels_ascending = get_levels_list_ascending(doc=doc)

    # loop over all area schemes in the model
    for area_scheme in all_area_schemes:
        
        # get the scheme name
        area_scheme_name = Element.Name.GetValue(area_scheme)
        
        # set up a dictionary containing level name as key and list of area lines as values
        by_level_name = {}

        # loop over levels
        for level in levels_ascending:
            # get the level name
            level_name = Element.Name.GetValue(level)

            # get lines by level
            area_lines_by_scheme_and_level = get_area_lines_by_scheme_and_level_name(doc=doc, scheme_name=area_scheme_name, level_name=level_name)

            # check for None
            if area_lines_by_scheme_and_level == None:
                by_level_name[level_name] = []
            else:
                by_level_name[level_name]=area_lines_by_scheme_and_level
        
        # store room separation lines by level in by scheme dictionary
        line_by_area_scheme_and_level[area_scheme_name] = by_level_name
    
    return line_by_area_scheme_and_level


def area_lines_with_warnings_by_schemes_and_by_levels(doc):
    """
    Reports all area separation line with warnings by area schemes and level they belong too. 

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: dictionary where key is the area scheme name and value is a list of are line ids, or empty list if no area lines are associated with the scheme
    :rtype: {str: Autodesk.Revit.DB.ElementId]}
    """

    # get area lines by scheme name and level name
    line_by_area_scheme_and_level = area_lines_by_schemes_and_by_levels (doc= doc)

    # check for empty and return if so
    if(len(line_by_area_scheme_and_level)==0):
        return line_by_area_scheme_and_level

    # get all area lines with warnings attached to them
    area_line_ids_of_axis = get_unique_warnings_elements_by_guid(doc=doc, guid= AREA_LINE_OFF_AXIS)

    # get all area lines overlapping
    area_lines_ids_overlapping = get_unique_warnings_elements_by_guid(doc=doc, guid= AREA_SEPARATION_LINES_OVERLAP)

    # combine lines with warnings lists
    area_lines_with_warnings = area_line_ids_of_axis + area_lines_ids_overlapping

    # check for empty and return if so
    if len(area_lines_with_warnings)==0:
        return {}
    
    # loop over dictionary and find lines with warnings
    for scheme_name in line_by_area_scheme_and_level:

        for level_name, separation_lines in line_by_area_scheme_and_level[scheme_name].items():
            lines_with_warnings = []
            for sep_line in separation_lines:
                if sep_line.Id in area_lines_with_warnings:
                    lines_with_warnings.append(sep_line)
            # replace previous line id list with line ids with warnigns associated
            line_by_area_scheme_and_level[scheme_name][level_name]=lines_with_warnings
    

    return line_by_area_scheme_and_level