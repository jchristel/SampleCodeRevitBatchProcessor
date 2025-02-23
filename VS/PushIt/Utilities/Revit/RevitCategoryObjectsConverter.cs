using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Autodesk.Revit.DB;

namespace duHast.PushIt.Utilities.Revit
{
    public static class RevitCategoryObjectsConverter
    {
        public static List<string> SupportedRevitCategories = new List<string>
        {
            "Ceilings",
            "Columns",
            "Mass",
            "Walls",
        };

        public static List<Models.CategoryDataModel> ConvertToRevitCategoryObjects(Document doc)
        {
            List<Models.CategoryDataModel> revitCategoryObjects = new List<Models.CategoryDataModel>();
            List<Category> revitCategories = RevitUtils.CategoryUtils.GetMainCategoriesInModel(doc);
            
            foreach (var revitCategory in revitCategories)
            {
                if (SupportedRevitCategories.Contains(revitCategory.Name))
                {
                    Models.CategoryDataModel categoryDataModel = new Models.CategoryDataModel(revitCategory.Name);
                    revitCategoryObjects.Add(categoryDataModel);
                }
            }
            return revitCategoryObjects;
        }
    }
}
