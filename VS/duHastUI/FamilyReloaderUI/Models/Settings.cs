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
using System.Xml.Serialization;
using System.IO;

namespace duHastNet.UI.FamilyReloaderUI.Models
{
    public class Settings
    {
        /// <summary>
        /// field containing all the column ids (sheet properties) to be displayed
        /// and id is the same as the parameter name but without any spaces!
        /// </summary>
        private List<string> _columnIds;

        public List<string> ColumnIds
        {
            get => _columnIds;
        }

        private string _targetDirectory;
        public string TargetDirectory
        {
            get => _targetDirectory;
            set => _targetDirectory = value;
        }

        private bool _includeSubdirectories;
        public bool IncludeSubdirectories
        {
            get => _includeSubdirectories;
            set => _includeSubdirectories = value;
        }


        private bool _loadAllFamilyTypesOnReload = false;
        public bool LoadAllFamilyTypesOnReload
        {
            get => _loadAllFamilyTypesOnReload;
            set => _loadAllFamilyTypesOnReload = value;
        }


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

        /// <summary>
        /// updates this settings object from another one. If null is past in this will be reset to default values
        /// </summary>
        /// <param name="otherSettings"></param>
        public void UpdateSettingsFromSettings(Settings otherSettings)
        {
            if (otherSettings == null)
            {
                //reset to default
                _columnIds = new List<string>();
                _targetDirectory = string.Empty;
                _includeSubdirectories = false;
                _navigationStates = new Dictionary<string, string>();
                return;
            }
            else
            {
                //deep copy of the column names
                _columnIds = new List<string>(otherSettings.ColumnIds);
                _targetDirectory = otherSettings.TargetDirectory;
                _includeSubdirectories = otherSettings.IncludeSubdirectories;
                _navigationStates = new Dictionary<string, string>(otherSettings.NavigationStates);
                return;
            }
        }

        public Settings()
        {
            _includeSubdirectories = false;
            _columnIds = new List<string>();
            _navigationStates = new Dictionary<string, string>();
        }
    }
}
