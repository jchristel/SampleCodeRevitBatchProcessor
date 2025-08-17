using System;
using System.Globalization;
using System.Windows.Data;

namespace duHastNet.Utils.WPF.Converters
{
    // <summary>
    /// Converter that combines multiple values into an array for command parameters
    /// </summary>
    public class MultiParameterConverter : IMultiValueConverter
    {
        public object Convert(object[] values, Type targetType, object parameter, CultureInfo culture)
        {
            // Return all the values as an array
            return values?.Clone();
        }

        public object[] ConvertBack(object value, Type[] targetTypes, object parameter, CultureInfo culture)
        {
            throw new NotImplementedException();
        }
    }
}
