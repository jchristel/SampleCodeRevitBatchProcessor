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

namespace duHastNet.Utils.DataConversion
{
    public static class TypeConverter
    {
        /// <summary>
        /// Converts a string value to the specified target type
        /// </summary>
        /// <param name="value">String value to convert</param>
        /// <param name="targetType">Target type to convert to</param>
        /// <returns>Converted value or original string if conversion fails</returns>
        public static object ConvertStringToType(string value, Type targetType)
        {
            // Handle null or empty strings
            if (string.IsNullOrEmpty(value))
            {
                if (targetType.IsValueType && Nullable.GetUnderlyingType(targetType) == null)
                {
                    return Activator.CreateInstance(targetType); // Default value for non-nullable value types
                }
                return null;
            }

            try
            {
                // Handle nullable types
                Type underlyingType = Nullable.GetUnderlyingType(targetType) ?? targetType;

                if (underlyingType == typeof(string))
                {
                    return value;
                }
                else if (underlyingType == typeof(int))
                {
                    return int.Parse(value);
                }
                else if (underlyingType == typeof(double))
                {
                    return double.Parse(value);
                }
                else if (underlyingType == typeof(bool))
                {
                    // Handle various boolean representations
                    if (value == "1" || value.ToLower() == "true" || value.ToLower() == "yes")
                        return true;
                    if (value == "0" || value.ToLower() == "false" || value.ToLower() == "no")
                        return false;
                    return bool.Parse(value);
                }
                else if (underlyingType == typeof(DateTime))
                {
                    return DateTime.Parse(value);
                }
                else
                {
                    // Generic conversion for other types
                    return Convert.ChangeType(value, underlyingType);
                }
            }
            catch (Exception)
            {
                // If conversion fails, return the original string
                return value;
            }
        }

        /// <summary>
        /// Converts a string to a Type based on common type names
        /// </summary>
        /// <param name="typeString">String representation of type</param>
        /// <returns>Corresponding Type</returns>
        public static Type GetTypeFromString(string typeString)
        {
            if (string.IsNullOrEmpty(typeString))
                return typeof(string);

            switch (typeString.ToLower())
            {
                // custom string options
                case "text":
                    return typeof(string);
                case "number":
                    return typeof(int);
                case "decimal":
                    return typeof(double);
                case "yes/no":
                    return typeof(bool);
                case "date":
                    return typeof(DateTime);

                // .NET type names
                case "string":
                    return typeof(string);
                case "int32":
                    return typeof(int);
                case "int":
                    return typeof(int);
                case "double":
                    return typeof(double);
                case "boolean":
                    return typeof(bool);
                case "bool":
                    return typeof(bool);
                case "datetime":
                    return typeof(DateTime);

                // Domain-specific types (from your original function)
                case "length":
                case "currency":
                case "distance":
                case "angle":
                case "rotation angle":
                case "time":
                case "cost per area":
                case "slope":
                case "speed":
                case "area":
                case "volume":
                    return typeof(double);

                default:
                    return Type.GetType(typeString) ?? typeof(string);
            }
        }

        /// <summary>
        /// Generic version for type-safe conversion
        /// </summary>
        /// <typeparam name="T">Target type</typeparam>
        /// <param name="value">String value to convert</param>
        /// <returns>Converted value</returns>
        public static T ConvertStringTo<T>(string value)
        {
            return (T)ConvertStringToType(value, typeof(T));
        }
    }
}
