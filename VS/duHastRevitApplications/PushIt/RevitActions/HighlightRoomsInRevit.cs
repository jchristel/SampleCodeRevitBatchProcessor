//
//License:
//
//
// Revit Batch Processor Sample Code
//
// BSD License
// Copyright 2025, Jan Christel
// All rights reserved.

// Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

// - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
// - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
// - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
//
// This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed.
// In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits;
// or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
//
//
//

using Autodesk.Revit.DB;
using Autodesk.Revit.UI;
using duHastNet.PushIt.Models;
using System;
using System.Collections.Generic;

namespace duHastNet.PushIt.RevitActions
{
    public class HighlightRoomsInRevit : RevitActionBase, duHastNet.RevitUtils.RevitActions.IRevitAction
    {
        private readonly RoomDataModel _roomToPush;
        private readonly UIDocument _uiDoc;

        public (string messageAction, Utils.WPF.Stores.MessageTypes messageActionType) Execute(Document doc)
        {
            List<ElementId> elementIds = [];

            try
            {
                // get the selected elements
                foreach (var room in _roomToPush.MatchingRevitRooms)
                {
                    elementIds.Add(new ElementId(room.RevitElementId));
                }

                // add any split room
                foreach (var room in _roomToPush.MatchingSplitRevitRooms)
                {
                    elementIds.Add(new ElementId(room.RevitElementId));
                }

                // log the action
                AddMessage($"Highlighting {elementIds.Count} rooms in Revit", Utils.WPF.Stores.MessageTypes.Information);

                // attempt to highlight and zoom to selected elements
                try
                {
                    // highlight the elements
                    _uiDoc.Selection.SetElementIds(elementIds);

                    // zoom to the elements
                    _uiDoc.ShowElements(elementIds);

                    // regenerate the view
                    _uiDoc.RefreshActiveView();
                }
                catch (Exception ex)
                {
                    //log the exception
                    AddMessage($"Error highlighting rooms in Revit: {ex.Message}", Utils.WPF.Stores.MessageTypes.Error);

                }
            }
            catch (Exception ex)
            {
                //log the exception
                AddMessage($"Error highlighting rooms in Revit: {ex.Message}", Utils.WPF.Stores.MessageTypes.Error);
            }

            // build the return message depending on error count
            return GetReturnValue("Highlighted rooms in Revit");
        }

        public HighlightRoomsInRevit(Models.RevitDataModel revitModel, Models.RoomDataModel roomToPush, UIDocument uiDoc)
        {
            RevitModel = revitModel;
            _roomToPush = roomToPush;
            _uiDoc = uiDoc;
        }
    }
}
