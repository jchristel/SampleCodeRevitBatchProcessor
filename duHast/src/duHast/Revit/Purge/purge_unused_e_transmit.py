"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a purge unused function using Autodesk's own eTransmit plug in.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Based on the building coder article:
https://thebuildingcoder.typepad.com/blog/2022/03/purge-unused-and-the-autodesk-camel.html
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

# import Autodesk.Revit.DB as rdb

from duHast.Utilities.Objects import result as res
from duHast.Utilities.Objects.timer import Timer


def _purge(doc, dll_path):
    """
    Purges the document using the purge unused functionality of the eTransmit tool provided by Autodesk.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param dll_path: Fully qualified file path to the revit version specific eTransmitForRevitDB.dll installed by eTransmit
    :type dll_path: str

    :return: True purge was successful, otherwise False.
    :rtype: bool
    """

    clr.AddReferenceToFileAndPath(dll_path)
    # import the eTransmit name space which includes
    # purge unused functionality
    from eTransmitForRevitDB import eTransmitUpgradeOMatic, UpgradeFailureType

    # purge the document
    e_transmit_upgrade_o_matic_thing = eTransmitUpgradeOMatic(doc.Application)
    result = e_transmit_upgrade_o_matic_thing.purgeUnused(doc)
    return result == UpgradeFailureType.UpgradeSucceeded


# -------------------------------------------- Purge Unused using eTransmit for Revit 2019 -------------------------------------


def _purge_unused_2019(doc):
    """
    Purges the document, revit version 2019, using the purge unused functionality of the eTransmit tool provided by Autodesk

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: True purge was successful, otherwise False.
    :rtype: bool
    """

    # path to e-Transmit dll for Revit 2019
    e_transmit_file_path = (
        r"C:\Program Files\Autodesk\eTransmit for Revit 2019\eTransmitForRevitDB.dll"
    )
    value = _purge(doc, e_transmit_file_path)
    return value


# -------------------------------------------- Purge Unused using eTransmit for Revit 2020 -------------------------------------


def _purge_unused_2020(doc):
    """
    Purges the document, revit version 2020, using the purge unused functionality of the eTransmit tool provided by Autodesk

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: True purge was successful, otherwise False.
    :rtype: bool
    """

    # path to e-Transmit dll for Revit 2019
    e_transmit_file_path = (
        r"C:\Program Files\Autodesk\eTransmit for Revit 2020\eTransmitForRevitDB.dll"
    )
    value = _purge(doc, e_transmit_file_path)
    return value


# -------------------------------------------- Purge Unused using eTransmit for Revit 2021 -------------------------------------


def _purge_unused_2021(doc):
    """
    Purges the document, revit version 2021, using the purge unused functionality of the eTransmit tool provided by Autodesk

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: True purge was successful, otherwise False.
    :rtype: bool
    """

    # path to e-Transmit dll for Revit 2019
    e_transmit_file_path = (
        r"C:\Program Files\Autodesk\eTransmit for Revit 2021\eTransmitForRevitDB.dll"
    )
    value = _purge(doc, e_transmit_file_path)
    return value


# -------------------------------------------- Purge Unused using eTransmit for Revit 2021 -------------------------------------


def _purge_unused_2022(doc):
    """
    Purges the document, revit version 2022, using the purge unused functionality of the eTransmit tool provided by Autodesk

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: True purge was successful, otherwise False.
    :rtype: bool
    """

    # path to e-Transmit dll for Revit 2019
    e_transmit_file_path = (
        r"C:\Program Files\Autodesk\eTransmit for Revit 2022\eTransmitForRevitDB.dll"
    )
    value = _purge(doc, e_transmit_file_path)
    return value


# -------------------------------------------- Purge Unused using eTransmit for Revit 2021 -------------------------------------


def purge_unused_e_transmit(doc):
    """
    Purges the document using the purge unused functionality of the eTransmit tool provided by Autodesk.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return:
        Result class instance.

        - Purge status returned in result.status. False if an exception occurred, purge command returned False, unsupported Revit version, otherwise True.
        - result.message will contain the purge status.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.

    :rtype: :class:`.Result`
    """

    result_value = res.Result()
    t_overall = Timer()
    t_overall.start()
    # get the revit version:
    revit_version = doc.Application.VersionNumber
    try:
        if revit_version == "2019":
            result_value.status = _purge_unused_2019(doc)
        elif revit_version == "2020":
            result_value.status = _purge_unused_2020(doc)
        elif revit_version == "2021":
            result_value.status = _purge_unused_2021(doc)
        elif revit_version == "2022":
            result_value.status = _purge_unused_2022(doc)
        else:
            # this is a non supported revit version!
            raise ValueError(
                "Revit version: {} is currently not supported by purge unused!".format(
                    revit_version
                )
            )
        # update messaging
        if result_value.status == True:
            result_value.message = "Successfully purged model!"
        else:
            result_value.message = "Failed to purge model!"
    except Exception as e:
        result_value.update_sep(
            False, "Terminated purge unused actions with exception: {}".format(e)
        )
    result_value.append_message("purge duration: {}".format(t_overall.stop()))
    return result_value
