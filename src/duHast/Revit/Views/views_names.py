"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions to check view names. Revit refuses to name a view the same as another view.
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

from Autodesk.Revit.DB import FilteredElementCollector, View


def get_view_names(doc):
    """
    Returns the names of all views in the model (not view templates, not schedules' internal views).

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: The set of view names, lower case.
    :rtype: set of str
    """

    names = set()
    for view in FilteredElementCollector(doc).OfClass(View):
        try:
            if view.IsTemplate:
                continue
            names.add(view.Name.strip().lower())
        except Exception:
            continue
    return names


def is_view_name_in_use(doc, name, view_names=None):
    """
    Checks whether a view with this name exists (case and surrounding white space are ignored).

    This is the check to run before creating views, to refuse work that would collide, rather than
    letting Revit refuse the name half way through.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param name: The name to check.
    :type name: str
    :param view_names: The names from get_view_names, when the caller checks many names, defaults to None (they are read).
    :type view_names: set of str, optional

    :return: True if a view has this name.
    :rtype: bool
    """

    names = view_names if view_names is not None else get_view_names(doc)
    return (name or "").strip().lower() in names


def get_views_in_name_collision(doc, names):
    """
    Returns those of the names which are already the name of a view.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param names: The names to check.
    :type names: list of str

    :return: The names in use, as given.
    :rtype: list of str
    """

    existing = get_view_names(doc)
    return [name for name in names if is_view_name_in_use(doc, name, existing)]
