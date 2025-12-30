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
using duHastNet.DocManager.Core.Models.CurrentFolder;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;

namespace duHastNet.DocManager.UI.Shared.ViewModels.Merge.MergeLog
{
    /// <summary>
    /// ViewModel for the Merge Log Dialog
    /// Displays process messages for all documents processed during a merge operation
    /// </summary>
    public partial class MergeLogDialogViewModel : ObservableObject
    {
        #region Observable Properties

        /// <summary>
        /// Collection of log entries, one per document
        /// </summary>
        [ObservableProperty]
        private ObservableCollection<MergeLogEntryViewModel> _logEntries = [];

        /// <summary>
        /// Dialog title
        /// </summary>
        [ObservableProperty]
        private string _dialogTitle = "Merge Log";

        #endregion

        #region Computed Properties

        /// <summary>
        /// Gets the total number of documents processed
        /// </summary>
        public int TotalDocuments => LogEntries.Count;

        /// <summary>
        /// Gets the number of documents with errors
        /// </summary>
        public int DocumentsWithErrors => LogEntries.Count(e => e.HasErrors);

        /// <summary>
        /// Gets the number of documents without errors
        /// </summary>
        public int DocumentsSuccessful => LogEntries.Count(e => !e.HasErrors);

        /// <summary>
        /// Gets whether any documents had errors
        /// </summary>
        public bool HasAnyErrors => DocumentsWithErrors > 0;

        /// <summary>
        /// Gets the summary message for display
        /// </summary>
        public string SummaryMessage
        {
            get
            {
                if (TotalDocuments == 0)
                    return "No documents were processed.";

                if (DocumentsWithErrors == 0)
                    return $"All {TotalDocuments} document(s) processed successfully.";

                return $"Processed {TotalDocuments} document(s): {DocumentsSuccessful} successful, {DocumentsWithErrors} with errors.";
            }
        }

        #endregion

        #region Events

        /// <summary>
        /// Event raised when the ViewModel requests the view to close
        /// </summary>
        public event EventHandler? RequestClose;

        #endregion

        #region Constructor

        /// <summary>
        /// Default constructor
        /// </summary>
        public MergeLogDialogViewModel()
        {
        }

        /// <summary>
        /// Creates a MergeLogDialogViewModel from a list of IncomingDocumentProcessingStatus
        /// </summary>
        /// <param name="processingStatuses">The list of document processing statuses</param>
        public MergeLogDialogViewModel(List<IncomingDocumentProcessingStatus> processingStatuses)
        {
            if (processingStatuses == null || processingStatuses.Count == 0)
            {
                return;
            }

            // Convert each status to a log entry
            foreach (var status in processingStatuses)
            {
                // Only include documents that have messages
                if (status.ProcessMessages.Any())
                {
                    LogEntries.Add(new MergeLogEntryViewModel(status));
                }
            }

            // Update computed properties
            OnPropertyChanged(nameof(TotalDocuments));
            OnPropertyChanged(nameof(DocumentsWithErrors));
            OnPropertyChanged(nameof(DocumentsSuccessful));
            OnPropertyChanged(nameof(HasAnyErrors));
            OnPropertyChanged(nameof(SummaryMessage));
        }

        #endregion

        #region Commands

        /// <summary>
        /// Command to close the dialog (OK button)
        /// </summary>
        [RelayCommand]
        private void Ok()
        {
            RequestClose?.Invoke(this, EventArgs.Empty);
        }

        #endregion
    }
}
