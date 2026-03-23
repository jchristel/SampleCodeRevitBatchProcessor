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

using duHastNet.DocManager.Revit.Utilities.RevitData;
using System.ComponentModel;

namespace duHastNet.DocManager.Revit.Models.Revit
{
    public class RevitDataModel : INotifyPropertyChanged
    {
        private RevitSheetContainer _revitSheetContainer;
        private RevitRevisionContainer _revitRevisionContainer;

        private duHastNet.Utils.Logging.SimpleLogger _logger;

        public string ModelName { get; private set; }

        public string SettingsAsJson { get; private set; }

        // ── Startup messages ──────────────────────────────────────────────────

        /// <summary>
        /// Durable record of messages generated during the startup sequence
        /// (settings validation, parameter load, room load). Written by Revit
        /// actions and startup helpers; read by <c>Main.ExecuteInternal</c> to
        /// forward entries to the UI message store once the window is visible.
        /// <para>
        /// This list is never serialised. It is runtime-only and is cleared at
        /// the start of each startup or manual reload sequence via
        /// <see cref="ClearStartupMessages"/>.
        /// </para>
        /// </summary>
        private readonly List<(string Message, duHastNet.Utils.WPF.Stores.MessageTypes Type)> _startupMessages
            = new List<(string, duHastNet.Utils.WPF.Stores.MessageTypes)>();

        /// <summary>
        /// Appends a message to the startup message list.
        /// Called by Revit actions and startup helpers during the startup sequence.
        /// </summary>
        public void AddStartupMessage(string message, duHastNet.Utils.WPF.Stores.MessageTypes type)
        {
            _startupMessages.Add((message, type));
        }

        /// <summary>
        /// Clears all previously recorded startup messages.
        /// Call this at the beginning of any startup or reload sequence so that
        /// stale messages from a prior run are not re-surfaced.
        /// </summary>
        public void ClearStartupMessages()
        {
            _startupMessages.Clear();
        }

        /// <summary>
        /// Returns a read-only view of the startup messages accumulated so far.
        /// </summary>
        public IReadOnlyList<(string Message, duHastNet.Utils.WPF.Stores.MessageTypes Type)> GetStartupMessages()
        {
            return _startupMessages.AsReadOnly();
        }

        // ── logging ──────────────────────────────────────────────────
        public void InitialiseLogger(string filePath)
        {
            _logger = new duHastNet.Utils.Logging.SimpleLogger(filePath);
        }

        public void LogMessages(List<(string, duHastNet.Utils.WPF.Stores.MessageTypes)> messages)
        {
            if (_logger == null) return;

            _logger.LogMessagesFireAndForget(messages);
        }

        // ── INotifyPropertyChanged implementation ────────────────────────────────────────────────────

        public event PropertyChangedEventHandler PropertyChanged;

        protected void OnPropertyChanged(string propertyName)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }

        public void RaisePropertyChanged(string name)
        {
            OnPropertyChanged(name);
        }


        public RevitDataModel(string modelName, string settingsAsJson="")
        {
            ModelName = modelName;
            SettingsAsJson = settingsAsJson;
            _revitSheetContainer = new RevitSheetContainer();
            _revitRevisionContainer = new RevitRevisionContainer();
        }

        public void AddSheet(RevitSheet sheet)
        {
            _revitSheetContainer.AddSheet(sheet);
        }

        public void AddRevision(RevitRevision revision)
        {
            _revitRevisionContainer.AddRevision(revision);
        }

        public RevitRevision GetRevisionByRevitElementId(Int64 revisionId)
        {
            return _revitRevisionContainer.GetRevisionByRevitId(revisionId);
        }
    }
}
