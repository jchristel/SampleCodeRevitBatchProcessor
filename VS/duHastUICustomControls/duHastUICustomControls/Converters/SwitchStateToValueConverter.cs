using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Data;
using static duHastNet.UI.CustomControls.ThreeWaySwitch;

namespace duHastNet.UI.CustomControls.Converters
{
    public class SwitchStateToValueConverter:IValueConverter
    {
        public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
        {
            return (int)(SwitchState)value;
        }

        public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
        {
            return (SwitchState)(int)(double)value;
        }
    }
}
