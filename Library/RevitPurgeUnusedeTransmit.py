'''
This module contains a purge unused function using Autodesk's own eTransmit plug in.
based on the building coder article:
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

from Autodesk.Revit.DB import *

import Result as res
from timer import Timer

def _purge(doc, dllPath):
    '''this method uses the purge unused functionality of the eTransmit tool provided by Autodesk
    - returns a bool indicating whether purge was succesfull (true) or failed (false) '''
    clr.AddReferenceToFileAndPath(dllPath)
    # import the eTransmit name space which includes 
    # purge unused functionality
    from eTransmitForRevitDB import eTransmitUpgradeOMatic, UpgradeFailureType
    # purge the document
    eTransmitUpgradeOMaticThing = eTransmitUpgradeOMatic(doc.Application)
    result = eTransmitUpgradeOMaticThing.purgeUnused(doc)
    return (result == UpgradeFailureType.UpgradeSucceeded)

#-------------------------------------------- Purge Unused using eTransmit for Revit 2019 -------------------------------------

# doc           current model document
def _PurgeUnused2019(doc):
    '''this method uses the purge unused functionality of the eTransmit tool provided by Autodesk
    - returns a bool indicating whether purge was succesfull (true) or failed (false) '''
    # path to eTransmitt dll for Revit 2019
    eTransmitFilePath = r'C:\Program Files\Autodesk\eTransmit for Revit 2019\eTransmitForRevitDB.dll'
    value = _purge(doc, eTransmitFilePath)
    return value

#-------------------------------------------- Purge Unused using eTransmit for Revit 2020 -------------------------------------

# doc           current model document
def _PurgeUnused2020(doc):
    '''this method uses the purge unused functionality of the eTransmit tool provided by Autodesk
    - returns a bool indicating whether purge was succesfull (true) or failed (false) '''
    # path to eTransmitt dll for Revit 2019
    eTransmitFilePath = r'C:\Program Files\Autodesk\eTransmit for Revit 2020\eTransmitForRevitDB.dll'
    value = _purge(doc, eTransmitFilePath)
    return value

#-------------------------------------------- Purge Unused using eTransmit for Revit 2021 -------------------------------------

# doc           current model document
def _PurgeUnused2021(doc):
    '''this method uses the purge unused functionality of the eTransmit tool provided by Autodesk
    - returns a bool indicating whether purge was succesfull (true) or failed (false) '''
    # path to eTransmitt dll for Revit 2019
    eTransmitFilePath = r'C:\Program Files\Autodesk\eTransmit for Revit 2021\eTransmitForRevitDB.dll'
    value = _purge(doc, eTransmitFilePath)
    return value

#-------------------------------------------- Purge Unused using eTransmit for Revit 2021 -------------------------------------

# doc           current model document
def _PurgeUnused2022(doc):
    '''this method uses the purge unused functionality of the eTransmit tool provided by Autodesk
    - returns a bool indicating whether purge was succesfull (true) or failed (false) '''
    # path to eTransmitt dll for Revit 2019
    eTransmitFilePath = r'C:\Program Files\Autodesk\eTransmit for Revit 2022\eTransmitForRevitDB.dll'
    value = _purge(doc, eTransmitFilePath)
    return value

#-------------------------------------------- Purge Unused using eTransmit for Revit 2021 -------------------------------------

# doc   current document
def PurgeUnusedETransmit(doc):
    '''calls purge unused methods in eTransmit dll '''
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