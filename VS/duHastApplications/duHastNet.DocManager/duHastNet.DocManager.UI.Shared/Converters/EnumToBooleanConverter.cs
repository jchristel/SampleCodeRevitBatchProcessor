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
using System.Globalization;
using System.Windows.Data;

namespace duHastNet.DocManager.UI.Shared.Converters
{
    /// <summary>
    /// Converts an enum value to a boolean for radio button binding
    /// Used to bind multiple radio buttons to a single enum property
    /// </summary>
    public class EnumToBooleanConverter : IValueConverter
    {
        /// <summary>
        /// Converts enum value to boolean by comparing with parameter
        /// </summary>
        /// <param name="value">The enum value</param>
        /// <param name="targetType">Target type (bool)</param>
        /// <param name="parameter">String representation of enum value to compare</param>
        /// <param name="culture">Culture info</param>
        /// <returns>True if enum value matches parameter, false otherwise</returns>
        public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
        {
            if (value == null || parameter == null)
                return false;

            return value.ToString() == parameter.ToString();
        }

        /// <summary>
        /// Converts boolean back to enum value when radio button is selected
        /// </summary>
        /// <param name="value">Boolean value from radio button</param>
        /// <param name="targetType">Target enum type</param>
        /// <param name="parameter">String representation of enum value</param>
        /// <param name="culture">Culture info</param>
        /// <returns>Enum value if conversion successful, otherwise DoNothing</returns>
        public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
        {
            if (value is bool boolValue && boolValue && parameter != null)
            {
                try
                {
                    return Enum.Parse(targetType, parameter.ToString()!);
                }
                catch
                {
                    return System.Windows.Data.Binding.DoNothing;
                }
            }
            return System.Windows.Data.Binding.DoNothing;
        }
    }
}
