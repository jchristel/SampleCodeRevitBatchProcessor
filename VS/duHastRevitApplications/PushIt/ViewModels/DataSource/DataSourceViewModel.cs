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
using duHastNet.PushIt.Models;
using duHastNet.Utils.WPF.Interfaces;
using System;
using System.Collections.ObjectModel;
using System.ComponentModel;

namespace duHastNet.PushIt.ViewModels.DataSource
{
    /// <summary>
    /// Host ViewModel for the data source configuration UI.
    /// Owns the provider-type dropdown and dynamically creates and swaps the
    /// provider-specific child control ViewModel when the selection changes.
    /// <para>
    /// This is the direct equivalent of <c>CloudDocumentManagerViewModel</c> in
    /// the DocManager namespace. <see cref="RoomsMainViewModel"/> consumes it in
    /// the same way that <c>SettingsViewModel</c> consumes
    /// <c>CloudDocumentManagerViewModel</c> — subscribing to
    /// <see cref="ObservableObject.PropertyChanged"/> and forwarding
    /// <see cref="HasValidationErrors"/> changes up the chain.
    /// </para>
    /// <para>
    /// Implements <see cref="ICloseable"/> so it can be registered with
    /// <c>ViewModelBase.RegisterChild</c> and have <see cref="OnClosing"/>
    /// called automatically when <see cref="RoomsMainViewModel"/> closes.
    /// </para>
    /// </summary>
    public partial class DataSourceViewModel : ObservableValidator, ICloseable
    {
        #region Private Fields

        /// <summary>
        /// The live settings object shared with the rest of the application.
        /// Passed into child control ViewModels so they can read and write their
        /// provider-specific config directly (e.g. DrofusDataSourceSettings).
        /// </summary>
        private readonly DataSourceSettings _settings;

        #endregion

        #region Observable Properties

        /// <summary>
        /// Currently selected data source provider type.
        /// Changing this value creates a new child control ViewModel and discards
        /// the previous one.
        /// </summary>
        [ObservableProperty]
        private DataSourceType _selectedSourceType = DataSourceType.None;

        /// <summary>
        /// The provider-specific configuration control ViewModel.
        /// Null when <see cref="SelectedSourceType"/> is
        /// <see cref="DataSourceType.None"/>.
        /// Bound to a <c>ContentControl</c> in the view; the correct XAML
        /// <c>DataTemplate</c> is selected automatically by type.
        /// </summary>
        [ObservableProperty]
        private ObservableObject? _currentSourceControlViewModel;

        /// <summary>
        /// The list of provider types shown in the dropdown.
        /// Add entries here as new providers are introduced.
        /// </summary>
        public ObservableCollection<DataSourceType> AvailableSourceTypes { get; }

        #endregion

        #region Validation Aggregation

        /// <summary>
        /// Returns <c>true</c> when the current configuration is incomplete or
        /// invalid, preventing data from being loaded.
        /// <para>
        /// Rules:
        /// <list type="bullet">
        ///   <item>No provider selected (<see cref="SelectedSourceType"/> == None)</item>
        ///   <item>Child control ViewModel is null (should not occur in practice)</item>
        ///   <item>Child control ViewModel reports validation errors</item>
        /// </list>
        /// </para>
        /// Consumed by <see cref="RoomsMainViewModel"/> to gate the Load command
        /// and surface errors in the UI.
        /// </summary>
        public bool HasValidationErrors
        {
            get
            {
                if (SelectedSourceType == DataSourceType.None)
                    return true;

                if (CurrentSourceControlViewModel == null)
                    return true;

                if (CurrentSourceControlViewModel is ObservableValidator childValidator)
                    return childValidator.HasErrors;

                return false;
            }
        }

        #endregion

        #region Partial Property Callbacks

        partial void OnSelectedSourceTypeChanged(DataSourceType value)
        {
            // Unsubscribe from the previous child to avoid memory leaks
            UnsubscribeFromChildErrors();

            // Create the appropriate child ViewModel for the selected type
            CurrentSourceControlViewModel = value switch
            {
                DataSourceType.None => null,
                DataSourceType.Csv => new CsvDataSourceControlViewModel(_settings),
                DataSourceType.Drofus => new DrofusDataSourceControlViewModel(_settings),
                _ => throw new ArgumentException($"Unknown source type: {value}")
            };

            // Subscribe to the new child's error notifications
            SubscribeToChildErrors();

            // Notify parent that validation state may have changed
            OnPropertyChanged(nameof(HasValidationErrors));
        }

