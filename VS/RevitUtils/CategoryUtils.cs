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
