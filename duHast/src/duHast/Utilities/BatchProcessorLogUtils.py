'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions to process Revit BatchProcessor log files.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2020  Jan Christel
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

# collection of tools used to process batch processor log files

# todo:
# write out current process IDs (empty text file with process id as file name)
#       script_util.GetSessionId()
# read out process ID from text file and find matching log files
# process log file:
#   - find files processed:
#            11/12/2020 18:01:40 : Processing Revit file (1 of 1) in Revit 2020 session.
#            11/12/2020 18:01:40 : 
#            11/12/2020 18:01:40 : 	P:\something\FileName.rvt
#            ....
#            25/11/2020 09:37:34 : 	- Operation completed.
#   - check whether an exception occurred when processing any of the above files:
#       - file(s) not found 
#           "WARNING: The following Revit Files do not exist"
#       - .net exception 
#           "ERROR: An error occurred while executing the task script!"
#       - timed out occurred and revit process got killed
#           "WARNING: Timed-out"
#   - delete process id pointer file
#   - show user processing results (only when something went wrong(?))

import clr
import System
from System.IO import Path
import glob
import time
import os
import json

# custom result class from common library
from duHast.Utilities import Result as res
# library from common library
from duHast.Utilities import Utility as util

#: global variable controlling debug output
debugMode_ = False

#: Message snippets which indicate processing of a file went bad
EXCEPTION_MESSAGES = [
    'ERROR: An error occurred while executing the task script! Operation', # revit batch p message when script is buggy
    'WARNING: Timed-out', # revit batch p message when revit times out
    'Exception: [Exception]', # Revit Batch P message when an exception occurs
    '\t- \tMessage: An unrecoverable error has occurred.  The program will now be terminated.', # Revit message when it crashes out
    'Script Exception:' # custom script message...something the script was meant to do failed
]

# output...
def Output(message = ''):
    if debugMode_:
        print (message)
        
def AdjustSessionIdForFileName(id):
    '''
    Removes chevrons and replace colons with underscores in session id supplied by revit batch processor so it\
        can be used in a file name.

    :param id: Session id supplied by revit batch processor.
    :type id: str

    :return: Re-formatted session id.
    :rtype: str
    '''

    # remove colons
    sessionIdChanged = id.replace(':','_')
    # remove chevrons
    sessionIdChanged = sessionIdChanged[1:-1]
    return sessionIdChanged

def AdjustSessionIdFileNameBack(fileNameId):
    '''
    Re-introduces chevrons and replaces underscores with colons to match session Id format used in batch processor to a\
        file name using a batch processor supplied id.

    :param fileNameId: A file name containing a session id with all illegal characters replaced.
    :type fileNameId: str

    :return: A session id.
    :rtype: str
    '''

    # re-instate colons
    sessionIdChanged = fileNameId.replace('_',':')
    # remove chevrons
    sessionIdChanged = '<' + sessionIdChanged + '>'
    return sessionIdChanged

def WriteSessionIdMarkerFile(folderPath, sessionId):
    '''
    Writes out an empty marker file in given directory. 
    
    - File is of type .txt
    - File name is the batch processor sessionId used to identify the log file belonging to this process.

    :param folderPath: Directory of where the file will be written to.
    :type folderPath: str
    :param sessionId: Session id supplied by revit batch processor.
    :type sessionId: str

    :return: True if marker file was written successfully, otherwise False.
    :rtype: bool
    '''

    fileName = os.path.join(folderPath, str(sessionId)+'.txt')
    status = True
    try:
        f = open(fileName, "w")
        f.close()
    except:
        status = False
    return status

def GetCurrentSessionIds(folderPath):
    '''
    Returns file names of all text files in a given directory representing session Ids.

    Files will be deleted immediately after reading

    :param folderPath: Directory of where test files are located
    :type folderPath: str

    :return: A list of ids in string format.
    :rtype: [str]
    '''
    ids = []
    file_list = glob.glob(folderPath + '\\*' + '.txt')
    # delete marker files
    resultDelete = True
    for fd in file_list:
        if(debugMode_ == False):
            resultDelete = resultDelete & util.FileDelete(fd)
    if(not resultDelete):
        Output ('Failed to delete a marker file!')
    for f in file_list:
        ids.append(AdjustSessionIdFileNameBack(Path.GetFileNameWithoutExtension(f)))
    return ids

