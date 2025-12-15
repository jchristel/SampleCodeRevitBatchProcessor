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
    public class AddToEnd : Interfaces.IDocumentNumberModifier
    {
        /// <summary>
        /// this class adds a suffix to the end of a document number
        /// </summary>
        private string _suffix;

        /// <summary>
        /// The suffix to add to the end of the document number
        /// </summary>
        public string Suffix
        {
            get => _suffix;
            set => _suffix = value ?? string.Empty;
        }

        public string DocumentNumber(string number)
        {
            return number + _suffix;
        }

        public string GetDisplayText()
        {
            if (string.IsNullOrEmpty(_suffix))
                return "Add Suffix: (empty)";
            return $"Add Suffix: {_suffix}";
        }

        /// <summary>
        /// Constructor for creating a new AddToEnd modifier
        /// </summary>
        /// <param name="suffix">The suffix to add</param>
        public AddToEnd(string suffix)
        {
            _suffix = suffix ?? string.Empty;
        }

        /// <summary>
        /// Parameterless constructor for JSON deserialization
        /// </summary>
        [JsonConstructor]
        public AddToEnd()
        {
            _suffix = string.Empty;
        }
    }
}