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


using Autodesk.Revit.DB;

namespace duHastNet.RevitUtils.Families
{
    public class FamilyLoadOption : IFamilyLoadOptions
    {

        private bool _overwriteExisting;

        public bool OverwriteExisting
        {
            get { return _overwriteExisting; }
            set { _overwriteExisting = value; }
        }

        private FamilySource _familySource;
        public FamilySource FamilySource
        {
            get { return _familySource; }
            set { _familySource = value; }
        }


        /// <summary>
        /// A method called when the family was found in the target document. (interface method)
        /// </summary>
        /// <param name="familyInUse"></param>
        /// <param name="overwriteFamily"></param>
        /// <returns></returns>
        public bool OnFamilyFound(
            bool familyInUse,
            out bool overwriteFamily)
        {

            // define overwrite behavior
            overwriteFamily = OverwriteExisting;

            //Return true to continue loading the family, false to cancel.
            return true;
        }

        /// <summary>
        /// A method called when the shared family was found in the target document. (interface method)
        /// </summary>
        public bool OnSharedFamilyFound(
            Family sharedFamily,
            bool familyInUse,
            out FamilySource source,
            out bool overwriteParameterValues)
        {
            source = FamilySource;
            overwriteParameterValues = OverwriteExisting;
            //Return true to continue loading the family, false to cancel.
            return true;
        }

        /// <summary>
        /// Constructor for the FamilyLoadOption class.
        /// </summary>
        /// <param name="overWriteExisting"></param>
        /// <param name="familySource"></param>
        public FamilyLoadOption(bool overWriteExisting = true, FamilySource familySource = FamilySource.Project)
        {
            OverwriteExisting = overWriteExisting;
            FamilySource = familySource;
        }
    }
}