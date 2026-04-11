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

using CommunityToolkit.Mvvm.ComponentModel;
using duHastNet.DocManager.Core.Models.Database;
using duHastNet.DocManager.UI.Shared.ViewModels.Settings.Database;
using System.Collections.ObjectModel;

namespace duHastNet.DocManager.Revit.ViewModels
{
    /// <summary>
    /// Represents a single sheet row in the custom-properties entry step of the import flow.
    /// <para>
    /// Exposes the sheet's document number and name for display, and a collection of
    /// <see cref="CustomFieldValueViewModel"/> instances — one per active custom field
    /// definition — that the user fills in before confirming the import.
    /// </para>
    /// </summary>
    public partial class SheetImportRowViewModel : ObservableObject
    {
        #region Properties

        /// <summary>
        /// Gets the built document number for this sheet. Display-only.
        /// </summary>
        public string DocumentNumber { get; }

        /// <summary>
        /// Gets the built document name for this sheet. Display-only.
        /// </summary>
        public string DocumentName { get; }

        /// <summary>
        /// Gets the current revision indicator for this sheet. Display-only.
        /// </summary>
        public string CurrentRevision { get; }

        /// <summary>
        /// Gets the editable custom field values for this sheet, one entry per active
        /// custom field definition.
        /// </summary>
        public ObservableCollection<CustomFieldValueViewModel> CustomFieldValues { get; }

        #endregion Properties

        #region Constructor

        /// <summary>
        /// Initialises a new instance of <see cref="SheetImportRowViewModel"/>.
        /// </summary>
        /// <param name="documentNumber">Built document number. Must not be null or whitespace.</param>
        /// <param name="documentName">Built document name. Must not be null or whitespace.</param>
        /// <param name="currentRevision">Current revision indicator. Must not be null.</param>
        /// <param name="customFieldDefinitions">
        /// Active custom field definitions for which the user must supply values.
        /// Must not be null.
        /// </param>
        /// <exception cref="ArgumentNullException">
        /// Thrown when <paramref name="customFieldDefinitions"/> is null.
        /// </exception>
        /// <exception cref="ArgumentException">
        /// Thrown when <paramref name="documentNumber"/> or <paramref name="documentName"/>
        /// is null or whitespace.
        /// </exception>
        public SheetImportRowViewModel(
            string documentNumber,
            string documentName,
            string currentRevision,
            IEnumerable<CustomFieldDefinition> customFieldDefinitions)
        {
            if (string.IsNullOrWhiteSpace(documentNumber))
                throw new ArgumentException("Document number must not be null or whitespace.", nameof(documentNumber));
            if (string.IsNullOrWhiteSpace(documentName))
                throw new ArgumentException("Document name must not be null or whitespace.", nameof(documentName));
            _ = customFieldDefinitions ?? throw new ArgumentNullException(nameof(customFieldDefinitions));

            DocumentNumber = documentNumber;
            DocumentName = documentName;
            CurrentRevision = currentRevision ?? string.Empty;

            CustomFieldValues = new ObservableCollection<CustomFieldValueViewModel>(
                customFieldDefinitions.Select(d => new CustomFieldValueViewModel(d)));
        }

        #endregion Constructor
    }
}
