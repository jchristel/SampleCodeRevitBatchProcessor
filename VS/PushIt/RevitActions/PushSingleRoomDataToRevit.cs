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
        private readonly RoomsDataModel _roomToPush;
        private readonly Element _pushTarget;

        public Models.RevitDataModel RevitModel => _revitModel;

        public void Execute(Document doc)
        {
            
            // No matching rooms found
            Console.WriteLine("PushSingleRoomDataToRevit.Execute()");

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

            // remove the previous Revit room from the data model before adding it back in with new data
            _revitModel.RemovePlacedRevitRoom(modelDataPrevious.RevitElementId);

            // add the updated Revit room to the data model
            _revitModel.AddPlacedRevitRoom(_roomToPush.Id.Value, modelDataUpdated);

        }

        public PushSingleRoomDataToRevit(RevitDataModel revitModel, Models.RoomsDataModel roomToPush, Element pushTarget)
        {
            _revitModel = revitModel;
            _roomToPush = roomToPush;
            _pushTarget = pushTarget;
        }
    }
}
