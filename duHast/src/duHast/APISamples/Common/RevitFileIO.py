'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit file operations utility functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2021  Jan Christel
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


import Autodesk.Revit.DB as rdb

from duHast.Utilities import Result as res, FilesIO as util


def sync_file (
    doc,
    compactCentralFile = False # type: bool
    ):
    # type: (...) -> res.Result
    '''
    Synchronizes a Revit central file.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param compactCentralFile: option to compact the central file, defaults to False
    :type compactCentralFile: bool, optional
    :return: 
        Result class instance.
        - .result = True if successfully synced file. Otherwise False.
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    # set up sync settings
    ro = rdb.RelinquishOptions(True)
    transActOptions = rdb.TransactWithCentralOptions()
    sync = rdb.SynchronizeWithCentralOptions()
    sync.Comment = 'Synchronized by Revit Batch Processor'
    sync.Compact = compactCentralFile
    sync.SetRelinquishOptions(ro)
    # Synch it
    try:
        # save local first ( this seems to prevent intermittent crash on sync(?))
        doc.Save()
        doc.SynchronizeWithCentral(transActOptions, sync)
        # relinquish all
        rdb.WorksharingUtils.RelinquishOwnership(doc, ro, transActOptions)
        returnValue.message = 'Successfully synched file.'
    except Exception as e:
        returnValue.update_sep(False, 'Failed with exception: {}'.format(e))
    return returnValue


def saves_as_workshared_file(
    doc,
    fullFileName  # type: str
    ):
    # type: (...) -> res.Result
    '''
    Saves a Revit project file as a workshared file.
    Save as options are:
    Workset configuration is : Ask users on open to specify.
    Any existing file will be overwritten.
    Number of backups is 5
    File will bew compacted on save.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param fullFileName: The fully qualified file path of where to save the file.
    :type fullFileName: string
    :return: 
        Result class instance.
        - .result = True if successfully saved file, otherwise False.
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    try:
        workSharingSaveAsOption = rdb.WorksharingSaveAsOptions()
        workSharingSaveAsOption.OpenWorksetsDefault = rdb.SimpleWorksetConfiguration.AskUserToSpecify
        workSharingSaveAsOption.SaveAsCentral = True
        saveOption = rdb.SaveAsOptions()
        saveOption.OverwriteExistingFile = True
        saveOption.SetWorksharingOptions(workSharingSaveAsOption)
        saveOption.MaximumBackups = 5
        saveOption.Compact = True
        doc.SaveAs(fullFileName, saveOption)
        returnValue.message = 'Successfully saved file: ' + str(fullFileName)
    except Exception as e:
        returnValue.update_sep(False, 'Failed with exception: {}'.format(e))
    return returnValue


