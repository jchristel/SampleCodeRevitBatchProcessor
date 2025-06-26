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

using System;
using System.Collections.Generic;

namespace duHastNet.UI.CustomControls.CustomDataGrid
{
    public class AvailableColumnDefinition
    {
        public string PropertyName { get; set; }
        public string DisplayName { get; set; }
        public Type DataType { get; set; }
        public string Category { get; set; }
        public string Description { get; set; }

        public ColumnUIType UIType { get; set; }
        public List<object> DropDownValues { get; set; }


        public AvailableColumnDefinition(
            string propertyName, 
            string displayName, 
            Type dataType, 
            string category = "General", 
            string description = "",
            ColumnUIType uiType = ColumnUIType.Standard, 
            List<object> dropDownValues = null)
        {
            PropertyName = propertyName;
            DisplayName = displayName;
            DataType = dataType;
            Category = category;
            Description = description;

            UIType = uiType;
            DropDownValues = dropDownValues ?? new List<object>();
        }

        public string TypeDisplayName
        {
            get
            {
                switch (DataType.Name)
                {
                    case "String":
                        return "Text";
                    case "Int32":
                        return "Number";
                    case "Double":
                        return "Decimal";
                    case "Boolean":
                        return "Yes/No";
                    case "DateTime":
                        return "Date";
                    default:
                        return DataType.Name;
                }
            }
        }
    }
}
