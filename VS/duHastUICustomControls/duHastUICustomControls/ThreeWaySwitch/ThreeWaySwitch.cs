using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;

namespace duHastNet.UI.CustomControls
{
    /// <summary>
    /// Follow steps 1a or 1b and then 2 to use this custom control in a XAML file.
    ///
    /// Step 1a) Using this custom control in a XAML file that exists in the current project.
    /// Add this XmlNamespace attribute to the root element of the markup file where it is 
    /// to be used:
    ///
    ///     xmlns:MyNamespace="clr-namespace:duHastUICustomControls"
    ///
    ///
    /// Step 1b) Using this custom control in a XAML file that exists in a different project.
    /// Add this XmlNamespace attribute to the root element of the markup file where it is 
    /// to be used:
    ///
    ///     xmlns:MyNamespace="clr-namespace:duHastUICustomControls;assembly=duHastUICustomControls"
    ///
    /// You will also need to add a project reference from the project where the XAML file lives
    /// to this project and Rebuild to avoid compilation errors:
    ///
    ///     Right click on the target project in the Solution Explorer and
    ///     "Add Reference"->"Projects"->[Select this project]
    ///
    ///
    /// Step 2)
    /// Go ahead and use your control in the XAML file.
    ///
    ///     <MyNamespace:CustomControl1/>
    ///
    /// </summary>
    public class ThreeWaySwitch : Control
    {
        public enum SwitchState
        {
            Off = 0,
            Neutral = 1,
            On = 2
        }
        static ThreeWaySwitch()
        {
            DefaultStyleKeyProperty.OverrideMetadata(typeof(ThreeWaySwitch), new FrameworkPropertyMetadata(typeof(ThreeWaySwitch)));
        }

        public SwitchState Value
        {
            get => (SwitchState)GetValue(ValueProperty);
            set => SetValue(ValueProperty, value);
        }

        public static readonly DependencyProperty ValueProperty =
            DependencyProperty.Register(
                nameof(Value),
                typeof(SwitchState),
                typeof(ThreeWaySwitch),
                new FrameworkPropertyMetadata(SwitchState.Neutral, FrameworkPropertyMetadataOptions.BindsTwoWayByDefault));


        public static readonly DependencyProperty LabelLeftProperty =
            DependencyProperty.Register(nameof(LabelLeft), typeof(string), typeof(ThreeWaySwitch), new PropertyMetadata("Off"));

        public static readonly DependencyProperty LabelCenterProperty =
            DependencyProperty.Register(nameof(LabelCenter), typeof(string), typeof(ThreeWaySwitch), new PropertyMetadata("Neutral"));

        public static readonly DependencyProperty LabelRightProperty =
            DependencyProperty.Register(nameof(LabelRight), typeof(string), typeof(ThreeWaySwitch), new PropertyMetadata("On"));

        public static readonly DependencyProperty DisplayNameProperty =
            DependencyProperty.Register(nameof(DisplayName), typeof(string), typeof(ThreeWaySwitch), new PropertyMetadata("Switch"));

        public string LabelLeft
        {
            get => (string)GetValue(LabelLeftProperty);
            set => SetValue(LabelLeftProperty, value);
        }

        public string LabelCenter
        {
            get => (string)GetValue(LabelCenterProperty);
            set => SetValue(LabelCenterProperty, value);
        }

        public string LabelRight
        {
            get => (string)GetValue(LabelRightProperty);
            set => SetValue(LabelRightProperty, value);
        }

        public string DisplayName
        {
            get => (string)GetValue(DisplayNameProperty);
            set => SetValue(DisplayNameProperty, value);
        }
    }
}
