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

namespace duHast.RevitUtils.Parameters
{

    /// <summary>
    /// A collection of utility functions for setting parameter valuies.
    /// </summary>
    public static class ParameterSetUtils
    {
        /// <summary>
        /// Sets a parameter value.
        /// </summary>
        /// <param name="parameter">The parameter to set the value for.</param>
        /// <param name="value">The value to set.</param>
        /// <returns>True if the value was set, otherwise false.</returns>
        public static bool SetParameterValue(Parameter parameter, string value)
        {
            if (parameter.StorageType == StorageType.String)
            {
                parameter.Set(value);
            }
            else if (parameter.StorageType == StorageType.Double)
            {
                // THIS IS THE KEY:  Use SetValueString instead of Set.  Set requires your data to be in//
                //whatever internal units of measure Revit uses. SetValueString expects your value to
                //be in whatever the current DisplayUnitType (units of measure) the document is set to
                //for the UnitType associated with the parameter.
                //
                //So SetValueString is basically how the Revit GUI works.

                parameter.SetValueString(value);
            }
            else if (parameter.StorageType == StorageType.Integer)
            {
                int intValue = 0;
                if (int.TryParse(value, out intValue))
                {
                    parameter.Set(intValue);
                }
            }
            else
            {
                ElementId elementIdValue = new ElementId(int.Parse(value));
                parameter.Set(elementIdValue);
            }
            return true;
        }
    }
}
