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
using System;
using System.Collections.Generic;

namespace duHastNet.RevitUtils.Categories
{
    public static class CategoryUtils
    {
        /// <summary>
        /// Get the built-in categories by name
        /// </summary>
        /// <param name="categoryNames">A list of names idetnifying the built-in categories to be returned</param>
        /// <returns>A list of built in categories. An empty list of no matchin categories where found.</returns>
        public static List<BuiltInCategory> GetBuiltInCategoriesByName(List<string> categoryNames)
        {
            //new list initialise symantics
            List<BuiltInCategory> builtInCategories = [];
            foreach (string categoryName in categoryNames)
            {
                BuiltInCategory builtInCategory = (BuiltInCategory)Enum.Parse(typeof(BuiltInCategory), categoryName);
                builtInCategories.Add(builtInCategory);
            }
            return builtInCategories;
        }

        /// <summary>
        /// Get the main built-in categories in the model.
        /// </summary>
        /// <param name="doc">The current model document</param>
        /// <returns>A list containing all main categories.</returns>
        public static List<Category>GetMainCategoriesInModel(Document doc)
        {
            //new list initialise symantics
            List<Category> categories = [];
            Autodesk.Revit.DB.Categories categoriesInModel = doc.Settings.Categories;
            foreach (Category category in categoriesInModel)
            {
                categories.Add(category);
            }
            return categories;
        }

        /// <summary>
        /// Returns all mian categories where the name matches the given list of names.
        /// </summary>
        /// <param name="doc">The current model document</param>
        /// <param name="categoryNames">A list of category names</param>
        /// <returns>A list of categories. An empty list if no matching categories were found.</returns>
        public static List<Category> GetMainCategoriesByName(Document doc, List<string> categoryNames)
        {
            //new list initialise symantics
            List<Category> categories = [];
            // get all categories from the model
            Autodesk.Revit.DB.Categories categoriesInModel = doc.Settings.Categories;
            
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

        /// <summary>
        /// Returns all built-incategories matching the past in categories.
        /// </summary>
        /// <param name="categories">List of categories of which to return the built in categories.</param>
        /// <returns>A list of built in categoreis.</returns>
        public static List<BuiltInCategory> GetBuiltInCategoriesFromCategories(List<Category> categories)
        {
            //new list initialise symantics
            List<BuiltInCategory> builtInCategories = [];
            foreach (Category category in categories)
            {
                BuiltInCategory builtInCategory = (BuiltInCategory)category.Id.Value;
                builtInCategories.Add(builtInCategory);
            }
            return builtInCategories;
        }
    }
}
