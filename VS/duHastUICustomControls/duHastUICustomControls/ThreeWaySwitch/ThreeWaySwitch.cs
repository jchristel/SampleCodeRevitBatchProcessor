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

using System.Windows;
using System.Windows.Controls;

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
            Left = 0,
            Centre = 1,
            Right = 2
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
                new FrameworkPropertyMetadata(SwitchState.Centre, FrameworkPropertyMetadataOptions.BindsTwoWayByDefault));


        public static readonly DependencyProperty LabelLeftProperty =
            DependencyProperty.Register(nameof(LabelLeft), typeof(string), typeof(ThreeWaySwitch), new PropertyMetadata("Left"));

        public static readonly DependencyProperty LabelCenterProperty =
            DependencyProperty.Register(nameof(LabelCenter), typeof(string), typeof(ThreeWaySwitch), new PropertyMetadata("Centre"));

        public static readonly DependencyProperty LabelRightProperty =
            DependencyProperty.Register(nameof(LabelRight), typeof(string), typeof(ThreeWaySwitch), new PropertyMetadata("Right"));

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
