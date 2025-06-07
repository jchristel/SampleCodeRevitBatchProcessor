using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;

namespace duHastNet.UI.CustomControls.CustomDataGrid
{
    public static class FilterIndicatorBehavior
    {
        public static readonly DependencyProperty HasActiveFilterProperty =
            DependencyProperty.RegisterAttached(
                "HasActiveFilter",
                typeof(bool),
                typeof(FilterIndicatorBehavior),
                new PropertyMetadata(false));

        public static bool GetHasActiveFilter(DependencyObject obj)
        {
            return (bool)obj.GetValue(HasActiveFilterProperty);
        }

        public static void SetHasActiveFilter(DependencyObject obj, bool value)
        {
            obj.SetValue(HasActiveFilterProperty, value);
        }
    }
}
