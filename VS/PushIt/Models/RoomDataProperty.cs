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



namespace duHast.PushIt.Models
{
    public class RoomDataProperty:Utilities.IRoomProperty
    {
        private string _name;
        private string _parameterGUID;
        private string _parameterName;
        private string _value;
        private bool _showInUI;
        private bool _isReadOnly;

        public string Value { get => _value; set => _value = value; }
        public string Name { get => _name; }
        public string ParameterGUID { get => _parameterGUID; }
        public string ParameterName { get => _parameterName; }
        public bool ShowInUI { get => _showInUI; }
        public bool IsReadOnly { get => _isReadOnly; }


        public RoomDataProperty(string name, string parameterGUID, string parameterName, string value, bool showInUI, bool isReadOnly)
        {
            _name = name;
            _parameterGUID = parameterGUID;
            _parameterName = parameterName;
            _value = value;
            _showInUI = showInUI;
            _isReadOnly = isReadOnly;
        }

    }
}
