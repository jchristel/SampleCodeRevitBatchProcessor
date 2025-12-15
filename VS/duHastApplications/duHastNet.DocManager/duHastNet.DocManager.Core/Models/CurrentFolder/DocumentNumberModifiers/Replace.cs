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

using Newtonsoft.Json;

namespace duHastNet.DocManager.Core.Models.CurrentFolder.DocumentNumberModifiers
{
    public class Replace : Interfaces.IDocumentNumberModifier
    {
        /// <summary>
        /// this class replaces a given string with a new string in a document number
        /// </summary>
        private string _oldValue;

        private string _newValue;

        /// <summary>
        /// The old value to be replaced in the document number
        /// </summary>
        public string OldValue
        {
            get => _oldValue;
            set => _oldValue = value ?? string.Empty;
        }

        /// <summary>
        /// The new value to replace the old value with
        /// </summary>
        public string NewValue
        {
            get => _newValue;
            set => _newValue = value ?? string.Empty;
        }

        public string DocumentNumber(string number)
        {
            return number.Replace(_oldValue, _newValue);
        }

        public string GetDisplayText()
        {
            var oldDisplay = string.IsNullOrEmpty(_oldValue) ? "(empty)" : _oldValue;
            var newDisplay = string.IsNullOrEmpty(_newValue) ? "(empty)" : _newValue;

            return $"Replace: {oldDisplay} → {newDisplay}";
        }

        /// <summary>
        /// Constructor for creating a new Replace modifier
        /// </summary>
        /// <param name="oldValue">The value to be replaced</param>
        /// <param name="newValue">The value to replace with</param>
        public Replace(string oldValue, string newValue)
        {
            _oldValue = oldValue ?? string.Empty;
            _newValue = newValue ?? string.Empty;
        }

        /// <summary>
        /// Parameterless constructor for JSON deserialization
        /// </summary>
        [JsonConstructor]
        public Replace()
        {
            _oldValue = string.Empty;
            _newValue = string.Empty;
        }
    }
}