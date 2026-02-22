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

using System;
using System.Windows;
using System.Windows.Controls;

namespace duHastNet.UI.CustomControls
{
    /// <summary>
    /// A control that displays a loading overlay with an animated barcode over any content.
    /// The overlay is shown when IsBusy is true and hidden when false.
    /// </summary>
    [TemplatePart(Name = "PART_BarcodeTransform", Type = typeof(System.Windows.Media.TranslateTransform))]
    public class LoadingOverlay : ContentControl
    {
        static LoadingOverlay()
        {
            DefaultStyleKeyProperty.OverrideMetadata(
                typeof(LoadingOverlay),
                new FrameworkPropertyMetadata(typeof(LoadingOverlay)));
        }

        #region Dependency Properties

        /// <summary>
        /// Dependency property for IsBusy
        /// </summary>
        public static readonly DependencyProperty IsBusyProperty =
            DependencyProperty.Register(
                nameof(IsBusy),
                typeof(bool),
                typeof(LoadingOverlay),
                new PropertyMetadata(false));

        /// <summary>
        /// Gets or sets whether the loading overlay is visible
        /// </summary>
        public bool IsBusy
        {
            get => (bool)GetValue(IsBusyProperty);
            set => SetValue(IsBusyProperty, value);
        }

        /// <summary>
        /// Dependency property for LoadingMessage
        /// </summary>
        public static readonly DependencyProperty LoadingMessageProperty =
            DependencyProperty.Register(
                nameof(LoadingMessage),
                typeof(string),
                typeof(LoadingOverlay),
                new PropertyMetadata("Loading..."));

        /// <summary>
        /// Gets or sets the message displayed in the loading overlay
        /// </summary>
        public string LoadingMessage
        {
            get => (string)GetValue(LoadingMessageProperty);
            set => SetValue(LoadingMessageProperty, value);
        }

        /// <summary>
        /// Dependency property for OverlayOpacity
        /// </summary>
        public static readonly DependencyProperty OverlayOpacityProperty =
            DependencyProperty.Register(
                nameof(OverlayOpacity),
                typeof(double),
                typeof(LoadingOverlay),
                new PropertyMetadata(0.8));

        /// <summary>
        /// Gets or sets the opacity of the overlay background (0.0 to 1.0)
        /// </summary>
        public double OverlayOpacity
        {
            get => (double)GetValue(OverlayOpacityProperty);
            set => SetValue(OverlayOpacityProperty, value);
        }

        #endregion
    }
}
