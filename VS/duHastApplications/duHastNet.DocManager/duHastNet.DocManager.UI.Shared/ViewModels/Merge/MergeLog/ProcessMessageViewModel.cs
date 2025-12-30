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
using duHastNet.DocManager.Core.Stores;
using System.Windows.Media;

namespace duHastNet.DocManager.UI.Shared.ViewModels.Merge.MergeLog
{
    /// <summary>
    /// ViewModel representing a single process message for display in the merge log
    /// </summary>
    public partial class ProcessMessageViewModel : ObservableObject
    {
        #region Observable Properties

        /// <summary>
        /// The message text
        /// </summary>
        [ObservableProperty]
        private string _message = string.Empty;

        /// <summary>
        /// The message type (Error, Information, Log)
        /// </summary>
        [ObservableProperty]
        private ProcessMessageTypes _messageType;

        #endregion

        #region Computed Properties

        /// <summary>
        /// Gets the color to display this message in
        /// Error messages are red, all others are black
        /// </summary>
        public System.Windows.Media.Brush MessageColor => MessageType == ProcessMessageTypes.Error 
            ? System.Windows.Media.Brushes.Red 
            : System.Windows.Media.Brushes.Black;

        /// <summary>
        /// Gets the bullet character for this message
        /// </summary>
        public string MessageBullet => "•";

        /// <summary>
        /// Gets whether this is an error message
        /// </summary>
        public bool IsError => MessageType == ProcessMessageTypes.Error;

        /// <summary>
        /// Gets whether this is an information message
        /// </summary>
        public bool IsInformation => MessageType == ProcessMessageTypes.Information;

        #endregion

        #region Constructor

        /// <summary>
        /// Creates a new ProcessMessageViewModel
        /// </summary>
        /// <param name="message">The message text</param>
        /// <param name="messageType">The message type</param>
        public ProcessMessageViewModel(string message, ProcessMessageTypes messageType)
        {
            Message = message;
            MessageType = messageType;
        }

        #endregion
    }
}
