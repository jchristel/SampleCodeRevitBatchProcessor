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

using duHastNet.DocManager.Revit.Models.Database;
using duHastNet.DocManager.Revit.Models.Revit;

namespace duHastNet.DocManager.Revit.ViewModels
{
    /// <summary>
    /// ViewModel for the Sheets panel.
    /// Displays Revit sheets and supports importing them into the Document Manager database
    /// or updating existing document names from Revit sheet names.
    /// </summary>
    /// <remarks>
    /// Stub implementation — full sheet import and update logic to be added in a future step.
    /// </remarks>
    public partial class SheetsPanelViewModel : AppViewModelBase
    {
        #region Private Fields

        private readonly RevitDataModel _revitDataModel;
        private readonly DatabaseDataModel _databaseDataModel;
        private readonly duHastNet.Utils.WPF.Stores.MessageStore _messageStore;

        #endregion Private Fields

        #region Constructor

        /// <summary>
        /// Initializes a new instance of <see cref="SheetsPanelViewModel"/>.
        /// </summary>
        /// <param name="revitDataModel">Revit data collected before the window opened. Must not be null.</param>
        /// <param name="databaseDataModel">Database data model whose collections are observed directly. Must not be null.</param>
        /// <param name="messageStore">Message store for surfacing errors and status to the UI banner. Must not be null.</param>
        /// <exception cref="ArgumentNullException">
        /// Thrown when any parameter is null.
        /// </exception>
        public SheetsPanelViewModel(
            RevitDataModel revitDataModel,
            DatabaseDataModel databaseDataModel,
            duHastNet.Utils.WPF.Stores.MessageStore messageStore)
        {
            _revitDataModel = revitDataModel ?? throw new ArgumentNullException(nameof(revitDataModel));
            _databaseDataModel = databaseDataModel ?? throw new ArgumentNullException(nameof(databaseDataModel));
            _messageStore = messageStore ?? throw new ArgumentNullException(nameof(messageStore));
        }

        #endregion Constructor

        #region Events

        /// <summary>
        /// Raised after a successful database write operation to signal that
        /// <see cref="RevitIntegrationViewModel"/> should reload the database collections.
        /// </summary>
        public event EventHandler? RefreshRequested;

        /// <summary>
        /// Raises <see cref="RefreshRequested"/>.
        /// Call this from a command after a successful write to the database.
        /// </summary>
        protected void OnRefreshRequested()
        {
            RefreshRequested?.Invoke(this, EventArgs.Empty);
        }

        #endregion Events
    }
}
