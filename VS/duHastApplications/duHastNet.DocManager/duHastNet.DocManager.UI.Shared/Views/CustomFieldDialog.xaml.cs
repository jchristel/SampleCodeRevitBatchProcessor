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
using System.Windows;

namespace duHastNet.DocManager.UI.Shared.Views
{
    /// <summary>
    /// Interaction logic for CustomFieldDialog.xaml
    /// </summary>
    public partial class CustomFieldDialog : Window
    {
        public CustomFieldDialog(CustomFieldDialogViewModel viewModel)
        {
            InitializeComponent();
            DataContext = viewModel;

            // Subscribe to RequestClose event from ViewModel
            viewModel.RequestClose += OnViewModelRequestClose;
        }

        /// <summary>
        /// Handles the RequestClose event from the ViewModel
        /// Sets DialogResult based on whether a field name was created
        /// </summary>
        private void OnViewModelRequestClose(object? sender, EventArgs e)
        {
            if (sender is CustomFieldDialogViewModel viewModel)
            {
                // OK was clicked if CreatedFieldName has a value
                DialogResult = !string.IsNullOrEmpty(viewModel.CreatedFieldName);
            }
            else
            {
                // Cancel was clicked
                DialogResult = false;
            }

            Close();
        }
    }
}
