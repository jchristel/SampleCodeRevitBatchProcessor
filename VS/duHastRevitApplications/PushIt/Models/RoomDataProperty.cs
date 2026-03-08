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



namespace duHastNet.PushIt.Models
{
    public class RoomDataProperty(
        string name,
        string parameterGUID,
        string parameterName,
        string value,
        bool showInUI,
        bool isReadOnly,
        bool isUniqueId,
        bool revitTakesPrecedenceAfterInitialPush = false) : Utilities.IRoomProperty
    {
        private readonly string _name = name;
        private readonly string _parameterGUID = parameterGUID;
        private readonly string _parameterName = parameterName;
        private string _value = value;
        private readonly bool _showInUI = showInUI;
        private readonly bool _isReadOnly = isReadOnly;
        private readonly bool _isUniqueId = isUniqueId;
        private readonly bool _revitTakesPrecedenceAfterInitialPush = revitTakesPrecedenceAfterInitialPush;

        public string Value { get => _value; set => _value = value; }
        public string Name { get => _name; }
        public string ParameterGUID { get => _parameterGUID; }
        public string ParameterName { get => _parameterName; }
        public bool ShowInUI { get => _showInUI; }
        public bool IsReadOnly { get => _isReadOnly; }
        public bool IsUniqueId { get => _isUniqueId; }

        /// <summary>
        /// When true, the data source value is written only on the first push to a split room.
        /// On all subsequent pushes the value read back from Revit takes precedence,
        /// preserving any changes made directly in Revit (e.g. a user-edited area).
        /// Defaults to false. Must not be combined with IsReadOnly = true.
        /// </summary>
        public bool RevitTakesPrecedenceAfterInitialPush { get => _revitTakesPrecedenceAfterInitialPush; }
    }
}
