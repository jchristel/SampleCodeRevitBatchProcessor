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

using System.Collections.Generic;
using System.Linq;

namespace duHastNet.Utils.Logging
{
    /// <summary>
    /// Base class for logging actions. This class is used to store messages and their types.
    /// </summary>
    public class LogActionsBase
    {
        private List<(string, Utils.WPF.Stores.MessageTypes)> Messages { get; }

        public List<string> GetErrorMessages()
        {
            return [.. Messages.Where(m => m.Item2 == Utils.WPF.Stores.MessageTypes.Error).Select(m => m.Item1)];
        }

        public List<string> GetInformationMessages()
        {
            return [.. Messages.Where(m => m.Item2 == Utils.WPF.Stores.MessageTypes.Information).Select(m => m.Item1)];
        }

        public List<string> GetWarningMessages()
        {
            return [.. Messages.Where(m => m.Item2 == Utils.WPF.Stores.MessageTypes.Warning).Select(m => m.Item1)];
        }

        public List<(string, Utils.WPF.Stores.MessageTypes)> GetLogMessagesAndLogTypes()
        {
            return Messages;
        }

        public void AddMessage(string message, Utils.WPF.Stores.MessageTypes messageType)
        {
            Messages.Add((message, messageType));
        }

        public void ClearMessages()
        {
            Messages.Clear();
        }

        public LogActionsBase()
        {
            Messages = [];
        }
    }
}