        partial void OnCurrentSourceControlViewModelChanged(ObservableObject? value)
        {
            OnPropertyChanged(nameof(HasValidationErrors));
        }

        #endregion

        #region Child Error Subscription

        private void SubscribeToChildErrors()
        {
            if (CurrentSourceControlViewModel is ObservableValidator childValidator)
            {
                childValidator.ErrorsChanged += OnChildErrorsChanged;
            }
        }

        private void UnsubscribeFromChildErrors()
        {
            if (CurrentSourceControlViewModel is ObservableValidator childValidator)
            {
                childValidator.ErrorsChanged -= OnChildErrorsChanged;
            }
        }

        private void OnChildErrorsChanged(object? sender, DataErrorsChangedEventArgs e)
        {
            // Propagate child error state changes to the parent via PropertyChanged
            // so RoomsMainViewModel can re-evaluate its own HasErrors / CanExecute
            OnPropertyChanged(nameof(HasValidationErrors));
        }

        #endregion

        #region ICloseable

        /// <summary>
        /// Called by <see cref="RoomsMainViewModel.OnClosing"/> via the
        /// <c>RegisterChild</c> mechanism. Unsubscribes from the current child's
        /// error events to prevent memory leaks after the window closes.
        /// </summary>
        public void OnClosing()
        {
            UnsubscribeFromChildErrors();
        }

        #endregion

        #region Settings Round-trip

        /// <summary>
        /// Loads state from a <see cref="DataSourceSettings"/> object.
        /// Called during startup to restore the previously saved configuration.
        /// Setting <see cref="SelectedSourceType"/> triggers
        /// <see cref="OnSelectedSourceTypeChanged"/> which creates the child
        /// ViewModel; <see cref="LoadFromSettings"/> then populates it.
        /// </summary>
        /// <param name="settings">The settings to load. Safe to call with null.</param>
        public void LoadFromSettings(DataSourceSettings settings)
        {
            if (settings == null) return;

            // Setting the type triggers child creation via OnSelectedSourceTypeChanged.
            // Both CsvDataSourceControlViewModel and DrofusDataSourceControlViewModel
            // now receive _settings in their constructors and self-populate, so no
            // additional call is needed here for either provider.
            SelectedSourceType = settings.SourceType;
        }

        /// <summary>
        /// Writes the current ViewModel state back into a
        /// <see cref="DataSourceSettings"/> object ready for serialisation.
        /// Called by <see cref="RoomsMainViewModel"/> before saving settings or
        /// reloading data.
        /// </summary>
        /// <param name="target">The settings object to populate.</param>
        public void SaveToSettings(DataSourceSettings target)
        {
            if (target == null) return;

            target.SourceType = SelectedSourceType;

            // DrofusDataSourceControlViewModel writes back to _settings.Drofus
            // directly; call SaveToSettings() here only to flush any in-flight
            // mapper state (e.g. newly added mappings) before serialisation.
            if (CurrentSourceControlViewModel is DrofusDataSourceControlViewModel drofusVm)
                drofusVm.SaveToSettings();

            // CsvDataSourceControlViewModel writes through to _settings.CsvConfig
            // on every FilePath change, so no explicit flush is required here.
        }

        #endregion

        #region Constructor

        /// <summary>
        /// Creates the host ViewModel.
        /// </summary>
        /// <param name="settings">
        /// The live <see cref="DataSourceSettings"/> from the application model.
        /// Must not be null — <see cref="SettingsUtils.LoadSettings"/> guarantees
        /// this. Passed into provider child ViewModels that need direct access to
        /// their config (e.g. <see cref="DrofusDataSourceControlViewModel"/>).
        /// </param>
        public DataSourceViewModel(DataSourceSettings settings)
        {
            _settings = settings ?? throw new ArgumentNullException(nameof(settings));

            AvailableSourceTypes = new ObservableCollection<DataSourceType>
            {
                DataSourceType.Csv,
                DataSourceType.Drofus,
            };
        }

        #endregion
    }
}