def save_as_family(
    doc,
    targetFolderPath, 
    currentFullFileName, 
    nameData, 
    fileExtension = '.rfa',
    compactFile = False 
    ):
   
    '''
    Saves a family file under new name in given location.

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param targetFolderPath: The directory path of where to save the file.
    :type targetFolderPath: str
    :param currentFullFileName: The current (old) name of the file.
    :type currentFullFileName: str
    :param nameData:  Old name and new name are Revit file names without file extension. Used to rename the family on save from old name to new name.
    :type nameData: List of string arrays in format[[oldname, newName]]
    :param fileExtension: The file extension used for the new file, defaults to '.rfa'
    :type fileExtension: str, optional
    :param compactFile: Flag whether family is to be compacted on save, defaults to False
    :type compactFile: bool, optional
    :return: 
        Result class instance.
            - .result = True if successfully saved file, otherwise False.
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    revitFileName = util.get_file_name_without_ext(currentFullFileName)
    newFileName= ''
    match = False
    # find new file name in list past in
    for oldName, newName in nameData:
        if (revitFileName.startswith(oldName)):
            match = True
            returnValue.message = ('Found file name match for: {} new name: {}'.format(revitFileName ,newName))
            # save file under new name
            newFileName = targetFolderPath + '\\'+ newName + fileExtension
            break
    if(match == False):
        # save under same file name
        newFileName = targetFolderPath + '\\'+ revitFileName + fileExtension
        returnValue.message = 'Found no file name match for: {}'.format(currentFullFileName)
    try:
        # setup save as option
        so = rdb.SaveAsOptions()
        so.OverwriteExistingFile = True
        so.MaximumBackups = 5
        so.SetWorksharingOptions(None)
        so.Compact = compactFile
        doc.SaveAs(newFileName, so)
        returnValue.update_sep(True, 'Saved file: {}'.format(newFileName))
    except Exception as e:
        returnValue.update_sep(False, 'Failed to save revit file to new location with exception: {}'.format(e))
    return returnValue


def save_as(
    doc,
    targetFolderPath, 
    currentFullFileName, 
    nameData, 
    fileExtension = '.rvt' 
    ):
    
    '''
    Saves a project file under new name in given location.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param targetFolderPath: The directory path of where to save the file.
    :type targetFolderPath: str
    :param currentFullFileName: The current (old) name of the file.
    :type currentFullFileName: str
    :param nameData: Old name and new name are revit file names without file extension. Used to rename the model on save from old name to new name.
    :type nameData: List of string arrays in format[[oldname, newName]]
    :param fileExtension: The file extension used for the new file, defaults to '.rvt'
    :type fileExtension: str, optional
    :return: 
        Result class instance.
        - .result = True if successfully saved file, otherwise False.
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    # added str() around this expression to satisfy sphinx auto code documentation
    # it will throw an exception when concatenating the string in the return statement
    revitFileName = str(util.get_file_name_without_ext(currentFullFileName))
    newFileName= ''
    match = False
    for oldName, newName in nameData:
        if (revitFileName.startswith(oldName)):
            match = True
            returnValue.message = ('Found file name match for: {} new name: {}'.format(revitFileName, newName))
            # save file under new name
            newFileName = targetFolderPath + '\\'+ newName + fileExtension
            break
    if(match == False):
        # save under same file name
        newFileName = targetFolderPath + '\\'+ revitFileName + fileExtension
        # added str.format around this expression to satisfy sphinx auto code documentation
        returnValue.message = 'Found no file name match for: {}'.format(currentFullFileName)
    try:
        returnValue.status = saves_as_workshared_file(doc, newFileName).status
        returnValue.append_message('Saved file: {}'.format(newFileName))
    except Exception as e:
        returnValue.update_sep(False, 'Failed to save revit file to new location; {} with exception: '.format(newFileName, e))
    return returnValue


def save_file(
    doc,
    compactFile = False # type: bool
    ):
    # type: (...) -> res.Result
    '''
    Saves a non workshared Revit file. To be used for families and non workshared revit files only.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param compactFile: True file will be compacted on save, defaults to False
    :type compactFile: bool, optional
    :return: 
            Result class instance.
            - .result = True if file was saved successfully. Otherwise False.
            - .message = 'Saved revit file!'
            On exception:
            - result.status (bool) will be False.
            - result.message will contain exception message.
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    try:
        so = rdb.SaveOptions()
        so.Compact = compactFile
        doc.Save(so)
        returnValue.update_sep(True, 'Saved revit file!')
    except Exception as e:
        returnValue.update_sep(False, 'Failed to save revit file with exception: {}'.format(e))
    return returnValue


def enable_worksharing(
    doc, #
    worksetNameGridLevel = 'Shared Levels and Grids', # type: str
    worksetName = 'Workset1' # type: str
    ):
    # type: (...) -> res.Result
    '''
    Enables worksharing in a non workshared revit project file.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param worksetNameGridLevel: _description_, defaults to 'Shared Levels and Grids'
    :type worksetNameGridLevel: str, optional
    :return: 
            Result class instance.
            - .result = True if worksharing was enabled successfully. Otherwise False.
            - .message = 'Successfully enabled worksharing.'
            On exception:
            - result.status (bool) will be False.
            - result.message will contain exception message.
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    try:
        doc.EnableWorksharing('Shared Levels and Grids','Workset1')
        returnValue.message = 'Successfully enabled worksharing.'
    except Exception as e:
        returnValue.update_sep(False, 'Failed with exception: {}'.format(e))
    return returnValue