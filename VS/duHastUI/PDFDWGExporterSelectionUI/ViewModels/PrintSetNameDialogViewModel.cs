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


using duHastNet.UI.PDFDWGExporterSelectionUI.Commands;
using duHastNet.Utils.WPF.Commands;
using duHastNet.Utils.WPF.ViewModels;
using System;
using System.Collections;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Windows.Input;

namespace duHastNet.UI.PDFDWGExporterSelectionUI.ViewModels
{
    public class PrintSetNameDialogViewModel : ViewModelBase, INotifyDataErrorInfo
    {

        private string _printSetName;

        /// <summary>
        /// Represents a collection of unique names that are used to track existing entries.
        /// </summary>
        /// <remarks>This field is intended for internal use to ensure that names are not
        /// duplicated.</remarks>
        private readonly HashSet<string> _existingNames;

        /// <summary>
        /// contains the dialog result
        /// </summary> 
        private bool _dialogResult;

        /// <summary>
        /// errors view model used for data validation ( export directory )
        /// </summary>
        private readonly duHastNet.Utils.WPF.ViewModels.ErrorsViewModel _errorsViewModel;


        #region data validation

        /// <summary>
        /// Indicates whether the print set name is valid
        /// </summary>
        private bool _printSetNameValid;
        public bool PrintSetNameValid
        {
            get => _printSetNameValid;
            set
            {
                _printSetNameValid = value;
                // call ui update
                OnPropertyChanged(nameof(PrintSetNameValid));
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

            // Trigger the command to re-evaluate its CanExecute state
            if (CreateCommand != null)
            {
                ((RelayCommand)CreateCommand).RaiseCanExecuteChanged();
            }
        }


        /// <summary>
        /// Validates the current print set name and updates the validation state.
        /// </summary>
        /// <remarks>This method checks the print set name for the following conditions: <list
        /// type="bullet"> <item><description>It must not be null, empty, or consist only of
        /// whitespace.</description></item> <item><description>It must not exceed 100 characters in
        /// length.</description></item> <item><description>It must not duplicate an existing print set
        /// name.</description></item> </list> If any of these conditions are violated, an appropriate error message is
        /// added to the  <see cref="_errorsViewModel"/> for the <c>PrintSetName</c> property, and the
        /// <c>PrintSetNameValid</c>  property is set to <see langword="false"/>. Otherwise, the name is considered
        /// valid, and  <c>PrintSetNameValid</c> is set to <see langword="true"/>.</remarks>
        private void ValidatePrintSetName()
        {

            var name = _printSetName?.Trim();

            // Clear previous errors
            _errorsViewModel.ClearErrors(nameof(PrintSetName));

            // Check if empty or null
            if (string.IsNullOrWhiteSpace(name))
            {
                // Add error
                _errorsViewModel.AddError(nameof(PrintSetName), "Print set name cannot be empty.");

                // set the print set name to invalid
                PrintSetNameValid = false;

                return;
            }
            
            // Check if name already exists
            if (_existingNames.Contains(name))
            {
                // Add error
                _errorsViewModel.AddError(nameof(PrintSetName), "A print set with this name already exists.");

                // set the print set name to invalid
                PrintSetNameValid = false;

                return;
            }

            // Check length (optional)
            if (name.Length > 100)
            {
                // Add error
                _errorsViewModel.AddError(nameof(PrintSetName), "Print set name is too long (maximum 100 characters).");

                // set the print set name to invalid
                PrintSetNameValid = false;

                return;
            }

            if(name.IndexOfAny(System.IO.Path.GetInvalidFileNameChars()) >= 0)
            {
                // Add error
                _errorsViewModel.AddError(nameof(PrintSetName), "Print set name contains invalid characters.");
                // set the print set name to invalid
                PrintSetNameValid = false;
                return;
            }

            //ok all good
            PrintSetNameValid = true;
            // this will trigger data validation
            // from the eventhandler ErrorsViewModel_ErrorsChanged
            _errorsViewModel.ClearErrors(nameof(PrintSetName));
            
        }

        #endregion

        /// <summary>
        /// Gets or sets the name of the print set.
        /// </summary>
        /// <remarks>Setting this property triggers validation of the print set name and raises a property
        /// change notification. Additionally, it updates the execution state of the associated create
        /// command.</remarks>
        public string PrintSetName
        {
            get => _printSetName;
            set
            {
                _printSetName = value;
                OnPropertyChanged(nameof(PrintSetName));
                ValidatePrintSetName();

                // Notify that CanExecute may have changed
                ((RelayCommand)CreateCommand).RaiseCanExecuteChanged();
            }
        }

        /// <summary>
        /// The dialog result indicating whether the operation was successful.
        /// </summary>
        public bool DialogResult
        {
            get => _dialogResult;
            private set
            {
                _dialogResult = value;
                OnPropertyChanged(nameof(DialogResult));
            }
        }

        #region commands

        public ICommand CreateCommand { get; }
        public ICommand CancelCommand { get; }

        #endregion

        // INotifyDataErrorInfo implementation
        public bool HasErrors => _errorsViewModel.HasErrors;

        // event handler for errors changed
        public event EventHandler<DataErrorsChangedEventArgs> ErrorsChanged
        {
            add { _errorsViewModel.ErrorsChanged += value; }
            remove { _errorsViewModel.ErrorsChanged -= value; }
        }

        
        /// <summary>
        /// Check if the create command can be executed
        /// </summary>
        /// <param name="parameter"></param>
        /// <returns></returns>
        private bool CanExecuteCreate(object parameter)
        {
          return !HasErrors && !string.IsNullOrWhiteSpace(_printSetName);
        }

        /// <summary>
        /// Executes the create operation if the specified parameter satisfies the conditions for execution.
        /// </summary>
        /// <remarks>This method checks whether the operation can be executed by calling <see
        /// cref="CanExecuteCreate"/>  with the provided parameter. If the conditions are met, it sets the <see
        /// cref="DialogResult"/> to <see langword="true"/>.</remarks>
        /// <param name="parameter">An object representing the parameter to evaluate before executing the operation.</param>
        private void ExecuteCreate(object parameter)
        {
            if (CanExecuteCreate(parameter))
            {
                DialogResult = true;
            }
        }

        /// <summary>
        /// Execute the cancel operation
        /// </summary>
        private void ExecuteCancel(object parameter)
        {
            DialogResult = false;
        }

        /// <summary>
        /// Class constructor
        /// </summary>
        public PrintSetNameDialogViewModel(string defaultName, IEnumerable<string> existingNames)
        {
            _existingNames = new HashSet<string>(existingNames ?? Enumerable.Empty<string>(), StringComparer.OrdinalIgnoreCase);
            _printSetName = defaultName ?? string.Empty;

            //initialize the errors view model
            _errorsViewModel = new duHastNet.Utils.WPF.ViewModels.ErrorsViewModel();
            //subscribe to errors changed event
            _errorsViewModel.ErrorsChanged += ErrorsViewModel_ErrorsChanged;

            CreateCommand = new RelayCommand(ExecuteCreate, CanExecuteCreate);
            CancelCommand = new RelayCommand(ExecuteCancel);

            // Validate initial value
            ValidatePrintSetName();
        }
    }
}