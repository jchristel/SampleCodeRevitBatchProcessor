//
//License:
//
//
// Revit Batch Processor Sample Code
//
// BSD License
// Copyright 2026, Jan Christel
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

using duHastNet.UI.DocManagerSettingsUI.Utils;
using System.Collections.Generic;

namespace duHastNet.UI.DocManagerSettingsUI.Models
{
    public class ExportDataModel : duHastNet.Utils.WPF.Models.DataModelBase
    {
        private Utils.Settings _settings;
        public Settings Settings { get => _settings; set => _settings = value; }

        /// <summary>
        /// properties ( parameters ) available for renaming
        /// </summary>
        public List<string> ParameterNames { get; }

        /// <summary>
        /// The document property options available for selection in the combo box.
        /// Pre-populated with the two standard options. Additional options (e.g. custom
        /// database properties) may be appended via AddDocumentPropertyOption() before
        /// the view model is constructed.
        /// </summary>
        public List<DocumentPropertyOption> DocumentPropertyOptions { get; }

        /// <summary>
        /// Add a parameter name to the list of available parameters
        /// </summary>
        /// <param name="parameterName"> name of the parameter to add</param>
        public void AddParameterName(string parameterName)
        {
            if (!ParameterNames.Contains(parameterName))
                ParameterNames.Add(parameterName);
        }

        /// <summary>
        /// Adds a document property option to the available options list if it is not already present.
        /// </summary>
        /// <param name="option">The document property option to add.</param>
        public void AddDocumentPropertyOption(DocumentPropertyOption option)
        {
            if (option != null && !DocumentPropertyOptions.Any(o => o.Key == option.Key))
                DocumentPropertyOptions.Add(option);
        }

        /// <summary>
        /// Constructor for the export data model
        /// </summary>
        public ExportDataModel()
        {
            // Initialize the settings object
            _settings = new Utils.Settings();

            ParameterNames = [];

            // Initialize the document property options with the two standard options.
            // Document Number is first so index 0 always maps to it.
            // Keys must match the constants in Utils.Constants to ensure consistency
            // with the DocumentProperties dictionary populated on each RevitSheet.
            DocumentPropertyOptions =
            [
                new Utils.DocumentPropertyOption(Utils.Constants.DocumentPropertyKeyDocumentNumber, "Document Number"),
                new Utils.DocumentPropertyOption(Utils.Constants.DocumentPropertyKeyDocumentName,   "Document Name")
            ];
        }
    }
}
