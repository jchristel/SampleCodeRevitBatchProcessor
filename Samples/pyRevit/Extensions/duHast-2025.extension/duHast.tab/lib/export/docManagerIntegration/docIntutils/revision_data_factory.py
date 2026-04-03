#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2026, Jan Christel
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


from duHast.Utilities.Objects.result import Result

from Autodesk.Revit.DB import Revision

DEBUG = True

def get_revision_data(doc, revit_data_model):
    """
    Get the revision data from the model and add it to the data model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_data_model: The data model to add the revision data to.
    :type revit_data_model: RevitDataModel
    
    :return:Result object with status, message, and the data model with revision data.
    :rtype: Result
    
    """
    return_value = Result()
    
    try:
        
        # import the UI class from the DocManagerSettingsUI namespace
        # do this in this function to allow the caller to register the UI dll before this code is executed
        from  duHastNet.DocManager.Revit.Utilities.RevitData import RevitRevision

        # get the revision from the model
        all_revision_ids =  Revision.GetAllRevisionIds(doc)
        for revision_id in all_revision_ids:
            # get the revision element
            revit_revision = doc.GetElement(revision_id)

            # create a RevitRevision object and add it to the list in the data model
            rev = RevitRevision(revision_id.Value,  revit_revision.RevisionDate,  revit_revision.Description)

            if DEBUG:
                print("...{}".format(rev))

            # add the revision to the data model
            revit_data_model.AddRevision(rev)

        # add the data model with revisions to the result object
        return_value.result.append(revit_data_model)
        return_value.update_sep(True, "Successfully retrieved revision data from model.")
        return return_value
    except Exception as e:
        message = "Error getting revision from file: {}".format( e)
        return_value.update_sep(False, message)
        return return_value