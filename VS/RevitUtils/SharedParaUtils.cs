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

using System;
using System.Collections.Generic;
using Autodesk.Revit.DB;

namespace RevitUtils
{
    public static class SharedParaUtils
    {

        public static List<SharedParameterElement> GetSharedParameters(Document doc)
        {
            List<SharedParameterElement> parameters = new List<SharedParameterElement>();
            FilteredElementCollector collector = new FilteredElementCollector(doc);
            collector.OfClass(typeof(SharedParameterElement));
            foreach (SharedParameterElement parameter in collector)
            {
                parameters.Add(parameter);
            }
            return parameters;
        }


        public static List<string> ParameterBindingsByGUID(Document doc, string parameterGUID)
        {
            List<string> parameterBindings = new List<string>();

            // get all parameters in the model
            List<SharedParameterElement> parametersInModel = GetSharedParameters(doc);
            foreach (SharedParameterElement parameter in parametersInModel)
            {
                if (parameter.GuidValue.ToString() == parameterGUID)
                {
                    // get the binding
                    DefinitionBindingMapIterator it = doc.ParameterBindings.ForwardIterator();
                    while (it.MoveNext())
                    {
                        // get the definition
                        Definition definition = it.Key as Definition;
                        if (definition == null || definition.Name != parameter.Name) { continue; }

                        // get the binding
                        ElementBinding binding = it.Current as ElementBinding;
                        if (binding == null) { continue; }

                        // get the categories the parameter is bound to
                        CategorySet categories = binding.Categories;
                        if (categories.Size == 0) { continue; }

                        //iterate over the categories
                        CategorySetIterator categorySetIterator = categories.ForwardIterator();
                        while (categorySetIterator.MoveNext())
                        {
                            //get the category and its name
                            Category category = categorySetIterator.Current as Category;
                            if (category == null) { continue; }

                            // add name to list to be returned
                            parameterBindings.Add(category.Name);
                        }
                    }
                }
            }

            return parameterBindings;
        }

        public static string GetSharedParameterValueFromElementByGUID(Element element, string parameterGUID)
        {
            string parameterValue = null;
            IList<Parameter> parameters = element.GetOrderedParameters();
            foreach (Parameter parameter in parameters)
            {
                try
                {
                    if (parameter.GUID.ToString() == parameterGUID)
                    {
                        parameterValue = parameter.AsString();
                    }
                }
                catch (Exception)
                {
                    //ignore and continue
                }
            }
            return parameterValue;
        }

        public static string GetSharedParameterValueFromElementByElementId(Element element, ElementId parameterId)
        {
            string parameterValue = null;

            IList<Parameter> parameters = element.GetOrderedParameters();
            foreach (Parameter parameter in parameters)
            {
                try
                {
                    if (parameter.Id == parameterId)
                    {
                        if (parameter.StorageType == StorageType.String)
                        {
                            parameterValue = parameter.AsString();
                        }
                        else if (parameter.StorageType == StorageType.Double)
                        {
                            parameterValue = parameter.AsDouble().ToString();
                        }
                        else if (parameter.StorageType == StorageType.Integer)
                        {
                            parameterValue = parameter.AsInteger().ToString();
                        }
                        else
                        {
                            parameterValue = parameter.AsElementId().ToString();
                        }
                    }
                }
                catch (Exception)
                {
                    //ignore and continue
                }
            }
            return parameterValue;
        }

        public static Dictionary<string, ElementId> GetSharedParameterIdsByGUID(Document doc)
        {
            Dictionary<string, ElementId> sharedParameterIds = new Dictionary<string, ElementId>();
            List<SharedParameterElement> sharedParameters = GetSharedParameters(doc);
            foreach (SharedParameterElement sharedParameter in sharedParameters)
            {
                sharedParameterIds.Add(sharedParameter.GuidValue.ToString(), sharedParameter.Id);
            }
            return sharedParameterIds;
        }


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

        public static bool SetSharedParameterValueByGUID(Document doc, Element el, string GUID, string value)
        {
            // get the shared parameter id
            ElementId sharedParameterId = null;
            Dictionary<string, ElementId> sharedParameterIdsByGUID = GetSharedParameterIdsByGUID(doc);
            if (sharedParameterIdsByGUID.ContainsKey(GUID))
            {
                sharedParameterId = sharedParameterIdsByGUID[GUID];
            }
            else
            {
                return false;
            }

            // set the value
            IList<Parameter> parameters = el.GetOrderedParameters();
            foreach (Parameter parameter in parameters)
            {
                if (parameter.Id == sharedParameterId)
                {
                    bool setResult = SetParameterValue(parameter, value);
                    return setResult;
                }
            }
            return false;
        }
    }
}
