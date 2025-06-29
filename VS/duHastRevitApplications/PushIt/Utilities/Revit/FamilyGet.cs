using Autodesk.Revit.DB;
using System;
using System.Collections.Generic;

namespace duHastNet.PushIt.Utilities.Revit
{
    public static class FamilyGet
    {

        /// <summary>
        /// Get families from the model and converts them to RoomRevit instances.
        /// 
        /// This assumes all parameters to be read exist in the model.
        /// </summary>
        /// <param name="doc"></param>
        /// <param name="roomsDataModel"></param>
        /// <param name="supportedCategoryNames"></param>
        /// <param name="AddMessage"></param>
        /// <returns></returns>
        public static List<duHastNet.PushIt.Models.RoomRevit> GetAllSupportedFamilies(
            Document doc,
            Models.RevitDataModel revitDataModel,
            List<string> supportedCategoryNames,
            Action<string, Utils.WPF.Stores.MessageTypes> AddMessage
            )
        {
            
            // get supported categories
            List<Category> categories = duHastNet.RevitUtils.Categories.CategoryUtils.GetMainCategoriesByName(doc, supportedCategoryNames);
            if (categories.Count == 0)
            {
                if (supportedCategoryNames.Count > 0)
                {
                    // build a string of supported categories
                    string supportedCategories = string.Join(", ", supportedCategoryNames);
                    AddMessage($"Supported categories are invalid: {supportedCategories}", Utils.WPF.Stores.MessageTypes.Error);
                }
                else
                {
                    AddMessage("No supported categories provided.", Utils.WPF.Stores.MessageTypes.Error);
                }
                return null;
            }

            // convert revit categories into revit builtIncategories for filtering
            List<BuiltInCategory> familyInstanceFilterCategories = duHastNet.RevitUtils.Categories.CategoryUtils.GetBuiltInCategoriesFromCategories(categories);

            //get families of supported built in categories
            List<FamilyInstance> familyInstances = duHastNet.RevitUtils.Families.FamilyUtils.GetFamilyInstancesByBuiltInCategories(doc, familyInstanceFilterCategories);

            //check if any families in the model
            if (familyInstances.Count == 0)
            {
                // if that is not the case return the rooms data model unchanged after popping a message to the user
                AddMessage("No rooms found in the model.", Utils.WPF.Stores.MessageTypes.Information);
            }

            // convert family instances to revit rooms
            List<duHastNet.PushIt.Models.RoomRevit> revitRooms = Utilities.Revit.RevitRoomObjectsConverter.ConvertFamiliesToRevitRooms(
                familyInstances,
                revitDataModel.GetAllParameters(),
                AddMessage
            );

            return revitRooms;
        }
    }
}
