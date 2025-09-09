"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions to get the IFC dlls.
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

IFC_EXPORTER_BASE_PATH_ONE = r"C:\ProgramData\Autodesk\ApplicationPlugins\IFC "
IFC_EXPORTER_BASE_PATH_TWO = r".bundle\Contents"

IFC_EXPORTER_UI_OVERRIDE= "IFCExporterUIOverride.dll"
IFC_EXPORTER_EXPORT= "Revit.IFC.Export.dll"
IFC_EXPORTER_FOLDER_PATH_ENUMS = "Revit.IFC.Common.dll"

def get_third_party_path(revit_version):
    """
    Get the path to the third party folder for the IFC exporter.

    :param revit_version: The version of Revit.
    :type revit_version: str
    
    :return: The path to the third party folder for the IFC exporter.
    :rtype: str
    """
    return ("{}{}{}\\{}\\{}".format(
        IFC_EXPORTER_BASE_PATH_ONE
        ,revit_version
        ,IFC_EXPORTER_BASE_PATH_TWO
        ,revit_version
        ,IFC_EXPORTER_UI_OVERRIDE
    ))


def get_enum_path(revit_version):
    """
    Get the path to the enum folder for the IFC exporter.

    :param revit_version: The version of Revit.
    :type revit_version: str
    
    :return: The path to the enum folder for the IFC exporter.
    :rtype: str
    """
    return ("{}{}{}\\{}\\{}".format(
        IFC_EXPORTER_BASE_PATH_ONE
        ,revit_version
        ,IFC_EXPORTER_BASE_PATH_TWO
        ,revit_version
        ,IFC_EXPORTER_EXPORT
    ))


def get_folder_path_enums(revit_version):
    """
    Get the path to the common folder for the IFC exporter.

    :param revit_version: The version of Revit.
    :type revit_version: str
    
    :return: The path to the common folder for the IFC exporter.
    :rtype: str
    """
    return ("{}{}{}\\{}\\{}".format(
        IFC_EXPORTER_BASE_PATH_ONE
        ,revit_version
        ,IFC_EXPORTER_BASE_PATH_TWO
        ,revit_version
        ,IFC_EXPORTER_FOLDER_PATH_ENUMS
    ))