def GetLogFiles(listOfSessionIds):
    '''
    Returns a list of fully qualified filepath to log files matching the provided session Ids.

    :param listOfSessionIds: List of session ids.
    :type listOfSessionIds: [str]

    :return: List of fully qualified file path.
    :rtype: [str]
    '''

    # save the current file in epoch
    timeNow = time.time()
    fileList = glob.glob(os.path.join(os.getenv('LOCALAPPDATA'),'BatchRvt') + '\\*' + '.log')
    logFiles = []
    if len(fileList) > 0:
        for l in fileList:
            # check whether file is older than 24h
            fileTime = os.path.getmtime(l)
            # 24 hr are 86400 seconds
            timeOut = 86400
            if debugMode_ == True:
                timeOut = 8640000
            if timeNow - fileTime < timeOut:
                # read the first two rows of the file to get the id
                idString = GetSessionIdFromLogFile(l)
                for idToMatch in listOfSessionIds:
                    if idToMatch == idString:
                        logFiles.append(l)
            else:
                Output('File is to old: ' + str(l))
    return logFiles

def GetSessionIdFromLogFile(filePath):
    '''
    Reads the first two rows of a log file to get the session Id used.

    :param filePath: Fully qualified file path to log file
    :type filePath: str

    :return: The session id, or if not not a log file: an empty string.
    :rtype: str
    '''

    rowCounter = 0
    retrievedId = ''
    for line in open( filePath, 'r' ):
        # read row 2 only
        if(rowCounter == 1):
            data = json.loads(line)
            message = GetMessageFromJson(data)
            retrievedId = GetIdFromRow(message)
            break
        rowCounter += 1
    return retrievedId

def GetIdFromRow(row):
    '''
    Extracts the session Id from logfile row.

    sample: 
    {"date":{"local":"17/12/2020","utc":"17/12/2020"},"time":{"local":"16:49:27","utc":"05:49:27"},"sessionId":"235e2180-dc33-4d61-8773-1005a59344c0","message":{"msgId":"","message":"Session ID: <2020-12-17T05:49:27.559Z>"}}

    Note: There are two session id fields in thi string!
    
    TODO: Do some error handling!

    :param row: A json formatted string with the session id in chevrons.
    :type row: str

    :return: The session id.
    :rtype: str
    '''

    first = '<'
    last = '>'
    t = GetTextBetween(row, first, last)
    return first + t + last

def GetTextBetween(text, first, last):
    '''
    Returns text in between characters

    :param text: Text to parse
    :type text: str
    :param first: String indicating start
    :type first: str
    :param last: String indicating end
    :type last: str

    :return: string in between start and end.
    :rtype: str
    '''

    start = text.index(first) + len(first)
    end = text.index(last, start)
    return text[start:end]

def GetMessageFromJson(data):
    '''
    Returns the outer message string from json formatted message field in log file.

    sample: 
    {"date":{"local":"17/12/2020","utc":"17/12/2020"},"time":{"local":"16:49:27","utc":"05:49:27"},"sessionId":"235e2180-dc33-4d61-8773-1005a59344c0","message":{"msgId":"","message":"Session ID: <2020-12-17T05:49:27.559Z>"}}

    This includes leading tab characters

    :param data: json formatted row of logfile
    :type data: str

    :return: The message string
    :rtype: str
    '''
    outerMessage = data['message']
    return outerMessage['message']

