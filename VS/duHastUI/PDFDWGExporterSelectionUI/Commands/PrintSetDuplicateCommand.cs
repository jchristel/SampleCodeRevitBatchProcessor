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
using System.ComponentModel;

namespace duHastNet.UI.PDFDWGExporterSelectionUI.Commands
{
    public class PrintSetDuplicateCommand : duHastNet.Utils.WPF.Commands.CommandBase
    {

        private readonly ViewModels.DocumentSelectionViewModel _documentSelectionViewModel;
        private readonly Models.SheetsDataModel _revitSheetsDataModel;


        /// <summary>
        /// sets the print set to be deleted
        /// </summary>
        /// <param name="parameter"></param>
        public override void Execute(object parameter)
        {
            try
            {
                // get the name of the print set to duplicate
                string printSetToDuplicate = _documentSelectionViewModel.SelectedPrintSet;

                // get the default new print set name
                string defaultNewPrintSetName = printSetToDuplicate + "_Copy";

                //get all print set names
                var allPrintSetNames = _revitSheetsDataModel.GetAllPrintSetNames();

                //show the MVVM dialog
                var inputDialog = new Views.PrintSetNameDialog(defaultNewPrintSetName, allPrintSetNames);
                if (inputDialog.ShowDialog() != true)
                {
                    // user cancelled
                    return;
                }

                //get the new name from the dialog
                string newPrintSetName = inputDialog.PrintSetName;

                //create the new print set
                Models.RevitPrintSet newPrintSet = new Models.RevitPrintSet(
                    name: newPrintSetName,
                    updateAction: PrintSetUpdateType.New
                    );

                // apply the same sheets as in the original print set
                var originalPrintSet = _revitSheetsDataModel.GetPrintSetByName (printSetToDuplicate);

                // check if the original print set was found (should never be the case)
                if (originalPrintSet == null)
                {
                    _documentSelectionViewModel.AddMessage(
                        $"Error: Original print set '{printSetToDuplicate}' not found.",
                        duHastNet.Utils.WPF.Stores.MessageTypes.Error
                    );
                    return;
                }

                // copy sheets
                foreach (var sheet in originalPrintSet.RevitSheets)
                {
                    newPrintSet.AddRevitSheet(sheet);
                }

                //add the new print set to the model
                _revitSheetsDataModel.PrintSets.Add(newPrintSet);

                // raise event to notify the view model that the model has been updated
                _revitSheetsDataModel.RaisePropertyChanged(Utils.PropertyChangedEventNames.DATA_MODEL_PRINTSETS_UPDATED);

                _documentSelectionViewModel.SelectedPrintSet = newPrintSetName;

                // inform user
                _documentSelectionViewModel.AddMessage(
                    $"New print set '{newPrintSetName}' created.",
                    duHastNet.Utils.WPF.Stores.MessageTypes.Information
                );
            }
            catch (System.Exception ex)
            {
                _documentSelectionViewModel.AddMessage(
                    $"Error during print set deletion: {ex.Message}",
                    duHastNet.Utils.WPF.Stores.MessageTypes.Error
                );
            }

        }



        /// <summary>
        /// this command is available if the print set is not none
        /// </summary>
        /// <param name="parameter"></param>
        /// <returns></returns>
        public override bool CanExecute(object parameter)
        {
            // check if there are any errors ( there is only one which relateds to a valid library path )
            if (_documentSelectionViewModel.SelectedPrintSet == Constants.DefaultPrintSetName)
            {
                return false;
            }
            return true;
        }

        private void OnViewModelPropertyChanged(object sender, PropertyChangedEventArgs e)
        {
            // check if the property that changed is the one that we are interested in
            if (e.PropertyName == nameof(ViewModels.DocumentSelectionViewModel.SelectedPrintSet))
            {
                OnCanExecutedChanged();
            }
        }
        public PrintSetDuplicateCommand(
            ViewModels.DocumentSelectionViewModel documentSelectionViewModel,
            Models.SheetsDataModel revitSheetsDataModel)
        {
            _documentSelectionViewModel = documentSelectionViewModel;
            _revitSheetsDataModel = revitSheetsDataModel;


            _documentSelectionViewModel.PropertyChanged += OnViewModelPropertyChanged;
        }
    }
}
