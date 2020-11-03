import clr
clr.AddReference('System.Windows.Forms')
clr.AddReference('IronPython.Wpf')

# import WPF creator and base window
import wpf
from System import Windows

import sys, getopt, os

# UI class
class MyWindow (Windows.Window):
    def __init__(self, revitFiles):
        wpf.LoadComponent(self,xamlFullFileName_)
        self.revitfiles = revitFiles
        self.files.ItemsSource = revitFiles

    def BtnOK(self, sender, EventArgs):
        print('ok')
    
    def BtnCancel(self, sender, EventArgs):
        print('cancel')


class MyItem:
    "An item to represent a row in a grid."

    def __init__(self, name):
        self.name = name

# main method
def main(argv):
    gotArgs, inputDirectory, outputfileNumber = processArgs(argv)
    if(gotArgs):
        # get revit files in input dir
        revitfiles = getRevitFiles(inputDirectory)
        if(len(revitfiles) > 0):
            # lets show the window
            MyWindow(revitfiles).ShowDialog()
        else:
            # show messagew box
            print ('No Revit project files found!')
            sys.exit(2)
    else:
        sys.exit()
# helper method retrieving revit files in a given directory
def getRevitFiles(directory):
    files = [MyItem(r'C:\test\firstfile.rfp'), MyItem(r'C:\test\secondfile.rfp')]
    #files = [r'C:\test\firstfile.rfp',r'C:\test\secondfile.rfp']
    return files

# argument processor
def processArgs(argv):
    inputDirectory = ''
    outputDirectory = ''
    outputfileNumber = 1
    gotArgs = False
    try:
        opts, args = getopt.getopt(argv,"hi:o:n:",["inputDir=","outputDir=",'numberFiles='])
    except getopt.GetoptError:
        print 'test.py -i <inputDirectory> -o <outputDirectory> -n <numberOfOutputFiles>'
    for opt, arg in opts:
        if opt == '-h':
            print 'test.py -i <inputDirectory> -o <outputDirectory> -n <numberOfOutputFiles>'
        elif opt in ("-i", "--inputDir"):
            inputDirectory = arg
            gotArgs = True
        elif opt in ("-o", "--outputDir"):
            outputDirectory = arg
            gotArgs = True
        elif opt in ("-n", "--numberFiles"):
            try:
                value = int(arg)
                outputfileNumber = value
                gotArgs = True
            except ValueError:
                print (arg + ' value is not an integer')
                gotArgs = False
    # check if input values are valid
    if (outputfileNumber < 0 or outputfileNumber > 100):
        gotArgs = False
        print ('The number of output files must be bigger then 0 and smaller then 100')
    if(not FileExist(inputDirectory)):
        gotArgs = False
        print ('Invalid input directory: ' + str(inputDirectory))
    if(not FileExist(outputDirectory)):
        gotArgs = False
        print ('Invalid output directory: ' + str(outputDirectory))

    return gotArgs, inputDirectory, outputfileNumber


def GetFolderPathFromFile(filePath):
    try:
        value = os.path.dirname(filePath)
    except Exception:
        value = ''
    return value

def FileExist(path):
    try:
        value = os.path.exists(path)
    except Exception:
        value = False
    return value

# the directory this script lives in
currentScriptDir_ = GetFolderPathFromFile(sys.path[0])
# xaml file name
xamlfile_ = 'ui.xaml'
# xaml full path
xamlFullFileName_ =  os.path.join(currentScriptDir_, xamlfile_)


# module entry
if __name__ == "__main__":
   main(sys.argv[1:])
