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
using duHast.RevitUtils.Parameters;
using System.Collections.Generic;

namespace RevitUtils.Parameters
{
    public static class ParaUtils
    {
        /// <summary>
        /// Set the value of a parameter by it's name.
        /// </summary>
        /// <param name="el">The element of which the parameter belongs to.</param>
        /// <param name="parameterName">The parameter name.</param>
        /// <param name="value">The value the parameter is to be set to.</param>
        /// <returns>True if parameter value was set successfully. Otherwise false.</returns>
        public static bool SetParameterValueByName(Element el, string parameterName, string value)
        {
            // set the value
            IList<Parameter> parameters = el.GetOrderedParameters();
            foreach (Parameter parameter in parameters)
            {
                if (parameter.Definition.Name == parameterName)
                {
                    bool setResult =  ParameterSetUtils.SetParameterValue(parameter, value);
                    return setResult;
                }
            }

            return false;
        }

        /// <summary>
        ///  Get the value of a parameter by it's name.
        /// </summary>
        /// <param name="el">The element containing the parameter</param>
        /// <param name="parameterName">The parameter name</param>
        /// <returns>A string containing the parameter value. Null, If  the parameter does not exist on the element.</returns>
        public static string GetParameterValueByName(Element el, string parameterName)
        {
            // get the value
            IList<Parameter> parameters = el.GetOrderedParameters();
            foreach (Parameter parameter in parameters)
            {
                if (parameter.Definition.Name == parameterName)
                {
                    string value = ParameterGetUtils.GetParameterValueAsString(para: parameter);
                    return value;
                }
            }
            return null;
        }
    }
}
