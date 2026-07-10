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


import copy
import datetime

from duHast.Revit.Rooms.Export.to_data_room import get_all_room_data
from duHast.Revit.Levels.Export.to_data_level_building import get_all_level_data
from duHast.Utilities.Objects.result import Result
from duHast.Data.Objects.Collectors import data_room as dr
from duHast.Data.Objects.Collectors import data_level_building as dl
from duHast.Data.Utils.data_to_file import build_json_for_file
from duHast.pyRevit.UI.doc_selector import pick_document

from post_rooms import post_payload_stream

def rooms_export_entry(doc, uiapp, output, forms):

    """
    Exports rooms from the current Revit document to a JSON file.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output.
    :type output: pyRevit.output
    :param forms: pyRevit forms.
    :type forms: pyRevit.forms

    :return: Result object with status and message.
    :rtype: Result
    """

    # set up a status tracker
    return_value = Result()

    try:

        # ask user to select active or linked document
        selected_docs = pick_document(doc, forms, button_name="Select model to collect room data from", multiselect=True)
        if not selected_docs or len(selected_docs) == 0:
            return_value.append_message("No document(s) selected")
            return return_value

        # get going
        model_counter = 0
        
        # set up a progress bar
        with forms.ProgressBar(
            title="Exporting model: {value} of {max_value}", cancellable=True
        ) as pb:
        
            # get data for each selected document and write to file
            for selected_doc in selected_docs:
                
                # update progress bar                
                model_counter += 1
                pb.update_progress(model_counter, max_value=len(selected_docs))
                
                # get room data
                room_data = get_all_room_data(selected_doc)
                # get level data
                level_data = get_all_level_data(selected_doc)

                # v4 identity envelope (STRATEGY.md "Identity"). Model id is a
                # known stopgap: Title, not a GUID -- no stable GUID source exists
                # in duHast for a plain local (non-workshared, non-cloud) file.
                # Two consequences of keying on Title: two different files that
                # share a Title collide into ONE model record on the server,
                # and renaming a file forks its history into a new record. If
                # duHast ever exposes Document.CreationGUID / worksharing
                # GUIDs, switch to those.
                #
                # taken_at carries microseconds: it becomes the snapshot
                # filename server-side, so two pushes of the same model within
                # one second must not collide (the server skips a duplicate
                # timestamp rather than overwriting, but the client shouldn't
                # produce one in normal use). %f is fixed-width, so the string
                # stays lexically sortable -- the server's "lexical max =
                # newest" rule depends on that.
                project_info = selected_doc.ProjectInformation
                envelope = {
                    "project": {
                        "id": project_info.Number or selected_doc.Title,
                        "name": project_info.Name or selected_doc.Title,
                    },
                    "model": {
                        "id": selected_doc.Title,
                        "name": selected_doc.Title,
                    },
                    "snapshot": {
                        "taken_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    },
                }

                # a large export takes a while -- honour a cancel clicked
                # during it before starting the (also slow) post
                if pb.cancelled:
                    return_value.update_sep(False, "User cancelled.")
                    break

                # convert into a dictionary
                dic_room_data = {
                    dr.DataRoom.data_type:room_data
                }
                dic_room_data.update(envelope)

                # add some more properties before writing to json
                json_formatted_room = build_json_for_file(dic_room_data, "{}".format(selected_doc.Title))

                # convert into a dictionary. The envelope is deep-copied for
                # this second use: .update() shares the nested project/model/
                # snapshot dict instances, and the two exports must not be able
                # to cross-contaminate if anything downstream mutates its input.
                dic_level_data = {
                    dl.DataLevelBuilding.data_type:level_data
                }
                dic_level_data.update(copy.deepcopy(envelope))

                # add some more properties before writing to json
                json_formatted_level = build_json_for_file(dic_level_data, "{}".format(selected_doc.Title))

                # post to the server: gzip-compressed NDJSON stream, so a
                # >100 MB FFE export never gets buffered whole client-side or
                # server-side (see roommate's HANDOVER-streaming*.md).
                # A failed push flips the overall Result red but does NOT abort
                # the loop -- one bad model shouldn't discard the other models'
                # successful pushes, the run just must not end green.
                ok, status, text = post_payload_stream(json_formatted_room, json_formatted_level)
                if ok:
                    return_value.append_message(
                        "{}: server accepted ({})".format(selected_doc.Title, text)
                    )
                else:
                    return_value.update_sep(
                        False,
                        "{}: push failed ({}): {}".format(selected_doc.Title, status, text),
                    )

                # check for cancel
                if pb.cancelled:
                    return_value.update_sep(False, "User cancelled.")
                    break
        
    except Exception as e:
        return_value.update_sep(
            False, "Failed to export room data with exception: {}".format(e)
        )
        print("Failed to export room data with exception: {}".format(e))

    print("Finished")

    return return_value