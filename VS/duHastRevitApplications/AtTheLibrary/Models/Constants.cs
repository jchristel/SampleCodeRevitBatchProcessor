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

using System.Collections.Generic;

namespace duHastNet.AtTheLibrary.Models
{
    public class Constants
    {
        // column headers in family selection data grid
        public const string ColumnHeaderFamilyId = "Id";
        public const string ColumnHeaderFamilyCount = "Count";
        public const string ColumnHeaderFamilyName = "Family Name";
        public const string ColumnHeaderFamilyCategory = "Family Category";
        public const string ColumnHeaderFamilyTypeName = "Family Type Name";
        public const string ColumnHeaderTypeCatalogueFile = "Has Type Catalogue File";


        public static readonly Dictionary<string, string> ColumnFamiliesInfo = new Dictionary<string, string>
        {
            {ColumnHeaderFamilyId.Replace(" ",""), ColumnHeaderFamilyId},
            {ColumnHeaderFamilyCount.Replace(" ",""), ColumnHeaderFamilyCount},
            {ColumnHeaderFamilyName.Replace(" ",""), ColumnHeaderFamilyName},
            {ColumnHeaderFamilyCategory.Replace(" ",""), ColumnHeaderFamilyCategory},
            {ColumnHeaderFamilyTypeName.Replace(" ",""), ColumnHeaderFamilyTypeName},
            {ColumnHeaderTypeCatalogueFile.Replace(" ",""), ColumnHeaderTypeCatalogueFile},
        };

        // column headers in paramter selection data grid
        public const string ColumnHeaderParameterIsSelected = "Is Selected";
        public const string ColumnHeaderParameterName = "Parameter Name";
        public const string ColumnHeaderParameterOccurenceCount = "Occurence Count";

        public static readonly Dictionary<string, string> ColumnParametersInfo = new Dictionary<string, string>
        {
            {ColumnHeaderParameterIsSelected.Replace(" ",""), ColumnHeaderParameterIsSelected},
            {ColumnHeaderParameterName.Replace(" ",""), ColumnHeaderParameterName},
            {ColumnHeaderParameterOccurenceCount.Replace(" ",""), ColumnHeaderParameterOccurenceCount},
        };
    }
}
