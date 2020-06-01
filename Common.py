#module managing output the revit batch processor console
import revit_script_util

#output messages either to batch processor (debug = False) or console (debug = True)
#default is console
def Output(message = '', debug = True):
    if not debug:
        revit_script_util.Output(str(message))
    else:
        print (message)

#transaction wrapper
#returns:
#   - False if something went wrong
#   - None if the action has no return value specified 
#   - return the outcome of the action or None if that is the outcome...
def InTransaction(tranny, action):
    result = None
    tranny.Start()
    try:
        result = action()
        tranny.Commit()
    except Exception as e:
        tranny.RollBack()
        result = False
    return result

#synchronises a Revit central file
#returns:
#   - true if sync without exception been thrown
#   - false if an exception occured
def SyncFile (doc):
    result = True
    # set up sync settings
    ro = RelinquishOptions(True)
    transActOptions = TransactWithCentralOptions()
    sync = SynchronizeWithCentralOptions()
    sync.Comment = "Synchronised by Revit Batch Processor"
    sync.SetRelinquishOptions(ro)
    #Synch it
    try:
        #save local first ( this seems to prevent intermittend crash on sync(?))
        doc.Save()
        doc.SynchronizeWithCentral(transActOptions, sync)
        #relinquish all
        WorksharingUtils.RelinquishOwnership(doc, ro, transActOptions)
    except Exception as e:
        result = False
    return result