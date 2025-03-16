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

namespace duHast.RevitUtils.Parameters
{
    /// <summary>
    /// A static class providing utility methods for shared parameters.
    /// </summary>
    public static class SharedParaUtils
    {
        #region all shared parameter getters

        /// <summary>
        /// Returns all shared parameters in a document.
        /// </summary>
        /// <param name="doc"></param>
        /// <returns>A list of all shared paramters presetn or an empty list if none are in the model.</returns>
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

        /// <summary>
        /// Returns all shared parameters in a document as aa dictionary where key is the shared parameter GUID and value is the ElementId of the shared parameter.
        /// </summary>
        /// <param name="doc">The document to get the shared parameters from.</param>
        /// <returns>A dictionary where key is the shared parameter GUID and value is the ElementId of the shared parameter.</returns>
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

        #endregion all shared parameter getters


        #region misc shared parameter utils

        /// <summary>
        /// Get the categories a shared parameter is bound to
        /// </summary>
        /// <param name="doc"></param>
        /// <param name="parameterGUID"></param>
        /// <returns> 
        /// Null if the parameter was not found, otherwise a list of category names the parameter is bound to. If no categories are bound to the parameter, an empty list is returned.
        /// </returns>
        public static List<string> ParameterBindingsByGUID(Document doc, string parameterGUID)
        {
            List<string> parameterBindings = new List<string>();
            
            // flag if parameter was found to start with
            bool foundParameter = false;

            // get all parameters in the model
            List<SharedParameterElement> parametersInModel = GetSharedParameters(doc);
            foreach (SharedParameterElement parameter in parametersInModel)
            {
                if (parameter.GuidValue.ToString() == parameterGUID)
                {
                    //set flag parameter was found
                    foundParameter = true;
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
            return foundParameter ? parameterBindings : null;
        }

        #endregion

        #region shared parameter value getters

        /// <summary>
        /// Returns the value of a shared parameter as a string. 
        /// Imperial unit values are converted to metric.
        /// </summary>
        /// <param name="element">The element of which to retieve the parameter value from.</param>
        /// <param name="parameterGUID">The guid of the hared parameter of which to retrieve the value from.</param>
        /// <returns>A string if the parameter was found on the element. Otherwise null</returns>
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
                        // get parameter value as string. This will also convert imperial units to metric!
                        parameterValue = ParameterGetUtils.GetParameterValueAsString(para:parameter);
                    }
                }
                catch (Exception)
                {
                    //ignore and continue
                }
            }
            return parameterValue;
        }

        /// <summary>
        /// Return the value of a shared parameter as a string. The parameter is identified by its ElementId.
        /// </summary> 
        /// <param name="element">The element of which to retieve the parameter value from.</param>
        /// <param name="parameterId">The ElementId of the shared parameter of which to retrieve the value from.</param>
        /// <returns>A string if the parameter was found on the element. Otherwise null</returns>
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
                        // get parameter value as string. This will also convert imperial units to metric!
                        parameterValue = ParameterGetUtils.GetParameterValueAsString(para: parameter);
                        return parameterValue;
                    }
                }
                catch (Exception)
                {
                    //ignore and continue
                }
            }
            return parameterValue;
        }

        #endregion shared parameter value getters

        #region shared parameter value setters

        /// <summary>
        /// Sets the value of a shared parameter identified by its GUID on an element .
        /// </summary>
        /// <param name="doc">The current model document</param>
        /// <param name="el">The Revit element</param>
        /// <param name="GUID">The guid identifying the parameter</param>
        /// <param name="value">The value to set the parameter to.</param>
        /// <returns>True if the parameter value was set. Otherwise false (i.e. parameter was not set successfully or the parameter does not exist on the element)</returns>
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
                    bool setResult = ParameterSetUtils.SetParameterValue(parameter, value);
                    return setResult;
                }
            }
            return false;
        }

        #endregion shared parameter value setters
    }
}
