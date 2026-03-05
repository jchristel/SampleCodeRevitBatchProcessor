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
    /// Mirrors <c>DrofusDataSourceControlViewModel</c> — receives the live
    /// <see cref="DataSourceSettings"/> reference and writes directly to
    /// <see cref="DataSourceSettings.CsvConfig"/> on every change, so CSV
    /// settings survive a provider type switch without requiring an external
    /// <c>SaveToSettings</c> / <c>LoadFromConfig</c> round-trip.
    /// </para>
    /// </summary>
    public partial class CsvDataSourceControlViewModel : ObservableValidator
    {
        #region Private Fields

        /// <summary>
        /// The live settings object shared with the rest of the application.
        /// Written to directly whenever <see cref="FilePath"/> changes so that
        /// CSV config is always in sync without an external save call.
        /// </summary>
        private readonly DataSourceSettings _settings;

        #endregion

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

            // Write through to the live settings object so CSV config is always
            // persisted regardless of whether SaveToSettings is called explicitly.
            _settings.CsvConfig ??= new CsvDataSourceConfig();
            _settings.CsvConfig.FilePath = value;
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

        #region Constructor

        /// <summary>
        /// Creates the ViewModel and pre-populates <see cref="FilePath"/> from
        /// any existing <see cref="CsvDataSourceConfig"/> already present in
        /// <paramref name="settings"/>, mirroring the pattern used by
        /// <see cref="DrofusDataSourceControlViewModel"/>.
        /// </summary>
        /// <param name="settings">
        /// The live <see cref="DataSourceSettings"/> from the application model.
        /// Must not be null.
        /// </param>
        public CsvDataSourceControlViewModel(DataSourceSettings settings)
        {
            _settings = settings ?? throw new System.ArgumentNullException(nameof(settings));

            // Pre-populate from any previously saved config so switching back to
            // CSV after selecting another provider restores the last-used path.
            if (_settings.CsvConfig != null)
                FilePath = _settings.CsvConfig.FilePath ?? string.Empty;

            // Run initial validation so HasErrors is correct from the start
            ValidateAllProperties();
        }

        #endregion
    }
}
