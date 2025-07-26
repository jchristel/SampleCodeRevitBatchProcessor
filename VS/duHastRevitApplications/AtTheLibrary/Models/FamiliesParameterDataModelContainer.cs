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

        public void AddParameter(Models.FamilyDataProperty parameter, List<string> supportedParameterNames)
        {
            if (!_parameterNames.Contains(parameter.Name))
            {
                _parameterNames.Add(parameter.Name);

                // convert family data property to parameter data property for UI
                var parameterDataProperty = new Models.ParameterDataProperty(
                    name: parameter.Name,
                    showInUI: supportedParameterNames.Contains(parameter.Name),
                    occurenceCount: 0);

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

        public List<string> GetAllParameterNames()
        {
            return _parameterNames;
        }

        public List<Models.ParameterDataProperty> GetParameterDataProperties()
        {
            return _parameterProperties;
        }

        public void ClearParameters()
        {
            _parameterProperties.Clear();
            _parameterNames.Clear();
        }

        public FamiliesParameterDataModelContainer()
        {
            _parameterNames = new List<string>();
            _parameterProperties = new List<ParameterDataProperty>();
        }
    }
}
