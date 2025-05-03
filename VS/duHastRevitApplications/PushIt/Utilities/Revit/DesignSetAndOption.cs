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

namespace duHastNet.PushIt.Utilities.Revit
{
    public static class DesignSetAndOptionUtils
    {

        /// <summary>
        /// returns the active design set and option name
        /// </summary>
        public static (string designSetName, string designOptionName) GetActiveDesignSetAndOptionName(Document doc)
        {
            // get the documents current design set and option
            var activeDesignOption = duHastNet.RevitUtils.DesignSetAndOptions.DesignSetAndOptionsUtils.GetActiveDesignOption(doc);
            var activeDesignSet = duHastNet.RevitUtils.DesignSetAndOptions.DesignSetAndOptionsUtils.GetDesignSetOfActiveDesignOption(doc);
            
            string designSetName = activeDesignSet == null ? duHastNet.RevitUtils.DesignSetAndOptions.DesignSetAndOptionDefaultNames.MAIN_MODEL_DEFAULT_DESIGN_SET_NAME : activeDesignSet.Name;
            string designOptionName = activeDesignOption == null ? duHastNet.RevitUtils.DesignSetAndOptions.DesignSetAndOptionDefaultNames.MAIN_MODEL_DEFAULT_DESIGN_OPTION_NAME : activeDesignOption.Name;

            return (designSetName, designOptionName);
        }
    }
}
