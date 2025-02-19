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

using PushIt.Models;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Autodesk.Revit.DB;

namespace PushIt.RevitActions
{
    public class PushSingleRoomDataToRevit : IRevitAction
    {
        private readonly RevitDataModel _revitModel;
        private readonly RoomDataModel _roomToPush;
        private readonly Element _pushTarget;

        public Models.RevitDataModel RevitModel => _revitModel;

        public void Execute(Document doc)
        {

            // get shared parameter data from the model
            // get shared parameter ids by GUID
            Dictionary<string, ElementId> sharedParameterIdsByGUIDs = RevitUtils.SharedParaUtils.GetSharedParameterIdsByGUID(doc);

            //extract current model data from the element selected
            var modelDataPrevious = Utilities.Revit.RevitRoomObjectsConverter.ConvertSingleFamilyToRevitRoom(
                familyInstance: _pushTarget as Autodesk.Revit.DB.FamilyInstance,
                sampleModelRoom: _roomToPush,
                sharedParameterIdsByGUIDs: sharedParameterIdsByGUIDs
            );

            bool updateFamily = Utilities.Revit.FamilyUpdate.updateSingleFamilyInstance(
                doc: doc,
                familyInstance: _pushTarget as Autodesk.Revit.DB.FamilyInstance,
                roomData: _roomToPush,
                safetyOff: false
            );

            if (!updateFamily)
            {
                // log error
                return;
            }
           
            // get updated model data from the element selected
            var modelDataUpdated = Utilities.Revit.RevitRoomObjectsConverter.ConvertSingleFamilyToRevitRoom(
                familyInstance: _pushTarget as Autodesk.Revit.DB.FamilyInstance,
                sampleModelRoom: _roomToPush,
                sharedParameterIdsByGUIDs: sharedParameterIdsByGUIDs
            );

            //only remove previous data if there is a valid room
            if (modelDataPrevious != null)
            {
                // remove the previous Revit room from the data model before adding it back in with new data
                _revitModel.RemovePlacedRevitRoom(modelDataPrevious.RevitElementId);
            }
            

            // add the updated Revit room to the data model
            _revitModel.AddPlacedRevitRoom(_roomToPush.Id.Value, modelDataUpdated);

        }

        public PushSingleRoomDataToRevit(RevitDataModel revitModel, Models.RoomDataModel roomToPush, Element pushTarget)
        {
            _revitModel = revitModel;
            _roomToPush = roomToPush;
            _pushTarget = pushTarget;
        }
    }
}
