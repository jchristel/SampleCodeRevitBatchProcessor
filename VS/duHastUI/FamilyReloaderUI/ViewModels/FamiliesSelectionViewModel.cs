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


using duHastNet.Utils.WPF.Stores;
using duHastNet.Utils.WPF.ViewModels;
using System;
using System.Collections;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Windows.Input;

namespace duHastNet.UI.FamilyReloaderUI.ViewModels
{
    public class FamiliesSelectionViewModel : ViewModelBase, INotifyDataErrorInfo
    {
        /// <summary>
        /// Global message view model for displaying messages to the user
        /// </summary>
        public duHastNet.Utils.WPF.ViewModels.GlobalMessageViewModel GlobalMessageViewModel { get; }


        /// <summary>
        /// errors view model used for data validation ( export directory )
        /// </summary>
        private readonly duHastNet.Utils.WPF.ViewModels.ErrorsViewModel _errorsViewModel;


        //property to check if there are any errors
        public bool HasErrors => _errorsViewModel.HasErrors;


        // event handler for errors changed
        public event EventHandler<DataErrorsChangedEventArgs> ErrorsChanged
        {
            add { _errorsViewModel.ErrorsChanged += value; }
            remove { _errorsViewModel.ErrorsChanged -= value; }
        }


        /// <summary>
        /// message store for storing messages
        /// </summary>
        private readonly duHastNet.Utils.WPF.Stores.MessageStore _messageStore;


        /// <summary>
        /// View model managing the view selection data grid.
        /// </summary>
        //public duHastNet.UI.PDFDWGExporterSelectionUI.ViewModels.ViewSelectionDataGridViewModel ViewSelectionDataGridViewModel { get; }


        /// <summary>
        /// The data model for the export settings
        /// </summary>
        private readonly Models.FamiliesDataModel _familiesDataModel;


        /// <summary>
        /// command to save the settings and close the window
        /// </summary>
        private readonly duHastNet.Utils.WPF.Commands.RelayCommand _saveAndCloseCommand;
        public ICommand SaveAndCloseCommand { get { return _saveAndCloseCommand; } }






        /// <summary>
        /// Adds a message to the global message store which will then be displayed in the UI
        /// </summary>
        /// <param name="message"></param>
        /// <param name="messageType"></param>
        public void AddMessage(string message, duHastNet.Utils.WPF.Stores.MessageTypes messageType)
        {
            _messageStore.SetCurrentMessage(message, messageType);
        }


        private void LoadSettings()
        {
            //load settings first
            var settings = duHastNet.UI.FamilyReloaderUI.Utils.SettingsUtils.LoadSettings(AddMessage: AddMessage);

            //cant simply replace the settings object in the data model...since it is used else where....need to update instead
            _familiesDataModel.Settings.UpdateSettingsFromSettings(settings);
        }

        /// <summary>
        /// The file path for the exports to be saved to
        /// </summary>
        private string _selectedLibraryFilePath;

        /// <summary>
        /// property handling file path changes
        /// </summary>
        public string LibraryFilePath
        {
            get => _selectedLibraryFilePath;
            set
            {
                if (_selectedLibraryFilePath != value)
                {
                    _selectedLibraryFilePath = value;


                    _errorsViewModel.ClearErrors(nameof(LibraryFilePath));

                    // check if the file path is valid, if not add an error
                    if (string.IsNullOrEmpty(value))
                    {
                        // set the data path to invalid
                        LibraryDirectoryPathValid = false;
                        // this will trigger data validation
                        // from the eventhandler ErrorsViewModel_ErrorsChanged
                        _errorsViewModel.AddError(nameof(LibraryFilePath), "Library path path cannot be empty");
                    }
                    else if (!System.IO.Directory.Exists(value))
                    {
                        // set the data path to invalid
                        LibraryDirectoryPathValid = false;
                        // this will trigger data validation
                        // from the eventhandler ErrorsViewModel_ErrorsChanged
                        _errorsViewModel.AddError(nameof(LibraryFilePath), "Library path does not exist");
                    }
                    else
                    {
                        // set the data path to valid
                        LibraryDirectoryPathValid = true;
                        // this will trigger data validation
                        // from the eventhandler ErrorsViewModel_ErrorsChanged
                        _errorsViewModel.ClearErrors(nameof(LibraryFilePath));

                        //save in settings
                        _familiesDataModel.Settings.TargetDirectory = value;
                    }


                    OnPropertyChanged(nameof(LibraryFilePath));
                }
            }
        }
        #region data validation

        private bool _libraryDirectoryPathValid;
        public bool LibraryDirectoryPathValid
        {
            get => _libraryDirectoryPathValid;
            set
            {
                _libraryDirectoryPathValid = value;
                // call ui update
                OnPropertyChanged(nameof(LibraryDirectoryPathValid));
            }
        }

        /// <summary>
        /// Data validation for text input fields
        /// </summary>
        /// <param name="propertyName">The name of the property of which to get any errors, if they exist, for.</param>
        /// <returns></returns>
        /// <exception cref="NotImplementedException"></exception>
        public IEnumerable GetErrors(string propertyName)
        {
            return _errorsViewModel.GetErrors(propertyName);
        }


        private void ErrorsViewModel_ErrorsChanged(object sender, DataErrorsChangedEventArgs e)
        {
            // The ErrorsChanged event will be automatically raised through the interface
            OnPropertyChanged(nameof(HasErrors));
            OnPropertyChanged(nameof(LibraryDirectoryPathValid));

            // Trigger the command to re-evaluate its CanExecute state
            if (_saveAndCloseCommand != null)
            {
                _saveAndCloseCommand.RaiseCanExecuteChanged();
            }
        }

        #endregion data validation

        public FamiliesSelectionViewModel(
            Models.FamiliesDataModel familiesDataModel,
            duHastNet.Utils.WPF.ViewModels.GlobalMessageViewModel globalMessageViewModel,
            duHastNet.Utils.WPF.Stores.MessageStore messageStore
            )
        {

            //store the export data model
            _familiesDataModel = familiesDataModel;

            //store the message store
            _messageStore = messageStore;

            //store the global message view model
            GlobalMessageViewModel = globalMessageViewModel;

            // initialize the errors view model
            _errorsViewModel = new duHastNet.Utils.WPF.ViewModels.ErrorsViewModel();
            //subscribe to errors changed event
            _errorsViewModel.ErrorsChanged += ErrorsViewModel_ErrorsChanged;

            //load settings first
            LoadSettings();
        }
    }
}