def ProcessLogFile(filePath):
    '''
    Process revit batch processor session log file.
    
    - find Revit files processed:
    - check whether an exception occurred when processing any of the above files.

    :param filePath: Fully qualified file path to json formatted log file
    :type filePath: str

    :return: returns list of arrays in format:
        [[processed Revit file name, status of processing (true or false), message]]
    :rtype: [[str]]
    '''

    filesProcessStatus = []
    # get all files processed
    try:
        filesProcessed = GetFilesProcessed(filePath)
        # check whether any file not founds came back
        try:
            filesNotFound = GetFilesNotFound(filesProcessed)
            try:
                # filter filesProcessed by files not found
                filesToCheck = filterFilesNotFound(filesProcessed, filesNotFound)
                # check for exceptions during file processing
                for fileToCheck in filesToCheck:
                    try:
                        status, message = GetProcessStatus(fileToCheck, filePath)
                    except Exception as e:
                        Output ('GetProcessStatus: ' + str(e))
                    dummy = [fileToCheck, status, message]
                    filesProcessStatus.append(dummy)
                # add files not found
                for f in filesNotFound:
                    dummy = [f[0], False, ['File not found']]
                    filesProcessStatus.append(dummy)
            except Exception as e:
                Output ('FileToCheck: ' + str(e))
        except Exception as e:
            Output ('GetFilesNotFound: ' + str(e))
    except Exception as e:
        Output ('GetFilesProcessed: ' + str(e))
    return filesProcessStatus

# filtering files not found from overall file list
#
# filesProcessed: list of arrays, first entry in array is fully qualified file path
# filesNotFound: list of fully qualified file path
# returns a list of fully qualified file path (of files marked as found)
def filterFilesNotFound(filesProcessed, filesNotFound):
    filteredList = []
    for fileName,status in filesProcessed:
        flag = False
        for fn, fnStatus in filesNotFound:
            if(fn == fileName):
                flag = True
                break
        if (not flag):
            filteredList.append(fileName)
    return filteredList

def GetProcessStatus(fileToCheck, logFilePath):
    '''
    Reads a log file and checks whether any exception occurred when processing a specific revit file.

    :param fileToCheck: Fully qualified file path of Revit file which was processed
    :type fileToCheck: str
    :param logFilePath: The fully qualified batch processor session log file path.
    :type logFilePath: str

    :return: A process status and a message.

        - process status: True if no exception occurred during revit file processing, otherwise false
        - message: the exception message recorded in the log file.

    :rtype: bool, str
    '''

    message = ['Found no match in log file']
    # flag indicating whether we managed to retrieve processing data for a file
    foundMatch = False
    jsonData = ReadLogFile(logFilePath)
    # get data block showing how each file was processed
    unformattedRevitFileProcessMessages = GetLogBlocks(jsonData, '\t- Processing file (', ['\t- Task script operation completed.','\t- Operation aborted.'], True)
    processStatus = True
    # loop over messages in this block and check for time out, and exception messages
    for messageBlock in  unformattedRevitFileProcessMessages:
        # check if right file the file name
        # todo
        fileName = GetFileNameFromDataBlock(messageBlock)
        if(fileName == fileToCheck):
            Output('file to check: ' +str(fileToCheck + '     file found: '+fileName) +'    is match '  +str(fileName == fileToCheck))
            foundMatch = True
            # flag to show whether logs show any issues
            foundProblem = False
            for m in messageBlock:
                Output(m)
                # check for exceptions
                for exceptionMessage in EXCEPTION_MESSAGES:
                    if(exceptionMessage in m):
                        processStatus = False
                        foundProblem = True
                        message = [m.strip()]
                        break
            if (foundProblem == False):
                message = '[ok]'
                processStatus = True
    # check if a match for given file was found in log data
    if(foundMatch == False):
        processStatus = False
        message = '[Failed to retrieve processing data for file.]'
    return processStatus, message
        
def GetFileNameFromDataBlock(messageBlock):
    '''
    Extracts the file name from a process message block.

    :param messageBlock: list of json formatted rows representing all messages received during file process
    :type messageBlock: [str]

    :return: The fully qualified file path of the file processed
    :rtype: str
    '''

    # check if this is a cloud model
    if('CLOUD MODEL' in messageBlock[0]):
        #['\t- Processing file (1 of 1): CLOUD MODEL', '\t- ', '\t- \tProject ID: GUID', '\t- \tModel ID: GUID',...]
        messageStarter = '\t- \t'
        fileName = messageBlock[3].Trim()[len(messageStarter)-1:]
    else:
        # ["\t- Processing file (x of y): file path"}},...]
        messageStarter = '\t- Processing file (x of y): '
        fileName = messageBlock[0].Trim()[len(messageStarter)-1:]
    return fileName

