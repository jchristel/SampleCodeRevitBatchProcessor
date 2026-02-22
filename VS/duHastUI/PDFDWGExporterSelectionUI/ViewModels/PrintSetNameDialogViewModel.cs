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

using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using duHastNet.Utils.WPF.ViewModels;
using System;
using System.Collections;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Windows.Input;

namespace duHastNet.UI.PDFDWGExporterSelectionUI.ViewModels
{
    public partial class PrintSetNameDialogViewModel : AppViewModelBase, INotifyDataErrorInfo
    {
        /// <summary>
        /// Represents a collection of unique names used to track existing entries.
        /// </summary>
        private readonly HashSet<string> _existingNames;

        /// <summary>
        /// Errors view model used for data validation.
        /// </summary>
        private readonly ErrorsViewModel _errorsViewModel;

        #region observable properties

        /// <summary>
        /// The name of the print set being created.
        /// Side effects: triggers validation and notifies CreateCommand.CanExecute.
        /// </summary>
        [ObservableProperty]
        private string _printSetName;

        partial void OnPrintSetNameChanged(string value)
        {
            ValidatePrintSetName();
            ((RelayCommand)CreateCommand).NotifyCanExecuteChanged();
        }

        /// <summary>
        /// Indicates whether the print set name is valid.
        /// </summary>
        [ObservableProperty]
        private bool _printSetNameValid;

        /// <summary>
        /// The dialog result indicating whether the operation was successful.
        /// Uses SetProperty with a private setter since [ObservableProperty] only generates public setters.
        /// </summary>
        private bool _dialogResult;
        public bool DialogResult
        {
            get => _dialogResult;
            private set => SetProperty(ref _dialogResult, value);
        }

        #endregion observable properties

        #region data validation

        /// <summary>
        /// Data validation for text input fields.
        /// </summary>
        /// <param name="propertyName">The name of the property to get errors for.</param>
        public IEnumerable GetErrors(string propertyName)
        {
            return _errorsViewModel.GetErrors(propertyName);
        }

        private void ErrorsViewModel_ErrorsChanged(object sender, DataErrorsChangedEventArgs e)
        {
            OnPropertyChanged(nameof(HasErrors));

            // Trigger the command to re-evaluate its CanExecute state
            if (CreateCommand != null)
            {
                ((RelayCommand)CreateCommand).NotifyCanExecuteChanged();
            }
        }

        /// <summary>
        /// Validates the current print set name and updates the validation state.
        /// </summary>
        private void ValidatePrintSetName()
        {
            var name = _printSetName?.Trim();

            // Clear previous errors
            _errorsViewModel.ClearErrors(nameof(PrintSetName));

            // Check if empty or null
            if (string.IsNullOrWhiteSpace(name))
            {
                _errorsViewModel.AddError(nameof(PrintSetName), "Print set name cannot be empty.");
                PrintSetNameValid = false;
                return;
            }

            // Check if name already exists
            if (_existingNames.Contains(name))
            {
                _errorsViewModel.AddError(nameof(PrintSetName), "A print set with this name already exists.");
                PrintSetNameValid = false;
                return;
            }

            // Check length
            if (name.Length > 100)
            {
                _errorsViewModel.AddError(nameof(PrintSetName), "Print set name is too long (maximum 100 characters).");
                PrintSetNameValid = false;
                return;
            }

            if (name.IndexOfAny(System.IO.Path.GetInvalidFileNameChars()) >= 0)
            {
                _errorsViewModel.AddError(nameof(PrintSetName), "Print set name contains invalid characters.");
                PrintSetNameValid = false;
                return;
            }

            // All validation passed
            PrintSetNameValid = true;
            _errorsViewModel.ClearErrors(nameof(PrintSetName));
        }

        #endregion

        // INotifyDataErrorInfo implementation
        public bool HasErrors => _errorsViewModel.HasErrors;

        public event EventHandler<DataErrorsChangedEventArgs> ErrorsChanged
        {
            add { _errorsViewModel.ErrorsChanged += value; }
            remove { _errorsViewModel.ErrorsChanged -= value; }
        }

        #region commands

        public ICommand CreateCommand { get; }
        public ICommand CancelCommand { get; }

        /// <summary>
        /// Checks if the create command can be executed.
        /// </summary>
        private bool CanExecuteCreate()
        {
            return !HasErrors && !string.IsNullOrWhiteSpace(_printSetName);
        }

        /// <summary>
        /// Executes the create operation if conditions are met.
        /// </summary>
        private void ExecuteCreate()
        {
            if (CanExecuteCreate())
            {
                DialogResult = true;
            }
        }

        /// <summary>
        /// Executes the cancel operation.
        /// </summary>
        private void ExecuteCancel()
        {
            DialogResult = false;
        }

        #endregion

        /// <summary>
        /// Class constructor.
        /// </summary>
        /// <param name="defaultName">The default name to pre-populate the input field.</param>
        /// <param name="existingNames">Collection of names already in use, for duplicate validation.</param>
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

        #region lifecycle methods

        public override void OnClosing()
        {
            base.OnClosing();
        }

        /// <summary>
        /// Disposes managed resources including event subscriptions.
        /// </summary>
        public override void Dispose()
        {
            System.Diagnostics.Debug.WriteLine("PrintSetNameDialogViewModel.Dispose() called");

            if (_errorsViewModel != null)
            {
                _errorsViewModel.ErrorsChanged -= ErrorsViewModel_ErrorsChanged;
            }

            base.Dispose();
        }

        #endregion
    }
}