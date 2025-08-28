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
using System.Windows.Markup;


namespace duHastNet.UI.PDFDWGExporterSelectionUI.Commands
{
    public class PrintSetUpdateCommand : duHastNet.Utils.WPF.Commands.CommandBase
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
                // set the status of the print set to be deleted
                string printSetToUpdate = _documentSelectionViewModel.SelectedPrintSet;

                foreach (var printSet in _revitSheetsDataModel.PrintSets)
                {
                    if (printSet.Name == printSetToUpdate)
                    {
                        // mark the print set for update
                        printSet.UpdateAction = PrintSetUpdateType.Update;

                        //wipe all sheets from the print set
                        printSet.RevitSheets.Clear();

                        //add the selected sheets to the print set
                        for (int i = 0; i < _revitSheetsDataModel.RevitSheets.Count; i++)
                        {
                            if (_revitSheetsDataModel.RevitSheets[i].IsSelected)
                            {
                                printSet.RevitSheets.Add(_revitSheetsDataModel.RevitSheets[i]);
                            }
                        }
                    }
                }

                // raise event to notify the view model that the model has been updated
                _revitSheetsDataModel.RaisePropertyChanged(Utils.PropertyChangedEventNames.DATA_MODEL_PRINTSETS_UPDATED);

                // inform user
                _documentSelectionViewModel.AddMessage(
                    $"Print set '{printSetToUpdate}' marked for update. Save settings to apply.",
                    duHastNet.Utils.WPF.Stores.MessageTypes.Information
                );
            }
            catch (System.Exception ex)
            {
                _documentSelectionViewModel.AddMessage(
                    $"Error during print set update: {ex.Message}",
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
            if (_documentSelectionViewModel.SelectedPrintSet==Constants.DefaultPrintSetName)
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


        public PrintSetUpdateCommand(
            ViewModels.DocumentSelectionViewModel documentSelectionViewModel,
            Models.SheetsDataModel revitSheetsDataModel)
        {
            _documentSelectionViewModel = documentSelectionViewModel;
            _revitSheetsDataModel = revitSheetsDataModel;


            _documentSelectionViewModel.PropertyChanged += OnViewModelPropertyChanged;
        }
    }
}
