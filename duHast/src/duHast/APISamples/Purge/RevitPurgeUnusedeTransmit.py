'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a purge unused function using Autodesk's own eTransmit plug in.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Based on the building coder article:
https://thebuildingcoder.typepad.com/blog/2022/03/purge-unused-and-the-autodesk-camel.html
'''

#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2022  Jan Christel
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

import Autodesk.Revit.DB as rdb

from duHast.Utilities import Result as res
from duHast.Utilities.timer import Timer

def _purge(doc, dllPath):
    '''
    Purges the document using the purge unused functionality of the eTransmit tool provided by Autodesk.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param dllPath: Fully qualified file path to the revit version specific eTransmitForRevitDB.dll installed by eTransmit
    :type dllPath: str

    :return: True purge was successful, otherwise False.
    :rtype: bool
    '''
    
    clr.AddReferenceToFileAndPath(dllPath)
    # import the eTransmit name space which includes 
    # purge unused functionality
    from eTransmitForRevitDB import eTransmitUpgradeOMatic, UpgradeFailureType
    # purge the document
    eTransmitUpgradeOMaticThing = eTransmitUpgradeOMatic(doc.Application)
    result = eTransmitUpgradeOMaticThing.purgeUnused(doc)
    return (result == UpgradeFailureType.UpgradeSucceeded)

#-------------------------------------------- Purge Unused using eTransmit for Revit 2019 -------------------------------------

def _PurgeUnused2019(doc):
    '''
    Purges the document, revit version 2019, using the purge unused functionality of the eTransmit tool provided by Autodesk
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: True purge was successful, otherwise False.
    :rtype: bool
    '''

    # path to e-Transmit dll for Revit 2019
    eTransmitFilePath = r'C:\Program Files\Autodesk\eTransmit for Revit 2019\eTransmitForRevitDB.dll'
    value = _purge(doc, eTransmitFilePath)
    return value

#-------------------------------------------- Purge Unused using eTransmit for Revit 2020 -------------------------------------

def _PurgeUnused2020(doc):
    '''
    Purges the document, revit version 2020, using the purge unused functionality of the eTransmit tool provided by Autodesk
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: True purge was successful, otherwise False.
    :rtype: bool
    '''

    # path to e-Transmit dll for Revit 2019
    eTransmitFilePath = r'C:\Program Files\Autodesk\eTransmit for Revit 2020\eTransmitForRevitDB.dll'
    value = _purge(doc, eTransmitFilePath)
    return value

#-------------------------------------------- Purge Unused using eTransmit for Revit 2021 -------------------------------------

def _PurgeUnused2021(doc):
    '''
    Purges the document, revit version 2021, using the purge unused functionality of the eTransmit tool provided by Autodesk
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: True purge was successful, otherwise False.
    :rtype: bool
    '''

    # path to e-Transmit dll for Revit 2019
    eTransmitFilePath = r'C:\Program Files\Autodesk\eTransmit for Revit 2021\eTransmitForRevitDB.dll'
    value = _purge(doc, eTransmitFilePath)
    return value

#-------------------------------------------- Purge Unused using eTransmit for Revit 2021 -------------------------------------

def _PurgeUnused2022(doc):
    '''
    Purges the document, revit version 2022, using the purge unused functionality of the eTransmit tool provided by Autodesk
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: True purge was successful, otherwise False.
    :rtype: bool
    '''

    # path to e-Transmit dll for Revit 2019
    eTransmitFilePath = r'C:\Program Files\Autodesk\eTransmit for Revit 2022\eTransmitForRevitDB.dll'
    value = _purge(doc, eTransmitFilePath)
    return value

#-------------------------------------------- Purge Unused using eTransmit for Revit 2021 -------------------------------------

def PurgeUnusedETransmit(doc):
    '''
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
    '''

    resultValue = res.Result()
    tOverall = Timer()
    tOverall.start()
    # get the revit version:
    revitVersion = doc.Application.VersionNumber
    try:
        if (revitVersion == '2019'):
            resultValue.status = _PurgeUnused2019(doc)
        elif (revitVersion == '2020'):
            resultValue.status = _PurgeUnused2020(doc)
        elif (revitVersion == '2021'):
            resultValue.status = _PurgeUnused2021(doc)
        elif (revitVersion == '2022'):
            resultValue.status = _PurgeUnused2022(doc)
        else:
            # this is a non supported revit version!
            raise ValueError('Revit version ' + revitVersion + ' is currently not supported by purge unused!')
        # update messaging
        if( resultValue.status == True):
            resultValue.message = 'Successfully purged model!'
        else:
            resultValue.message = 'Failed to purge model!'
    except Exception as e:
            resultValue.UpdateSep(False,'Terminated purge unused actions with exception: '+ str(e))
    resultValue.AppendMessage('purge duration: '+ str(tOverall.stop()))
    return resultValue