def GetFilesProcessed(filePath):
    '''
    Reads a batch processor logfile and extracts all file names of files processed.
    
    :param filePath: The fully qualified file path to log file.
    :type filePath: str

    :return: a list lists containing The fully qualified file path for each file processed and their process status. True for no exception encountered, otherwise false.
        [[filepath, status]]
    :rtype: [[str, bool]]
    '''
    # log file structure:
    # start of file list (file server):
    #   {"date":{"local":"17/12/2020","utc":"17/12/2020"},"time":{"local":"16:49:28","utc":"05:49:28"},"sessionId":"235e2180-dc33-4d61-8773-1005a59344c0","message":{"msgId":"","message":"Revit Files for processing (1):"}}
    #   {"date":{"local":"17/12/2020","utc":"17/12/2020"},"time":{"local":"16:49:28","utc":"05:49:28"},"sessionId":"235e2180-dc33-4d61-8773-1005a59344c0","message":{"msgId":"","message":""}}
    #   {"date":{"local":"17/12/2020","utc":"17/12/2020"},"time":{"local":"16:49:28","utc":"05:49:28"},"sessionId":"235e2180-dc33-4d61-8773-1005a59344c0","message":{"msgId":"","message":"\tP:\\something\\FileName.rvt"}}
    #   {"date":{"local":"17/12/2020","utc":"17/12/2020"},"time":{"local":"16:49:28","utc":"05:49:28"},"sessionId":"235e2180-dc33-4d61-8773-1005a59344c0","message":{"msgId":"","message":"\tFile exists: YES"}}
    #   {"date":{"local":"17/12/2020","utc":"17/12/2020"},"time":{"local":"16:49:28","utc":"05:49:28"},"sessionId":"235e2180-dc33-4d61-8773-1005a59344c0","message":{"msgId":"","message":"\tFile size: 86.93MB"}}
    #   {"date":{"local":"17/12/2020","utc":"17/12/2020"},"time":{"local":"16:49:28","utc":"05:49:28"},"sessionId":"235e2180-dc33-4d61-8773-1005a59344c0","message":{"msgId":"","message":"\tRevit version: Autodesk Revit 2020 (Build: 20200826_1250(x64))"}}
    #   {"date":{"local":"17/12/2020","utc":"17/12/2020"},"time":{"local":"16:49:28","utc":"05:49:28"},"sessionId":"235e2180-dc33-4d61-8773-1005a59344c0","message":{"msgId":"","message":""}}
    #   {"date":{"local":"17/12/2020","utc":"17/12/2020"},"time":{"local":"16:49:28","utc":"05:49:28"},"sessionId":"235e2180-dc33-4d61-8773-1005a59344c0","message":{"msgId":"","message":"Starting batch operation..."}}
    # end of file list
    # start of file list (cloud model):
    #   {"date":{"local":"18/05/2021","utc":"18/05/2021"},"time":{"local":"19:20:00","utc":"09:20:00"},"sessionId":"e8a39f45-ca88-464f-a32f-278f0414280f","message":{"msgId":"","message":"Revit Files for processing (1):"}}
    #   {"date":{"local":"18/05/2021","utc":"18/05/2021"},"time":{"local":"19:20:00","utc":"09:20:00"},"sessionId":"e8a39f45-ca88-464f-a32f-278f0414280f","message":{"msgId":"","message":""}}
    #   {"date":{"local":"18/05/2021","utc":"18/05/2021"},"time":{"local":"19:20:00","utc":"09:20:00"},"sessionId":"e8a39f45-ca88-464f-a32f-278f0414280f","message":{"msgId":"","message":"\tCLOUD MODEL"}}
    #   {"date":{"local":"18/05/2021","utc":"18/05/2021"},"time":{"local":"19:20:00","utc":"09:20:00"},"sessionId":"e8a39f45-ca88-464f-a32f-278f0414280f","message":{"msgId":"","message":"\tProject ID: ee514b99-fac1-441a-ba98-6912c4aa4fdb"}}
    #   {"date":{"local":"18/05/2021","utc":"18/05/2021"},"time":{"local":"19:20:00","utc":"09:20:00"},"sessionId":"e8a39f45-ca88-464f-a32f-278f0414280f","message":{"msgId":"","message":"\tModel ID: c15a664d-fab8-4153-8532-b8fa04402528"}}
    #   {"date":{"local":"18/05/2021","utc":"18/05/2021"},"time":{"local":"19:20:00","utc":"09:20:00"},"sessionId":"e8a39f45-ca88-464f-a32f-278f0414280f","message":{"msgId":"","message":"\tRevit version: 2020"}}
    #   {"date":{"local":"18/05/2021","utc":"18/05/2021"},"time":{"local":"19:20:00","utc":"09:20:00"},"sessionId":"e8a39f45-ca88-464f-a32f-278f0414280f","message":{"msgId":"","message":""}}
    # end of file list
    listOfFiles = []
    jsonData = ReadLogFile(filePath)
    # get data block showing which files are to be processed
    # there should just be one ...
    logBlocks = GetLogBlocks(jsonData, 'Revit Files for processing', ['Starting batch operation...'], False)
    if(len(logBlocks) > 0):
        unformattedRevitFileProcessMessages = logBlocks[0]
        # parse data block and get list of files and file exists status
        # each file block is proceeded by an empty message row
        # last entry is also an empty message block!
        for x in range(len(unformattedRevitFileProcessMessages)):
            # check for start of data block 
            # Output('unformatted messages '+str(unformattedRevitFileProcessMessages))
            if(unformattedRevitFileProcessMessages[x] == '' and x + 3 <= len(unformattedRevitFileProcessMessages)):
                # check whether cloud model or file server model
                if('CLOUD MODEL' in unformattedRevitFileProcessMessages[x + 1]):
                    # get file data from next two rows
                    # substitute file name with file GUID, fake the status always exists
                    dummy = [unformattedRevitFileProcessMessages[x + 3],'File exists: YES']
                else:
                    # get file data from next two rows
                    dummy = [unformattedRevitFileProcessMessages[x + 1],unformattedRevitFileProcessMessages[x + 2]]
                listOfFiles.append(GetFileData(dummy))
    return listOfFiles

