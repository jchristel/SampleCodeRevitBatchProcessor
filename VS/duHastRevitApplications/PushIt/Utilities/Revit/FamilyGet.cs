using Autodesk.Revit.DB;
using System;
using System.Collections.Generic;

namespace duHastNet.PushIt.Utilities.Revit
{
    public static class FamilyGet
    {

        public static List<duHastNet.PushIt.Models.RoomRevit> GetAllSupportedFamilies(
            Document doc,
            List<Models.RoomDataModel> roomsDataModel,
            List<string> supportedCategoryNames,
            Action<string, Utils.WPF.Stores.MessageTypes> AddMessage
            )
        {
            string refreshMessage = "";
            // check if all shared parameters exist and are bound to the correct categories
            bool parameterCheck = Utilities.Revit.SharedParameters.SharedParametersCheck(
                doc,
                roomsDataModel,
                supportedCategoryNames,
                out refreshMessage);

            // if not get out
            if (!parameterCheck)
            {
                AddMessage(refreshMessage, Utils.WPF.Stores.MessageTypes.Error);
                return null;
            }
            else
            {
                AddMessage("Successfully checked shared parameter mapping in file.", Utils.WPF.Stores.MessageTypes.Log);
            }

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
                roomsDataModel[0],
                AddMessage
            );

            return revitRooms;
        }
    }
}
