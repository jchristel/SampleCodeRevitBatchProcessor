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

namespace duHastNet.DocManager.Core.Models.DocumentNumberModifiers
{
    public class AddAtIndex : Interfaces.IDocumentNumberModifier
    {
        /// <summary>
        /// this class adds a suffix at a particular index to a document number
        /// </summary>
        private string _value;

        private int _index;

        /// <summary>
        /// The value to insert at the specified index
        /// </summary>
        public string Value
        {
            get => _value;
            set => _value = value ?? string.Empty;
        }

        /// <summary>
        /// The index position where the value will be inserted (0 for prefix)
        /// </summary>
        public int Index
        {
            get => _index;
            set => _index = value;
        }

        public string DocumentNumber(string number)
        {
            return number.Insert(_index, _value);
        }

        public string GetDisplayText()
        {
            var displayValue = string.IsNullOrEmpty(_value) ? "(empty)" : _value;

            // Special case: index 0 is a prefix
            if (_index == 0)
                return $"Add Prefix: {displayValue}";

            return $"Add at Index {_index}: {displayValue}";
        }

        /// <summary>
        /// Constructor for creating a new AddAtIndex modifier
        /// </summary>
        /// <param name="value">The value to insert</param>
        /// <param name="index">The index position (0 for prefix)</param>
        public AddAtIndex(string value, int index)
        {
            _value = value ?? string.Empty;
            _index = index;
        }

        /// <summary>
        /// Parameterless constructor for JSON deserialization
        /// </summary>
        [JsonConstructor]
        public AddAtIndex()
        {
            _value = string.Empty;
            _index = 0;
        }
    }
}