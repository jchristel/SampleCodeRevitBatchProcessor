using Autodesk.Revit.DB;
using System;
using System.Collections.Generic;

namespace RevitUtils
{
    public static class CategoryUtils
    {

        public static List<BuiltInCategory> GetBuiltInCategoriesByName(Document doc, List<string> categoryNames)
        {
            List<BuiltInCategory> builtInCategories = new List<BuiltInCategory>();
            foreach (string categoryName in categoryNames)
            {
                BuiltInCategory builtInCategory = (BuiltInCategory)Enum.Parse(typeof(BuiltInCategory), categoryName);
                builtInCategories.Add(builtInCategory);
            }
            return builtInCategories;
        }

        public static List<Category> GetMainCategoriesByName(Document doc, List<string> categoryNames)
        {
            List<Category> categories = new List<Category>();
            // get all categories from the model
            Categories categoriesInModel = doc.Settings.Categories;
            
            // find matches
            foreach (Category category in categoriesInModel)
            {
                // get the category name
                string categoryName = category.Name;

                // check if the category name is in the list
                if (categoryNames.Contains(categoryName))
                {
                    categories.Add(category);
                }
            }
            return categories;
        }

        public static List<BuiltInCategory> GetBuiltInCategoriesFromCategories(List<Category> categories)
        {
            List<BuiltInCategory> builtInCategories = new List<BuiltInCategory>();
            foreach (Category category in categories)
            {
                BuiltInCategory builtInCategory = (BuiltInCategory)category.Id.IntegerValue;
                builtInCategories.Add(builtInCategory);
            }
            return builtInCategories;
        }
    }
}
