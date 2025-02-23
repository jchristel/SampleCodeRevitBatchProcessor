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
using duHast.PushIt.Models;
using System;
using System.Collections.Generic;

namespace duHast.PushIt.RevitActions
{
    public class HighlightRoomsInRevit : IRevitAction
    {
        private readonly RoomDataModel _roomToPush;
        private readonly UIDocument _uiDoc;
        private readonly RevitDataModel _revitModel;

        public Models.RevitDataModel RevitModel => _revitModel;

        public void Execute(Document doc)
        {
            List<ElementId> elementIds = new List<ElementId>();

            // get the selected elements
            foreach (var room in _roomToPush.MatchingRevitRooms)
            {
                elementIds.Add(new ElementId(room.RevitElementId));
            }

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
                // TODO: log the exception
                
            }
        }

        public HighlightRoomsInRevit(Models.RevitDataModel revitModel, Models.RoomDataModel roomToPush, UIDocument uiDoc)
        {
            _revitModel = revitModel;
            _roomToPush = roomToPush;
            _uiDoc = uiDoc;
        }
    }
}
