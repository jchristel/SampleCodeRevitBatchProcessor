using System;
using System.Globalization;
using System.Windows.Data;

namespace duHastNet.UI.CustomControls.Converters
{
    public class StringContainsConverter : IValueConverter
    {
        public bool IgnoreCase { get; set; } = true;

        public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
        {
            if (value == null || parameter == null)
                return false;

            var stringValue = value.ToString();
            var searchText = parameter.ToString();

            if (string.IsNullOrEmpty(stringValue) || string.IsNullOrEmpty(searchText))
                return false;

            var comparison = IgnoreCase ? StringComparison.OrdinalIgnoreCase : StringComparison.Ordinal;
            return stringValue.Contains(searchText, comparison);
        }

        public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
        {
            throw new NotImplementedException("StringContainsConverter does not support ConvertBack");
        }
    }
}
