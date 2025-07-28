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


namespace duHastNet.UI.FamilyReloaderUI.Models
{
    public class RevitFamily
    {

        /// <summary>
        /// add a is selected for export property
        /// </summary>
        private bool _isSelected = false;
        public bool IsSelected
        {
            get { return _isSelected; }
            set { _isSelected = value; }
        }

        /// <summary>
        /// The revit family name
        /// </summary>
        private string _familyName;
        public string FamilyName
        {
            get => _familyName;
            set => _familyName = value;
        }

        /// <summary>
        /// the revit family category name
        /// </summary>
        private string _familyCategory;
        public string FamilyCategory
        {
            get => _familyCategory;
            set => _familyCategory = value;
        }


        /// <summary>
        /// Flag indicating as to whether family is shared
        /// </summary>
        private bool _isShared;
        public bool IsShared
        {
            get => _isShared;
            set => _isShared = value;
        }


        //toggle indicating whether family has a file match by name
        private Utils.MatchStatus _matchStatus;
        public Utils.MatchStatus MatchStatus
        {
            get => _matchStatus;
            set => _matchStatus = value;
        }


        // the file path of the family if a match is established
        private string _familyFilePath;
        public string FamilyFilePath
        {
            get => _familyFilePath;
            set => _familyFilePath = value;
        }


        //default constructor
        public RevitFamily(string familyName, string familyCategory,  bool isShared)
        {
            _familyName = familyName;
            _familyCategory = familyCategory;
            _isShared = isShared;

            // set no match as the default value
            _matchStatus = Utils.MatchStatus.NoMatch;
        }
    }
}
