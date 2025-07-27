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

// a class containing all unique parameter names from all families

using System.Collections.Generic;
using System.Linq;

namespace duHastNet.AtTheLibrary.Models
{
    public class FamiliesParameterDataModelContainer
    {
        public List<string> _parameterNames;
        public List<ParameterDataProperty> _parameterProperties;


        /// <summary>
        /// Converts a parameter from a family data property to a parameter data property and adds the parameter name and data property to internal lists
        /// </summary>
        /// <param name="parameter"></param>
        /// <param name="enabledParameterNames"></param>
        /// <param name="shownParameterNames"></param>
        public void AddParameter(Models.FamilyDataProperty parameter, List<string> enabledParameterNames, List<string>shownParameterNames)
        {
            if (!_parameterNames.Contains(parameter.Name))
            {
                _parameterNames.Add(parameter.Name);

                // convert family data property to parameter data property for UI
                var parameterDataProperty = new Models.ParameterDataProperty(
                    name: parameter.Name,
                    occurenceCount: 0,
                    shownInUI: shownParameterNames.Contains(parameter.Name),
                    enabledInUI:enabledParameterNames.Contains(parameter.Name)
                 );

                _parameterProperties.Add(parameterDataProperty);
            }
            else
            {
                // increase the occurrence count of the parameter
                var para = _parameterProperties.FirstOrDefault(p => p.Name == parameter.Name);
                if (para != null)
                {
                    para.OccurenceCount++;
                }
            }
        }


        /// <summary>
        /// clears parameter names and property lists
        /// </summary>
        public void ClearParameters()
        {
            _parameterProperties.Clear();
            _parameterNames.Clear();
        }


        /// <summary>
        /// loops over all parameter properties and makes sure that if a parameter is not enabled for the UI
        /// its shown in UI property is also set to false
        /// </summary>
        public void VerifyEnabledVsShownInUI()
        {
            foreach (var parameter in _parameterProperties)
            {
                if (!parameter.EnabledInUI) {parameter.ShowInUI = false;}
            }
        }


        /// <summary>
        /// returns all parameter names of parameters which are enabled for the UI
        /// </summary>
        /// <returns></returns>
        public List<string> GetAllEnabledParameterNames()
        {
            var enabledParameterNames = _parameterProperties
                    .Where(p => p.EnabledInUI)
                    .Select(p => p.Name)
                    .ToList();
            return enabledParameterNames;
        }


        /// <summary>
        /// returns all parameter names of parameters visible in the UI
        /// </summary>
        /// <returns></returns>
        public List<string> GetAllShownParameterNames()
        {
            var shownParameterNames = _parameterProperties
                   .Where(p => p.ShowInUI)
                   .Select(p => p.Name)
                   .ToList();
            return shownParameterNames;
        }


        /// <summary>
        /// Returns a list of unique parameter names which occured in all families.
        /// </summary>
        /// <returns></returns>
        public List<string> GetAllParameterNames()
        {
            return _parameterNames;
        }

        /// <summary>
        /// Returns a list of unique parameter data properties from all families.
        /// </summary>
        /// <returns></returns>
        public List<Models.ParameterDataProperty> GetParameterDataProperties()
        {
            return _parameterProperties;
        }

        
        public FamiliesParameterDataModelContainer()
        {
            _parameterNames = new List<string>();
            _parameterProperties = new List<ParameterDataProperty>();
        }
    }
}
