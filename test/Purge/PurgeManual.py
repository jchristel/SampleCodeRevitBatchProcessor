'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Purge unit testing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from duHast.Utilities import result as res
from duHast.Utilities import files_tab as filesTab
from duHast.Utilities.timer import Timer

from duHast.Revit.Purge.purge_unused import PURGE_ACTIONS


#: indentation for names of items purged
SPACER = '...'

# set up a timer objects
t = Timer()
TIMER_OVERALL = Timer()

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
        filesTab.write_report_data(
            outputFilePath,
            '',
            data,
            writeType)
        resultValue.update_sep(True,'Added type group ' + reportHeader + ' with ' + str(len(typeIds)) + ' entries ' +  writeType)
    except Exception as e:
        resultValue.update_sep(False,'Terminated purge unused ' + reportHeader + ' with exception: '+ str(e))
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
                    resultValue.append_message('{} has different ids!'.format(key))
                    data = [key] + notInList
                    resultValue.result.append(data)
            else:
                # entire key is missing!
                resultValue.append_message('{} is missing!'.format(key))
                resultValue.status = False
                data = [key] + first[key]
                resultValue.result.append(data)
    # check whether any dif was found
    if(len(resultValue.result) == 0):
        resultValue.update_sep(True, "All elements from first dictionary are in second dictionary")
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
    sourceRows = filesTab.read_tab_separated_file(fileSource)
    testRows = filesTab.read_tab_separated_file(fileTest)
    sourceDic = ConvertReportDataIntoDictionary(sourceRows)
    testDic = ConvertReportDataIntoDictionary(testRows)
    # check benchmark against test
    statusSource = CompareReportDictionaries(sourceDic, testDic)
    # update overall status
    resultValue.update_status(statusSource.status)
    if(statusSource.status == True):
        resultValue.message ='Benchmark contains no additional ids'
    else:
        resultValue.message ='Benchmark contains additional ids'
        resultValue.append_message(statusSource.message)
        resultValue.result.append({'Benchmark':statusSource.result})
    
    # check test against benchmark
    statusTest = CompareReportDictionaries(testDic, sourceDic)

    resultValue.update_status(statusTest.status)
    # update overall message with data from test benchmark comparison
    if(statusTest.status == True):
        resultValue.append_message('\n' + 'Test contains no additional ids')
    else:
        resultValue.append_message('\n' + 'Test contains additional ids')
        resultValue.append_message(statusTest.message)
        resultValue.result.append({'Test':statusTest.result})

    return resultValue

# doc           current document
# filePath      fully qualified report file path
def ReportAvailableTypeIds(doc, filePath):
    '''calls all available type id getter functions and writes results to file'''
    resultValue = res.Result()
    TIMER_OVERALL.start()
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
            reportFlag.append_message('{}{}'.format(SPACER,t.stop()))
            resultValue.update(reportFlag)
        except Exception as e:
            resultValue.update_sep(False,'Terminated get available type id actions with exception: {}'.format(e))
        counter = counter + 1
    resultValue.append_message('Report available types duration: {}'.format(TIMER_OVERALL.stop()))
    return resultValue
