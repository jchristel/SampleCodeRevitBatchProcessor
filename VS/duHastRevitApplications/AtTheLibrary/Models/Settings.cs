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
    public class Settings
    {
        // path to the data file containing the family in library data
        public string DataPath { get; set; }

        // list of enabled Revit type parameter names ( this is a list of pre-selected parameters which can be shown in the UI )
        public List<string> EnabledTypeParameterNames { get; set; }

        // list of shown Revit type parameter names ( this is a list of parameters are actually shown in the main ui )
        public List<string> ShownTypeParameterNames { get; set; }

        /// <summary>
        /// field containing all the column ids (room properties) to be displayed in the ui at start up
        /// and id is the same as the property name but without any spaces!
        /// </summary>
        private List<string> _columnIds;

        public List<string> ColumnIds
        {
            get => _columnIds;
        }

        /// <summary>
        /// states of the navigation controls (e.g. DataGrid) in the UI
        /// </summary>
        private Dictionary<string, string> _navigationStates;

        // <summary>
        /// Stores the serialized DataGrid state (columns, filters, sorting, etc.)
        /// This allows the grid layout to be preserved between sessions
        /// </summary>
        public Dictionary<string, string> NavigationStates
        {
            get => _navigationStates;
            set => _navigationStates = value;
        }

        public Settings()
        {
            EnabledTypeParameterNames = new List<string>();
            ShownTypeParameterNames = new List<string>();
            _columnIds = new List<string>();
            DataPath = string.Empty;
            _navigationStates = new Dictionary<string, string>();
        }
    }
}
