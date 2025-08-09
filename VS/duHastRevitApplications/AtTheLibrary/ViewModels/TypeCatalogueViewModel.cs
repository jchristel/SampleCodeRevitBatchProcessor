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

using System;
using System.Collections.Generic;

namespace duHastNet.AtTheLibrary.ViewModels
{
    public class TypeCatalogueViewModel : Utils.WPF.ViewModels.ViewModelBase
    {
        private Models.RevitFamiliesDataModel RevitDataModel { get; set; }

        /// <summary>
        /// the family of which to display the catalogue file
        /// </summary>
        private Models.FamilyDataModel SelectedFamily { get; set; }


        /// <summary>
        /// Dictionary containing custom default values for specific columns
        /// </summary>
        private Dictionary<string, Func<TypeCatalogueViewModel, object>> _columnDefaults;

        /// <summary>
        /// Dictionary containing custom default values for specific columns
        /// </summary>
        public Dictionary<string, Func<TypeCatalogueViewModel, object>> ColumnDefaults
        {
            get => _columnDefaults;
        }

        /// <summary>
        /// maps column ids to display names
        /// </summary>
        private Dictionary<string, string> _columnIdToParameterNameLookUp;
        public Dictionary<string, string> ColumnIdToParameterNameLookUp
        {
            get => _columnIdToParameterNameLookUp;
        }

        /// <summary>
        /// As read from type catalogue file
        /// </summary>
        private List<string> _catalogueFileHeadersOriginal;
        private List<List<string>> _catalogueFileDataOriginal;



        public TypeCatalogueViewModel(Models.RevitFamiliesDataModel revitDataModel, Models.FamilyDataModel selectedFamily, ViewModels.FamiliesSelectionViewModel familiesSelectionViewModel)
        {
            // Base constructor will call InitializeAvailableColumns()
            // and set up all the commands

            this.RevitDataModel = revitDataModel;
            this.SelectedFamily = selectedFamily;

            // read catalogue file
            (_catalogueFileHeadersOriginal, _catalogueFileDataOriginal) = Utilities.Revit.TypeCatalogueFileUtils.GetCatalogueFileData(selectedFamily.FamilyFilePath.Value , familiesSelectionViewModel);

            //check for null values indicating falure to read
            if (_catalogueFileDataOriginal == null || _catalogueFileHeadersOriginal == null)
            {
                return;
            }
        }
    }
}
