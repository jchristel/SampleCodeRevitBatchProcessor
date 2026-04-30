//
//License:
//
//
// Revit Batch Processor Sample Code
//
// BSD License
// Copyright 2026, Jan Christel
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

using duHastNet.DocManager.Revit.ViewModels;
using System.Windows;

namespace duHastNet.DocManager.Revit.Views
{
    /// <summary>
    /// Modal window that allows the user to assign red (not-in-database) Revit sheet rows to
    /// existing database documents whose number has changed.
    /// <para>
    /// Follows the same pattern as <see cref="SheetCustomPropertiesWindow"/>: the ViewModel is
    /// passed into the constructor, <see cref="UpdateExistingDocumentViewModel.RequestClose"/>
    /// drives the window close, and <see cref="Window.DialogResult"/> is set from
    /// <see cref="UpdateExistingDocumentViewModel.DialogConfirmed"/>.
    /// </para>
    /// </summary>
    public partial class UpdateExistingDocumentWindow : Window
    {
        /// <summary>
        /// Parameterless constructor required by XAML infrastructure.
        /// </summary>
        public UpdateExistingDocumentWindow()
        {
            InitializeComponent();
        }

        /// <summary>
        /// Constructs the window with the given ViewModel and wires the close event.
        /// </summary>
        /// <param name="viewModel">The ViewModel to bind. Must not be null.</param>
        /// <exception cref="ArgumentNullException">
        /// Thrown when <paramref name="viewModel"/> is null.
        /// </exception>
        public UpdateExistingDocumentWindow(UpdateExistingDocumentViewModel viewModel) : this()
        {
            _ = viewModel ?? throw new ArgumentNullException(nameof(viewModel));

            DataContext = viewModel;

            viewModel.RequestClose += (sender, e) =>
            {
                DialogResult = viewModel.DialogConfirmed;
                Close();
            };
        }
    }
}
