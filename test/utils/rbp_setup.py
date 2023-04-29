import clr

def add_rbp_ref():
    # Add batch processor scripting reference   s
    import revit_script_util
    import revit_file_util
    clr.AddReference('RevitAPI')
    clr.AddReference('RevitAPIUI')
    # NOTE: these only make sense for batch Revit file processing mode.
    doc = revit_script_util.GetScriptDocument()
    REVIT_FILE_PATH = revit_script_util.GetRevitFilePath()
    return doc

# output messages either to batch processor
def output(message = ''):
    revit_script_util.Output(str(message))
    