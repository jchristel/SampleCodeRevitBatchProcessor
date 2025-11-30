#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2024, Jan Christel
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


from duHast.Utilities.Objects.base import Base

class DocManagerSheetData(Base):

    # field indices in csv export/import
    index_database_id = 0
    index_date = 1
    index_description = 2
    
    def __init__(
        self, number, name
    ):
        super(DocManagerSheetData, self).__init__()
    
        self.revisions = [] # to be set when associating with revisions
        self.number = number
        self.name = name
        self.current_revision_indicator="" # the revision i.e A, B or 1 or 2
        self.current_revision = None # the current revision object, to be set when associating with revisions
    
    def add_revision(self, revision):
        
        self.revisions.append(revision)
    
    def get_doc_manager_export_string(self, custom_fields=[], revision_data=[]):
        """
        Get sheet data as list csv export to doc manager.
        """
        
        # build export string, starting with Id as NEW for new sheet, then number and name
        export_string = ["NEW", self.number, self.name]
        
        #custom fields are not implemented yet, should just be exported as empty strings
        for field in custom_fields:
            export_string.append("")

        
        # add revision data
        # thats is done in 2 steps: 
        # add the current revision and its matching revision id,
        # add all other revision in order of the past in revision data.
        # if the sheet has no revision for a given revision data entry, 2 empty strings are added ( one for the revision and one for the revision id)
        if self.current_revision is not None:
            export_string.append(self.current_revision_indicator)
            export_string.append(self.current_revision.database_id)
        else:
            export_string.append("")
            export_string.append("")
    
        for rev_data in revision_data:
            # check if sheet has a revision for this revision data
            revision_found = False
            for sheet_revision in self.revisions:
                if sheet_revision.database_id == rev_data.database_id:
                    # found matching revision
                    revision_found = True
                    # check if this happen to be the current revision, 
                    if self.current_revision is not None and sheet_revision.database_id == self.current_revision.database_id:
                        # add the revision indicator from sheet
                        export_string.append(self.current_revision_indicator)
                        export_string.append(sheet_revision.database_id)
                    else:
                        # not sure how am I supposed to get the revision indicator here?
                        export_string.append(sheet_revision.revision_on_sheet)
                        export_string.append(sheet_revision.database_id)
                   
                    break
            
            if not revision_found:
                # no matching revision found, add empty strings
                export_string.append("")
                export_string.append("")

        return export_string