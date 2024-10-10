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


def is_link_workset_visible(view, lnk_instance):
    """
    Check if the workset of the link is visible in the view
    :param view: The view to check
    :type view: View
    :param lnk_instance: The Revit link instance to check the workset visibility of
    :type lnk_instance: RevitLinkInstance
    :return: True if the workset of the link is visible in the view, False otherwise
    :rtype: bool
    """
    return view.IsWorksetVisible(lnk_instance.WorksetId)


def is_link_hidden(view, lnk_instance):
    """
    Check if the link is hidden in the view
    :param view: The view to check
    :type view: View
    :param lnk_instance: The Revit link instance to check
    :type lnk_instance: RevitLinkInstance
    :return: True if the link is hidden in the view, False otherwise
    :rtype: bool
    """
    return lnk_instance.IsHidden(view)


def is_link_visible(view_elem, lnk_inst):
    """
    Check if the link is visible in the view. This is determined by:
     - The link is not hidden
     - The link workset is visible

    :param view_elem: The view element to check
    :type view_elem: View
    :param lnk_inst: The Revit link instance to check
    :type lnk_inst: RevitLinkInstance
    :return: True if the link is visible in the view, False otherwise
    :rtype: bool
    """
    link_is_not_hidden = is_link_hidden(view_elem, lnk_inst) == False
    link_workset_is_visible = is_link_workset_visible(view_elem, lnk_inst) == True
    return link_is_not_hidden and link_workset_is_visible