# method parsing two rows of json formatted data
#
# data list of 2 rows of Json formatted data
# sample of file system:
#18/05/2021 15:57:53 : 	File exists: YES
#18/05/2021 15:57:53 : 	File size: 199.38MB
# sample of BIM360:
#18/05/2021 15:37:23 : 	Project ID: a valid guid
#18/05/2021 15:37:23 : 	Model ID: a valid guid
# note: when processing BIM360 files batch processor is not checking whether the file exists upfront!
# returns list in format
# [filename, file exists status as bool]
def GetFileData(data):
    # trim white spaces from file name
    fileName = data[0].Trim()
    fileStatus = False
    # check whether file status contains a YES or whether this is a cloud model 
    # (RBP does not check upfront whether a cloud model exists!)
    if ('YES' in data[1] or 'Project ID' in data[1]):
        fileStatus = True
    return [fileName,fileStatus]  

def GetFilesNotFound(filesProcessed):
    '''
    Filters list of all files meant to be processed and returns the ones flagged as file not found.

    :param filesProcessed: array of lists in format: [[filename, status as bool],[filename, status as bool],...]
    :type filesProcessed: [[str, bool]]

    :return: array of lists in format: [[filename, status as bool],[filename, status as bool],...]
    :rtype: [[str, bool]]
    '''

    fileNotFound = []
    for f in filesProcessed:
        if f[1]==False:
            fileNotFound.append(f)
    return fileNotFound

