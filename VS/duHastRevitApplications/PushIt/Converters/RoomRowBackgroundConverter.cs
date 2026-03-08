// BSD License - Copyright 2025, Jan Christel

using System;
using System.Globalization;
using System.Windows.Data;

namespace duHastNet.PushIt.Converters
{
    /// <summary>
    /// Converts a room ID string to a token used by the rooms grid row style triggers.
    /// - IDs containing "::SPLIT::" → "SplitRoom"  → amber row background
    /// - IDs starting with "NEW"    → "NewRoom"     → light green row background
    /// - All other IDs              → null           → Count-based colouring applies
    /// </summary>
    [ValueConversion(typeof(object), typeof(string))]
    public class RoomRowBackgroundConverter : IValueConverter
    {
        public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
        {
            if (value is string id)
            {
                if (id.Contains("::SPLIT::", StringComparison.OrdinalIgnoreCase))
                    return "SplitRoom";
                if (id.StartsWith("NEW", StringComparison.OrdinalIgnoreCase))
                    return "NewRoom";
            }
            return null;
        }

        public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
            => throw new NotImplementedException();
    }
}
