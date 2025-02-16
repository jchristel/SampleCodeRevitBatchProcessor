using System.Collections.Generic;
using Autodesk.Revit.DB;
using PushIt.Models;
using RevitUtils;

namespace PushIt.RevitActions
{
    public class RefreshRoomDataWithRevitData:IRevitAction
    {
        private readonly RevitDataModel _revitModel;
        public Models.RevitDataModel RevitModel => _revitModel;

        
        public void Execute(Document doc)
        {
            List<Models.RoomsDataModel> updatedRooms = RefreshRoomData(
                doc, 
                _revitModel._roomsContainer.GetAllRooms(),
                _revitModel.Settings.SupportedCategories
             );
            
            if (updatedRooms != null)
            {
                //clear all rooms
                _revitModel.ClearRooms();
                // add updated rooms
                foreach (var rooms in updatedRooms)
                {
                    _revitModel.AddRoom(rooms);
                }
            }
        }

        /// <summary>
        /// Refresh the rooms data model with the rooms from the revit model
        /// </summary>
        /// <param name="doc"></param>
        /// <param name="roomsDataModel"></param>
        /// <param name="supportedCategoryName"></param>
        /// <returns></returns>
        public static List<Models.RoomsDataModel> RefreshRoomData(Document doc, List<Models.RoomsDataModel> roomsDataModel, List<string> supportedCategoryName)
        {
            // check if all shared parameters exist and are bound to the correct categories
            bool parameterCheck = Utilities.Revit.SharedParameters.sharedParametersCheck(doc, roomsDataModel, supportedCategoryName);
            
            // if not get out
            if (!parameterCheck){
                return null;
            }

            // get supported categories
            List<Category> categories = RevitUtils.CategoryUtils.GetMainCategoriesByName(doc, supportedCategoryName);
            if (categories.Count == 0)
            {
                return null;
            }

            // conver revit categories into revit builtIncategories for filtering
            List<BuiltInCategory> familyInstanceFilterCategories = CategoryUtils.GetBuiltInCategoriesFromCategories(categories);

            //get families of supported built in categories
            List<FamilyInstance> familyInstances = RevitUtils.Families.GetFamilyInstancesByBuiltInCategories(doc, familyInstanceFilterCategories);

            // convert family instances to revit rooms
            List < PushIt.Models.RoomsRevit > revitRooms = Utilities.Revit.RevitRoomObjectsConverter.ConvertFamiliesToRevitRooms(familyInstances, roomsDataModel[0]);


            // get the documents current design set and option
            (string designSetName, string designOptionName) = Utilities.Revit.DesignSetAndOptionUtils.GetActiveDesignSetAndOptionName(doc);

            // update rooms data model with revit rooms
            roomsDataModel = Utilities.UpdateRoomDataModelWithRoomsRevitModelUtils.UpdateRoomDataModelWithRoomsRevitModel(
                 roomsDataModel: roomsDataModel,
                 roomsRevit: revitRooms,
                 revitModelActiveDesignSetName: designSetName,
                 revitModelActiveDesignOptionName: designOptionName);

            return roomsDataModel;
        }


        public RefreshRoomDataWithRevitData(RevitDataModel revitModel)
        {
            _revitModel = revitModel;
        }
    }
}