def GetLogBlocks(jsonData, startMarker, endMarkers, multipleBlocks):
    '''
    Reads json formatted data into blocks per files processed.

    Returns the message sections per row entry only.

    :param jsonData: List of logfile rows in json data format
    :type jsonData: [str]
    :param startMarker: String in messages indicating start of block.
    :type startMarker: str
    :param endMarkers: String in messages indicating end of block.
    :type endMarkers: str
    :param multipleBlocks: Flag indicating whether there are multiple data block in log file to be returned
    :type multipleBlocks: bool

    :return: List of list of str
    :rtype: [[str]]
    '''

    unformattedBlockData = []
    dataBlock = []
    messageString = ''
    # extract rows belonging to blocks
    fileBlock = False
    #Output('json data: ' + str(jsonData))
    for data in jsonData:
        messageString = GetMessageFromJson(data)
        if messageString.startswith(startMarker) and fileBlock == False:
            fileBlock = True
        # flag to indicate we found a match for end of block
        matchEndBlock = False
        for endMarker in endMarkers:
            match = False
            if messageString.startswith(endMarker) and fileBlock == True:
                matchEndBlock = True
                unformattedBlockData.append(dataBlock)
                dataBlock = []
                fileBlock = False
                match = True
                break
        if(not multipleBlocks and match):
            break
        if (fileBlock):
            dataBlock.append(messageString)
    # check for open block
    if (fileBlock == True and matchEndBlock == False):
        # append this data...hopefully there is an exception message in there!!
        unformattedBlockData.append(dataBlock)
        Output('Added open data block')
        Output(dataBlock)
        Output('')
    return unformattedBlockData

def ReadLogFile(filePath):
    '''
    Reads batch processor log file into lists of json objects.
    
    Sample row:
        {'sessionId': '778e87a5-4b94-4552-9e7e-c9ed38b5caee', 'time': {'local': '09:35:45', 'utc': '22:35:45'}, 'date': {'local': '25/11/2020', 'utc': '24/11/2020'}, 'message': {'msgId': '', 'message': ''}}
    
    :param filePath: The fully qualified file path to log file in json format
    :type filePath: str

    :return: list of json objects
    :rtype: [json]
    '''

    data = []
    with open(filePath) as f:
        for line in f:
            data.append(json.loads(line))
    return data

def ProcessLogFiles(folderPath, debug = False):
    '''
    Loops over log files and checks whether any exceptions occurred during revit files processing.

    :param folderPath: Fully qualified directory path where marker files are stored.
    :type folderPath: str
    :param debug: Flag indicating whether this is running in debug mode which will output some debug messages, defaults to False
    :type debug: bool, optional

    :return: List of lists of revit files processed in format:
        [logId,[processed Revit file name, status of processing (true or false), message]]
    :rtype: [str,[str, bool, str]]
    '''

    returnValue = res.Result()
    debugMode_ = debug
    logfileResults = []
    try:
        # get all marker files
        markerFileIds = GetCurrentSessionIds(folderPath)
        if(debugMode_):
            returnValue.AppendMessage('Found marker file(s): ' + str(len(markerFileIds)))
        if(len(markerFileIds) > 0):
            # find log files matching markers
            logFiles = GetLogFiles(markerFileIds)
            if(debugMode_):
                returnValue.AppendMessage('Found log file(s): ' + str(len(logFiles)))
            if(len(logFiles) == len(markerFileIds)):
                data = []
                for lf in logFiles:
                    # debug output
                    message = 'Processing log file(s): ' + lf
                    #returnValue.AppendMessage('Processing log files: ' + lf)
                    try:
                        data = ProcessLogFile(lf)
                        if (len(data) > 0):
                            message = message + ' [Got processed Revit file(s) data: ' + str(len(data)) +']'
                        else:
                            # dummy run no files processed!
                            message = message + ' [No Revit file(s) processed!]'
                    except Exception as e:
                        message = message + ' [An exception occurred: ' + str(e) + ']'
                    if(debugMode_):
                        returnValue.AppendMessage(message)
                    for d in data:
                        logfileResults.append(d)
                returnValue.AppendMessage('\n')
                returnValue.AppendMessage('Processed file(s) results:')
                # store results in return object
                for lfResults in logfileResults:
                    listToStr = '\t'.join(map(str, lfResults)) 
                    returnValue.AppendMessage(listToStr)
                returnValue.status = True
            else:
                returnValue.UpdateSep(False,'Number of log files [' + str(len(logFiles)) + '] does not match required number: ' + str(len(markerFileIds))) 
        else:
            returnValue.UpdateSep(False,'No marker files found in location: ' + str(folderPath))
    except Exception as e:
        returnValue.UpdateSep(False, 'Terminated with Exception '+ str(e))    
    return returnValue