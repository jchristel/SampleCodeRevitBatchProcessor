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
using System.Collections.ObjectModel;
using System.ComponentModel;

namespace duHastNet.UI.PDFDWGExporterSelectionUI.Models
{
    public class SheetsDataModel : duHastNet.Utils.WPF.Models.DataModelBase, INotifyPropertyChanged
    {
        /// <summary>
        /// contains the user settings for the UI
        /// </summary>
        private Utils.Settings _settings;
        public Utils.Settings Settings { get => _settings; set => _settings = value; }


        /// <summary>
        /// contains the Revit sheets in the model
        /// </summary>
        private List<Models.RevitSheet> _revitSheets;
        public List<Models.RevitSheet> RevitSheets
        {
            get => _revitSheets;
        }

        /// <summary>
        /// print set from the revit model
        /// </summary>
        private List<Models.RevitPrintSet> _printSets;
        public List<Models.RevitPrintSet> PrintSets
        {
            get => _printSets;
        }

        /// <summary>
        /// schedules from the revit model
        /// </summary>
        private List<Models.RevitSchedule> _schedules;
        public List<Models.RevitSchedule> Schedules
        {
            get => _schedules;
        }

        /// <summary>
        /// json formatted string representing pdf name settings
        /// </summary>
        private string _currentPDFExportString;
        public string CurrentPDFExportString { get => _currentPDFExportString; }

        /// <summary>
        /// jso formatted string representing dwg name settings
        /// </summary>
        private string _currentDWGExportString;
        public string CurrentDWGExportString { get => _currentDWGExportString; }

        /// <summary>
        /// available sheet parameters
        /// </summary>
        private List<string> _parameterNames;
        public List<string> ParameterNames { get => _parameterNames; }

        /// <summary>
        /// pdf settings
        /// </summary>
        private ObservableCollection<PDFDWGExporterUI.Utils.DocumentSetting> _pdfSettings;

        public ObservableCollection<PDFDWGExporterUI.Utils.DocumentSetting> PDFSettings
        { get => _pdfSettings; }

        /// <summary>
        /// dwg settings
        /// </summary>
        private ObservableCollection<PDFDWGExporterUI.Utils.DocumentSetting> _dwgSettings;
        public ObservableCollection<PDFDWGExporterUI.Utils.DocumentSetting> DWGSettings
        { get => _dwgSettings; }

        private void AddPreviewNames()
        {
            // get the pdf name settings
            _pdfSettings = duHastNet.UI.PDFDWGExporterUI.Utils.SettingsStringParser.ParsePdfSettingsString(
                settingsString: CurrentPDFExportString,
                availableParameters: ParameterNames);

            // get the dwg name settings
            _dwgSettings = duHastNet.UI.PDFDWGExporterUI.Utils.SettingsStringParser.ParseDwgSettingsString(
                settingsString: CurrentDWGExportString,
                availableParameters: ParameterNames);

            // update sheets
            foreach (var sheet in RevitSheets)
            {
                // get the pdf name
                sheet.PDFPreviewName = Utils.FileNamePreviewUtils.GetFileName(sheet, _pdfSettings);

                //get the dwg name
                sheet.DWGPreviewName = Utils.FileNamePreviewUtils.GetFileName(sheet, _dwgSettings);
            }
        }


        #region property changed event

        //event handlers for property changed
        public event PropertyChangedEventHandler PropertyChanged;

        protected void OnPropertyChanged(string propertyName)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }

        public void RaisePropertyChanged(string name)
        {
            OnPropertyChanged(name);
        }

        #endregion

        /// <summary>
        /// Constructor for the sheets data model
        /// </summary>
        public SheetsDataModel(
            Utils.Settings settings,
            List<RevitSheet> revitSheets,
            List<RevitPrintSet> revitPrintSets,
            List<RevitSchedule> revitSchedules,
            string currentPDFExportString,
            string currentDWGExportString,
            List<string> parameterNames
            )
        {
            // Initialize the settings object
            _settings = settings;

            //initialise sheets
            _revitSheets = revitSheets;

            //initialise print sets
            _printSets = revitPrintSets;

            //initialise schedules
            _schedules = revitSchedules;

            //initialise exporter file name settings
            _currentPDFExportString = currentPDFExportString;
            _currentDWGExportString = currentDWGExportString;
            _parameterNames = parameterNames;

            //add preview names for pdf and dwg export for each sheet
            AddPreviewNames();
        }
    }
}
