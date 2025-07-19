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

namespace duHastNet.UI.PDFDWGExporterSelectionUI.Utils
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

        /// <summary>
        /// the print set selected by the user. If null none was selected
        /// </summary>
        private string _printSet;

        public string Printset
        {
            get => _printSet;
            set => _printSet = value;
        }

        /// <summary>
        /// the folder to which sheets are going to be exported
        /// </summary>
        private string _exportFolderPath;
        public string ExportFolderPath
        {
            get => _exportFolderPath;
            set => _exportFolderPath = value;
        }

        /// <summary>
        /// which type of documents to export
        /// </summary>
        private string _exportModus;
        public string ExportModus
        {
            get => _exportModus;
            set => _exportModus = value;
        }


        /// <summary>
        /// updates this settings object from another one. If null is past in this will be reset to default values
        /// </summary>
        /// <param name="settings"></param>
        public void UpdateSettingsFromSettings(Settings settings)
        {
            if (settings == null)
            {
                //reset to default
                _columnIds = [];
                _printSet = Models.Constants.DefaultPrintSetName;
                _exportFolderPath = string.Empty;
                _exportModus = Models.Constants.ExportModusPDF;
                return;
            }
            else
            {
                //deep copy of the column names
                _columnIds = [.. settings.ColumnIds];
                _printSet = settings.Printset;
                _exportFolderPath = settings.ExportFolderPath;
                _exportModus = settings.ExportModus;
                return;
            }
        }


        /// <summary>
        /// default constructor
        /// </summary>
        public Settings()
        {
            // set default values
            _columnIds = [];
            _printSet = Models.Constants.DefaultPrintSetName;
            _exportFolderPath = string.Empty;
            _exportModus = Models.Constants.ExportModusPDF;
        }
    }
}
