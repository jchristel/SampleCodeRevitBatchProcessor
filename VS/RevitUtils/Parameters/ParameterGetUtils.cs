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
using duHast.Utils;
using System.Collections.Generic;
using System;

namespace duHast.RevitUtils.Parameters
{
    public static class ParameterGetUtils
    {


        /// <summary>
        /// Get the value of a parameter as a string. Double values are converted to metric.
        /// </summary>
        /// <param name="para"></param>
        /// <returns>A string representing the parameter value. If an exception occured the string will include the exception message.</returns>
        public static string GetParameterValueAsString(Parameter para)
        {
            // Set return value default
            string parameterValue = "no Value";
            try
            {
                var valueGetter = new Dictionary<StorageType, Func<Parameter, object>>
                {
                    { StorageType.Double, GetterDoubleAsDoubleConvertedToMetric },
                    { StorageType.Integer, GetterDoubleOrIntAsString },
                    { StorageType.String, GetterStringAsString },
                    { StorageType.ElementId, GetterElementIdAsString },
                    { StorageType.None, GetterNone }
                };

                parameterValue = GetParameterValueWithOverLoad(para, valueGetter).ToString();
            }
            catch (Exception e)
            {
                parameterValue = $"Exception: {e.Message}";
            }

            return parameterValue;
        }

        /// <summary>
        /// Gets the value of a parameter by using overload functions depending on the parameter storage type.
        /// </summary>
        /// <param name="para">The parameter.</param>
        /// <param name="parameterValueGetters">The dictionary of parameter value getters.</param>
        /// <returns>The parameter value.</returns>
        public static object GetParameterValueWithOverLoad(Parameter para, Dictionary<StorageType, Func<Parameter, object>> parameterValueGetters)
        {
            // Set return value default (default value should never be used...!)
            object parameterValue = null;
            try
            {
                // Extract parameter value depending on its storage type
                if (para.StorageType == StorageType.Double)
                {
                    if (parameterValueGetters.ContainsKey(StorageType.Double))
                    {
                        parameterValue = parameterValueGetters[StorageType.Double](para);
                    }
                    else
                    {
                        throw new ArgumentException("No parameter value getter for storage type Double provided");
                    }
                }
                else if (para.StorageType == StorageType.Integer)
                {
                    if (parameterValueGetters.ContainsKey(StorageType.Integer))
                    {
                        parameterValue = parameterValueGetters[StorageType.Integer](para);
                    }
                    else
                    {
                        throw new ArgumentException("No parameter value getter for storage type Integer provided");
                    }
                }
                else if (para.StorageType == StorageType.String)
                {
                    if (parameterValueGetters.ContainsKey(StorageType.String))
                    {
                        parameterValue = parameterValueGetters[StorageType.String](para);
                    }
                    else
                    {
                        throw new ArgumentException("No parameter value getter for storage type String provided");
                    }
                }
                else if (para.StorageType == StorageType.ElementId)
                {
                    if (parameterValueGetters.ContainsKey(StorageType.ElementId))
                    {
                        parameterValue = parameterValueGetters[StorageType.ElementId](para);
                    }
                    else
                    {
                        throw new ArgumentException("No parameter value getter for storage type ElementId provided");
                    }
                }
                else
                {
                    // This should be invalid storage type only
                    parameterValue = parameterValueGetters[StorageType.None](para);
                }
            }
            catch (Exception e)
            {
                parameterValue = $"Exception: {e.Message}";
            }
            return parameterValue;
        }


        #region Getters

        #region doubles

        /// <summary>
        /// return the value of a parameter as a double, converted to metric if applicable
        /// </summary>
        public static object GetterDoubleAsDoubleConvertedToMetric(Parameter para)
        {
            double? parameterValue = null;

            // Check if the parameter value is not null or empty
            if (!string.IsNullOrEmpty(para.AsValueString()))
            {
                // Assume this is Revit 2023 onwards
                var dataType = para.Definition.GetDataType();
                if (dataType == SpecTypeId.Length)
                {
                    parameterValue = UnitConversion.ConvertImperialFeetToMetricMm(para.AsDouble());
                }
                else if (dataType == SpecTypeId.Area)
                {
                    parameterValue = UnitConversion.ConvertImperialSquareFeetToMetricSquareMetre(para.AsDouble());
                }
                else if (dataType == SpecTypeId.Volume)
                {
                    parameterValue = UnitConversion.ConvertImperialCubicFeetToMetricCubicMetre(para.AsDouble());
                }
                else
                {
                    parameterValue = para.AsDouble();
                }
            }

            return parameterValue;
        }

        /// <summary>
        /// return the double value of a parameter as a string
        /// </summary>
        /// <param name="para"></param>
        /// <returns></returns>
        private static object GetterDoubleOrIntAsString(Parameter para)
        {
            return para.AsDouble().ToString();
        }


        /// <summary>
        /// Returns a parameter value of type double as a double.
        /// </summary>
        /// <param name="para">The parameter.</param>
        /// <returns>Double value. If value is empty it will return null.</returns>
        public static object GetterDoubleAsDouble(Parameter para)
        {
            double? parameterValue = null;
            if (!string.IsNullOrEmpty(para.AsValueString()))
            {
                parameterValue = para.AsDouble();
            }
            return parameterValue;
        }

        #endregion doubles

        #region integer

        /// <summary>
        /// Returns a parameter value of type integer as an integer.
        /// </summary>
        /// <param name="para">The parameter.</param>
        /// <returns>Integer value. If value is empty it will return null.</returns>
        public static object GetterIntAsInt(Parameter para)
        {
            int? parameterValue = null;
            if (!string.IsNullOrEmpty(para.AsValueString()))
            {
                parameterValue = para.AsInteger();
            }
            return parameterValue;
        }

        #endregion integer


        #region strings
        private static object GetterStringAsString(Parameter para)
        {
            return para.AsString();
        }

        #endregion strings

        #region ElementId

        /// <summary>
        /// Returns a parameter value of type element id as a string.
        /// </summary>
        /// <param name="para"></param>
        /// <returns></returns>
        private static object GetterElementIdAsString(Parameter para)
        {
            return para.AsElementId().ToString();
        }

        /// <summary>
        /// Returns a parameter value of type element id as an element id.
        /// </summary>
        /// <param name="para">The parameter.</param>
        /// <returns>Element id value. If value is empty it will return null.</returns>
        public static object GetterElementIdAsElementId(Parameter para)
        {
            ElementId parameterValue = null;
            if (para.StorageType == StorageType.ElementId)
            {
                if (para.AsElementId() != null)
                {
                    parameterValue = para.AsElementId();
                }
            }
            return parameterValue;
        }

        /// <summary>
        /// Returns a parameter value of type element id as an integer.
        /// </summary>
        /// <param name="para">The parameter.</param>
        /// <returns>Integer value. If value is empty it will return null.</returns>
        public static object GetterElementIdAsElementInt(Parameter para)
        {
            int? parameterValue = null;
            if (para.StorageType == StorageType.ElementId)
            {
                if (para.AsElementId() != null)
                {
                    parameterValue = para.AsElementId().IntegerValue;
                }
            }
            return parameterValue;
        }


        #endregion ElementId

        /// <summary>
        /// Method used if the storage type on a parameter is None.
        /// </summary>
        /// <param name="para">The parameter.</param>
        /// <returns>String "None".</returns>
        private static object GetterNone(Parameter para)
        {
            return "None";
        }

        #endregion Getters

    }
}

