'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Purge unit testing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from duHast.Utilities import Result as res
from duHast.Utilities import FilesTab as filesTab
from duHast.Utilities.timer import Timer

from duHast.APISamples.Purge.RevitPurgeUnused import PURGE_ACTIONS


#: indentation for names of items purged
SPACER = '...'

# set up a timer objects
t = Timer()
tOverall = Timer()

#: list containing keys to be ignored in comparison code
#: these keys do not get purged by Revit's native purge unused and would therefore show up as false positives
COMPARISON_IGNORE= [
    'View Family Type(s)',
    'View Family Templates(s)',
    'View Filter(s)'
]

# doc                       current document
# typeIdGetter              function which returns all available type ids
# reportHeader              the first entry per row written to file
# outputFilePath            location of file
# counter                   action counter, if 0 the report file will be created from scratch, any other value means append to existing report file
def WriteAvailableTypeIds(doc, typeIdGetter, reportHeader, outputFilePath, counter):
    '''gets all available type ids from passed in type id getter and writes result to file'''
    resultValue = res.Result()
    writeType = 'a'
    if(counter == 0):
        writeType = 'w'
    try:
        typeIds = typeIdGetter(doc)
        # convert data to list of lists of strings for report writer
        data = []
        typeIdsAsString = [reportHeader]
        for tId in typeIds:
            typeIdsAsString.append(str(tId))
        data.append(typeIdsAsString)
        # writer data to file
        filesTab.writeReportData(
            outputFilePath,
            '',
            data,
            writeType)
        resultValue.UpdateSep(True,'Added type group ' + reportHeader + ' with ' + str(len(typeIds)) + ' entries ' +  writeType)
    except Exception as e:
        resultValue.UpdateSep(False,'Terminated purge unused ' + reportHeader + ' with exception: '+ str(e))
    return resultValue

# first     base line dictionary
# second    dictionary to be checked against base line
def CompareReportDictionaries(first,second):
    '''comparison will return all elements which are in first dictionary only, True if none are missing'''
    resultValue = res.Result()
    for key,value in first.items():
        if(key not in COMPARISON_IGNORE):
            if(second.has_key(key)):
                # check whether all values in base line key are in matching comparison key
                notInList = []
                for d in first[key]:
                    if d not in second[key]:
                        notInList.append(d)
                if(len(notInList) > 0):
                    resultValue.status = False
                    resultValue.AppendMessage(key + ' has different ids!')
                    data = [key] + notInList
                    resultValue.result.append(data)
            else:
                # entire key is missing!
                resultValue.AppendMessage(key + ' is missing!')
                resultValue.status = False
                data = [key] + first[key]
                resultValue.result.append(data)
    # check whether any dif was found
    if(len(resultValue.result) == 0):
        resultValue.UpdateSep(True, "All elements from first dictionary are in second dictionary")
    return resultValue

# data      list of list of strings
def ConvertReportDataIntoDictionary(data):
    '''build a dictionary where key is the first entry in each list, values are all subsequent entries in the same list'''
    dic = {}
    for d in data:
        dic[d[0]] = []
        for i in range(0,len(d)-1):
            if(i>0):
                dic[d[0]].append(d[i])
    return dic

# fileSource            bench mark type ids file
# fileTest              file to check against the benchmark
def CompareReportData(fileSource, fileTest):
    resultValue = res.Result()
    '''used to compare a bench mark results file containing type ids against a new results file
    will report missing or additional ids in results file'''
    sourceRows = filesTab.ReadTabSeparatedFile(fileSource)
    testRows = filesTab.ReadTabSeparatedFile(fileTest)
    sourceDic = ConvertReportDataIntoDictionary(sourceRows)
    testDic = ConvertReportDataIntoDictionary(testRows)
    # check benchmark against test
    statusSource = CompareReportDictionaries(sourceDic, testDic)
    # update overall status
    resultValue.UpdateStatus(statusSource.status)
    if(statusSource.status == True):
        resultValue.message ='Benchmark contains no additional ids'
    else:
        resultValue.message ='Benchmark contains additional ids'
        resultValue.AppendMessage(statusSource.message)
        resultValue.result.append({'Benchmark':statusSource.result})
    
    # check test against benchmark
    statusTest = CompareReportDictionaries(testDic, sourceDic)

    resultValue.UpdateStatus(statusTest.status)
    # update overall message with data from test benchmark comparison
    if(statusTest.status == True):
        resultValue.AppendMessage('\n' + 'Test contains no additional ids')
    else:
        resultValue.AppendMessage('\n' + 'Test contains additional ids')
        resultValue.AppendMessage(statusTest.message)
        resultValue.result.append({'Test':statusTest.result})

    return resultValue

# doc           current document
# filePath      fully qualified report file path
def ReportAvailableTypeIds(doc, filePath):
    '''calls all available type id getter functions and writes results to file'''
    resultValue = res.Result()
    tOverall.start()
    counter = 0 #any counter value greater then 0 means append to report file rather then creating a new file
    for pA in PURGE_ACTIONS:
        try:
            t.start()
            reportFlag = WriteAvailableTypeIds(
                doc,
                pA.testIdsGetter,
                pA.testReportHeader,
                filePath,
                counter
            )
            reportFlag.AppendMessage(SPACER + str(t.stop()))
            resultValue.Update(reportFlag)
        except Exception as e:
            resultValue.UpdateSep(False,'Terminated get available type id actions with exception: '+ str(e))
        counter = counter + 1
    resultValue.AppendMessage('Report available types duration: '+ str(tOverall.stop()))
    return resultValue
