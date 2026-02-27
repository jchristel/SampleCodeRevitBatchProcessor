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
using duHastNet.PushIt.Models;
using System.ComponentModel.DataAnnotations;
using System.IO;
using System.Windows.Forms;

namespace duHastNet.PushIt.ViewModels.DataSource
{
    /// <summary>
    /// Child control ViewModel for the CSV data source provider.
    /// Holds and validates the file path required by <see cref="CsvDataSourceConfig"/>.
    /// Displayed inside <see cref="DataSourceViewModel.CurrentSourceControlViewModel"/>
    /// when <see cref="DataSourceType.Csv"/> is selected.
    /// <para>
    /// Mirrors <c>AconexMetadataControlViewModel</c> — uses
    /// <see cref="ObservableValidator"/> with <c>[CustomValidation]</c> on the
    /// observable property and calls <see cref="ObservableValidator.ValidateProperty"/>
    /// in the partial changed handler.
    /// </para>
    /// </summary>
    public partial class CsvDataSourceControlViewModel : ObservableValidator
    {
        #region Observable Properties

        /// <summary>
        /// Full path to the CSV file.
        /// Validated on every change via <see cref="ValidateFilePath"/>.
        /// Errors are surfaced through <see cref="ObservableValidator.HasErrors"/>
        /// so <see cref="DataSourceViewModel"/> can aggregate them.
        /// </summary>
        [ObservableProperty]
        [CustomValidation(typeof(CsvDataSourceControlViewModel), nameof(ValidateFilePath))]
        private string _filePath = string.Empty;

        /// <summary>
        /// Convenience flag that reflects whether the current
        /// <see cref="FilePath"/> passes all validation rules.
        /// Can be bound to the Load button's IsEnabled in the view.
        /// </summary>
        [ObservableProperty]
        private bool _filePathValid = false;

        #endregion

        #region Partial Property Callbacks

        partial void OnFilePathChanged(string value)
        {
            // Trigger the [CustomValidation] attribute on FilePath
            ValidateProperty(value, nameof(FilePath));

            // Keep the convenience flag in sync
            FilePathValid = !HasErrors;
        }

        #endregion

        #region Validation

        /// <summary>
        /// Static validation method referenced by the
        /// <c>[CustomValidation]</c> attribute on <see cref="FilePath"/>.
        /// Mirrors the pattern in <c>AconexMetadataControlViewModel.ValidateTemplateFilePath</c>.
        /// </summary>
        public static ValidationResult? ValidateFilePath(string? value, ValidationContext context)
        {
            if (string.IsNullOrWhiteSpace(value))
                return new ValidationResult("A CSV file path is required.");

            if (!File.Exists(value))
                return new ValidationResult("The specified file does not exist.");

            if (!value.TrimEnd().EndsWith(".csv", System.StringComparison.OrdinalIgnoreCase))
                return new ValidationResult("The file must be a .csv file.");

            return ValidationResult.Success;
        }

        /// <summary>
        /// Validates all properties and returns whether the ViewModel is valid.
        /// </summary>
        public bool IsValid()
        {
            ValidateAllProperties();
            return !HasErrors;
        }

        #endregion

        #region Commands

        /// <summary>
        /// Opens a file-picker dialog filtered to *.csv and sets
        /// <see cref="FilePath"/> with the chosen path.
        /// </summary>
        [RelayCommand]
        private void Browse()
        {
            using var dialog = new OpenFileDialog
            {
                Title = "Select Schedule of Accommodation CSV file",
                Filter = "CSV files (*.csv)|*.csv|All files (*.*)|*.*",
                FilterIndex = 1,
                CheckFileExists = true
            };

            if (!string.IsNullOrWhiteSpace(FilePath) && File.Exists(FilePath))
            {
                dialog.InitialDirectory = Path.GetDirectoryName(FilePath);
                dialog.FileName = Path.GetFileName(FilePath);
            }

            if (dialog.ShowDialog() == DialogResult.OK)
            {
                FilePath = dialog.FileName;
            }
        }

        #endregion

        #region Settings Round-trip

        /// <summary>
        /// Populates this ViewModel from an existing
        /// <see cref="CsvDataSourceConfig"/> on startup or when settings are loaded.
        /// </summary>
        public void LoadFromConfig(CsvDataSourceConfig config)
        {
            if (config == null) return;

            // Setting FilePath triggers OnFilePathChanged → ValidateProperty
            FilePath = config.FilePath ?? string.Empty;
        }

        /// <summary>
        /// Writes the current ViewModel state back into the provided
        /// <see cref="DataSourceSettings"/>. Called by
        /// <see cref="DataSourceViewModel.SaveToSettings"/> before serialisation.
        /// </summary>
        public void SaveToSettings(DataSourceSettings target)
        {
            if (target == null) return;

            target.SourceType = DataSourceType.Csv;
            target.CsvConfig = new CsvDataSourceConfig
            {
                FilePath = FilePath ?? string.Empty
            };
        }

        #endregion

        #region Constructor

        public CsvDataSourceControlViewModel()
        {
            // Run initial validation so HasErrors is correct from the start
            ValidateAllProperties();
        }

        #endregion
    }
}
