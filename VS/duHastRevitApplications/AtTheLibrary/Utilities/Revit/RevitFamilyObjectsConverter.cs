using Autodesk.Revit.DB;
using System;
using System.Collections.Generic;

namespace duHastNet.AtTheLibrary.Utilities.Revit
{
    public static class RevitFamilyObjectsConverter
    {
        /// <summary>
        /// Convert a single family to a revit family placeholder
        /// </summary>
        /// <param name="family"></param>
        /// <returns></returns>
        public static List<Models.FamilyRevit> ConvertSingleFamilyToRevitFamily(
            Family family
            )
        {
            // get the family types
            List<FamilySymbol> familyTypes = duHastNet.RevitUtils.Families.FamilyUtils.GetFamilyTypes(family.Document, family);

            if (familyTypes.Count == 0)
            {
                return null;
            }

            List<Models.FamilyRevit> familiesRevit = new List<Models.FamilyRevit>();

            foreach (FamilySymbol familyType in familyTypes)
            {
                // create a unique id for the family
                string famId = duHastNet.Utils.Hash.ComputeHashUtils.ComputeShortSHA256Hash(new string[] { family.Name, family.FamilyCategory.Name, familyType.Name });

                // create a new family revit object
                Models.FamilyRevit familyRevit = new Models.FamilyRevit(
                    id: new Models.FamilyDataProperty(
                        name: nameof(Models.FamilyRevit.Id),
                        value: famId,
                        storageTypeString:"string"),
                    familyName: new Models.FamilyDataProperty(
                        name: nameof(Models.FamilyRevit.FamilyName),
                        value: family.Name,
                        storageTypeString:"string"),
                    familyCategory: new Models.FamilyDataProperty(
                        name: nameof(Models.FamilyRevit.FamilyCategory),
                        value: family.FamilyCategory.Name,
                        storageTypeString:"string"),
                    familyTypeName: new Models.FamilyDataProperty(
                        name: nameof(Models.FamilyRevit.FamilyTypeName),
                        value: familyType.Name,
                        storageTypeString: "string")
                    );

                familiesRevit.Add(familyRevit);
            }

            return familiesRevit;
        }

        /// <summary>
        /// Convert a list of families to revit families placeholders
        /// </summary>
        /// <param name="families">Revit families to be converted into place holders</param>
        /// <param name="AddMessage">A function to add varies types messages to the caller</param>
        public static List<Models.FamilyRevit> ConvertFamiliesToRevitFamilies(
            List<Element> families,
            Action<string, Utils.WPF.Stores.MessageTypes> AddMessage)
        {
            List<Models.FamilyRevit> familiesInModel = new List<Models.FamilyRevit>();

            foreach (Family family in families)
            {
                try
                {
                    List<Models.FamilyRevit> familiesRevit = ConvertSingleFamilyToRevitFamily(family);
                    if (familiesRevit == null)
                    {
                        continue;
                    }
                    familiesInModel.AddRange(familiesRevit);
                }
                catch (Exception ex)
                {
                    AddMessage($"Error converting family to revit family: {ex.Message}", Utils.WPF.Stores.MessageTypes.Error);
                }
            }

            AddMessage($"Converted {familiesInModel.Count} family instances to revit families.", Utils.WPF.Stores.MessageTypes.Log);
            return familiesInModel;
        }
    }
}
