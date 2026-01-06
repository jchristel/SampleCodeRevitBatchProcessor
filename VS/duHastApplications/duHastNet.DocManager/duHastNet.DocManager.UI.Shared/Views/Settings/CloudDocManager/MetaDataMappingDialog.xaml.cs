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

using duHastNet.DocManager.UI.Shared.ViewModels;
using duHastNet.DocManager.UI.Shared.ViewModels.Settings.CloudDocManager.CloudProviderControls;
using System.ComponentModel;
using System.Windows;

namespace duHastNet.DocManager.UI.Shared.Views.Settings.CloudDocManager
{
    /// <summary>
    /// Interaction logic for MetaDataMappingDialog.xaml
    /// Dialog for adding or editing metadata field mappings
    /// </summary>
    public partial class MetaDataMappingDialog : Window
    {
        /// <summary>
        /// Gets the ViewModel for this dialog
        /// </summary>
        public MetaDataMappingDialogViewModel ViewModel { get; }

        /// <summary>
        /// Constructor for the dialog
        /// </summary>
        /// <param name="viewModel">The ViewModel instance</param>
        public MetaDataMappingDialog(MetaDataMappingDialogViewModel viewModel)
        {
            InitializeComponent();

            ViewModel = viewModel ?? throw new ArgumentNullException(nameof(viewModel));
            DataContext = ViewModel;

            // Subscribe to ViewModel property changes to detect when OK completes
            ViewModel.PropertyChanged += OnViewModelPropertyChanged;

            // Subscribe to RequestClose event for Cancel button
            ViewModel.RequestClose += OnRequestClose;
        }

        /// <summary>
        /// Handles when ViewModel requests the window to close (Cancel button)
        /// </summary>
        private void OnRequestClose(object? sender, EventArgs e)
        {
            DialogResult = false;
            Close();
        }

        /// <summary>
        /// Handles ViewModel property changes to detect when OK command creates a mapping
        /// </summary>
        private void OnViewModelPropertyChanged(object? sender, PropertyChangedEventArgs e)
        {
            // When CreatedMapping is set (not null), OK command succeeded
            if (e.PropertyName == nameof(ViewModel.CreatedMapping) && ViewModel.CreatedMapping != null)
            {
                DialogResult = true;
                Close();
            }
        }

        /// <summary>
        /// Override to handle Cancel button or X button
        /// </summary>
        protected override void OnClosing(CancelEventArgs e)
        {
            // Unsubscribe from events
            ViewModel.PropertyChanged -= OnViewModelPropertyChanged;
            ViewModel.RequestClose -= OnRequestClose;

            // If closing without OK (DialogResult not set), ensure it's false
            if (DialogResult != true)
            {
                DialogResult = false;
            }

            base.OnClosing(e);
        }
    }
}