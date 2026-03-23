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

namespace duHastNet.DocManager.Revit.Utilities.RevitData
{
    /// <summary>
    /// A simple class to represent a document property, with a property name and its value.
    /// </summary>
    public class RevitDocumentProperty
    {
        public string Name { get; set; }
        public string Value { get; set; }
        public RevitDocumentProperty(string name, string value)
        {
            Name = name;
            Value = value;
        }

        /// <summary>
        /// Check for conflict by name only, as there can only be one property with the same name in Revit.
        /// </summary>
        /// <param name="other"></param>
        /// <returns></returns>
        public bool Conflicts(RevitDocumentProperty other)
        {
            return Name == other.Name;
        }

        public override string ToString()
        {
            return $"{Name}: {Value}";
        }
    }
}
