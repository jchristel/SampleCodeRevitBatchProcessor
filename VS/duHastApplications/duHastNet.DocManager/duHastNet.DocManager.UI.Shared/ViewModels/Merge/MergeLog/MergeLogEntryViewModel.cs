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
using duHastNet.DocManager.Core.Models.CurrentFolder;
using duHastNet.DocManager.Core.Stores;
using System.Collections.ObjectModel;
using System.IO;
using System.Linq;

namespace duHastNet.DocManager.UI.Shared.ViewModels.Merge.MergeLog
{
    /// <summary>
    /// ViewModel representing a single document entry in the merge log
    /// Contains the document path and all its process messages
    /// </summary>
    public partial class MergeLogEntryViewModel : ObservableObject
    {
        #region Observable Properties

        /// <summary>
        /// The full file path of the document
        /// </summary>
        [ObservableProperty]
        private string _documentPath = string.Empty;

        /// <summary>
        /// The file name only (extracted from path)
        /// </summary>
        [ObservableProperty]
        private string _documentFileName = string.Empty;

        /// <summary>
        /// Collection of process messages for this document
        /// </summary>
        [ObservableProperty]
        private ObservableCollection<ProcessMessageViewModel> _messages = [];

        #endregion

        #region Computed Properties

        /// <summary>
        /// Gets whether this document has any error messages
        /// </summary>
        public bool HasErrors => Messages.Any(m => m.IsError);

        /// <summary>
        /// Gets whether this document has any information messages
        /// </summary>
        public bool HasInformation => Messages.Any(m => m.IsInformation);

        /// <summary>
        /// Gets the count of error messages
        /// </summary>
        public int ErrorCount => Messages.Count(m => m.IsError);

        /// <summary>
        /// Gets the count of information messages
        /// </summary>
        public int InformationCount => Messages.Count(m => m.IsInformation);

        /// <summary>
        /// Gets the bullet character for the document header
        /// </summary>
        public string DocumentBullet => "●";

        #endregion

        #region Constructor

        /// <summary>
        /// Default constructor
        /// </summary>
        public MergeLogEntryViewModel()
        {
        }

        /// <summary>
        /// Creates a MergeLogEntryViewModel from an IncomingDocumentProcessingStatus
        /// </summary>
        /// <param name="status">The processing status containing the document and messages</param>
        public MergeLogEntryViewModel(IncomingDocumentProcessingStatus status)
        {
            DocumentPath = status.NewDocumentPath ?? string.Empty;
            DocumentFileName = Path.GetFileName(DocumentPath);

            // Convert process messages to ViewModels
            foreach (var (message, messageType, _) in status.ProcessMessages)
            {
                Messages.Add(new ProcessMessageViewModel(message, messageType));
            }
        }

        #endregion
    }
}
