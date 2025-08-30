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
        private readonly HashSet<string> _existingNames;
        private readonly Dictionary<string, List<string>> _errors = new Dictionary<string, List<string>>();
        private bool _dialogResult;

        public PrintSetNameDialogViewModel(string defaultName, IEnumerable<string> existingNames)
        {
            _existingNames = new HashSet<string>(existingNames ?? Enumerable.Empty<string>(), StringComparer.OrdinalIgnoreCase);
            _printSetName = defaultName ?? string.Empty;

            CreateCommand = new RelayCommand(ExecuteCreate, CanExecuteCreate);
            CancelCommand = new RelayCommand(ExecuteCancel);

            // Validate initial value
            ValidatePrintSetName();
        }

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

        public bool DialogResult
        {
            get => _dialogResult;
            private set
            {
                _dialogResult = value;
                OnPropertyChanged(nameof(DialogResult));
            }
        }

        public ICommand CreateCommand { get; }
        public ICommand CancelCommand { get; }

        // INotifyDataErrorInfo implementation
        public bool HasErrors => _errors.Any();

        public event EventHandler<DataErrorsChangedEventArgs> ErrorsChanged;

        public IEnumerable GetErrors(string propertyName)
        {
            return _errors.ContainsKey(propertyName) ? _errors[propertyName] : Enumerable.Empty<string>();
        }

        private void ValidatePrintSetName()
        {
            var errors = new List<string>();
            var name = _printSetName?.Trim();

            // Check if empty or null
            if (string.IsNullOrWhiteSpace(name))
            {
                errors.Add("Print set name cannot be empty.");
            }
            else
            {
                // Check if name already exists
                if (_existingNames.Contains(name))
                {
                    errors.Add("A print set with this name already exists.");
                }

                // Check for invalid characters (optional)
                var invalidChars = System.IO.Path.GetInvalidFileNameChars();
                if (name.IndexOfAny(invalidChars) >= 0)
                {
                    errors.Add("Print set name contains invalid characters.");
                }

                // Check length (optional)
                if (name.Length > 100)
                {
                    errors.Add("Print set name is too long (maximum 100 characters).");
                }
            }

            SetErrors(nameof(PrintSetName), errors);
        }

        private void SetErrors(string propertyName, List<string> errors)
        {
            var hadErrors = _errors.ContainsKey(propertyName);

            if (errors.Any())
            {
                _errors[propertyName] = errors;
            }
            else
            {
                _errors.Remove(propertyName);
            }

            if (hadErrors || errors.Any())
            {
                ErrorsChanged?.Invoke(this, new DataErrorsChangedEventArgs(propertyName));
                OnPropertyChanged(nameof(HasErrors));

                // Notify that CanExecute may have changed due to error state change
                ((RelayCommand)CreateCommand).RaiseCanExecuteChanged();
            }
        }

        private bool CanExecuteCreate(object parameter)
        {
            return !HasErrors && !string.IsNullOrWhiteSpace(_printSetName);
        }

        private void ExecuteCreate(object parameter)
        {
            if (CanExecuteCreate(parameter))
            {
                DialogResult = true;
            }
        }

        private void ExecuteCancel(object parameter)
        {
            DialogResult = false;
        }
    }
}