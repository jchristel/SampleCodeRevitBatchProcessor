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

using duHastNet.UI.PDFDWGExporterSelectionUI.Models;
using duHastNet.UI.PDFDWGExporterSelectionUI.Views;
using duHastNet.Utils.WPF.Stores;
using System.Collections.Generic;

namespace duHastNet.UI.PDFDWGExporterSelectionUI
{
    public class Main
    {

        readonly duHastNet.Utils.WPF.Stores.MessageStore _messageStore;
        readonly duHastNet.Utils.WPF.Stores.NavigationStore _navigationStore;
        readonly Models.SheetsDataModel _exportSheetsDataModel;
        readonly Utils.Settings _settings;


        public Main(
            List<RevitSheet> sheetsInModel,
            List<RevitPrintSet> printSetsInModel,
            List<RevitSchedule> schedulesInModel,
            string currentPDFExportString,
            string currentDWGExportString,
            List<string> parameterNames)

        {

            // do some sanity checking before proceeding:
            // do we have any sheets?
            if (sheetsInModel == null || sheetsInModel.Count == 0)
            { throw new System.Exception("No sheets supplied."); }

            // any sheet parameters?
            if (parameterNames == null || parameterNames.Count == 0)
            { throw new System.Exception("No sheet parameters supplied"); }

            // any export strings?
            if (string.IsNullOrEmpty(currentDWGExportString) && string.IsNullOrEmpty(currentPDFExportString))
            {
                throw new System.Exception("Neither a pdf export setting nor a dwg export setting was supplied.");
            }

            //set up stores
            _navigationStore = new NavigationStore();
            _messageStore = new MessageStore();

            //set up a setting object
            //load settings from file is done in the view model
            _settings = new Utils.Settings();

            //set up the export data model
            _exportSheetsDataModel = new Models.SheetsDataModel(
                settings: _settings,
                revitSheets: sheetsInModel,
                revitPrintSets: printSetsInModel,
                revitSchedules: schedulesInModel,
                currentPDFExportString: currentPDFExportString,
                currentDWGExportString: currentDWGExportString,
                parameterNames: parameterNames);
        }


        /// <summary>
        /// Function which will display the document selection window and return the selected sheets to the caller
        /// </summary>
        public duHastNet.UI.PDFDWGExporterSelectionUI.Utils.ExportSelection Execute()
        {

            //create the settings view model
            var settingsViewModel = CreateDocumentSelectionViewModel();

            //set the current view model to the settings view model
            _navigationStore.CurrentViewModel = settingsViewModel;

            //show the main window
            MainWindow mainWindow = new(_settings)
            {
                DataContext = new ViewModels.MainWindowViewModel(_navigationStore)
            };

            mainWindow.ShowDialog();

            var exportSelection = new Utils.ExportSelection();

            // return the selected sheets...
            List<int> sheetIdsSelected = [];

            foreach (var sheet in this._exportSheetsDataModel.RevitSheets)
            {
                if (sheet.IsSelected)
                {
                    sheetIdsSelected.Add(int.Parse(sheet.RevitElementId.Value));
                }
            }

            exportSelection.SheetIdsToExport = sheetIdsSelected;
            exportSelection.ExportDirectoryPath = _exportSheetsDataModel.Settings.ExportFolderPath;
            exportSelection.ExportModus = _exportSheetsDataModel.Settings.ExportModus;
            return exportSelection;
        }

        /// <summary>
        /// Creates the document selection view model.
        /// </summary>
        /// <returns></returns>
        private ViewModels.DocumentSelectionViewModel CreateDocumentSelectionViewModel()
        {
            duHastNet.Utils.WPF.ViewModels.GlobalMessageViewModel _globalMessageViewModel = new(_messageStore);

            return new ViewModels.DocumentSelectionViewModel(
                _exportSheetsDataModel,
                _navigationStore,
                _globalMessageViewModel,
                _messageStore);
        }

    }
}
