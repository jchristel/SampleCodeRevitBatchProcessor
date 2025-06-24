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

using System.Collections.Specialized;
using System.Windows;
using System.Windows.Controls;

namespace duHastNet.UI.CustomControls.CustomDataGrid
{
    /// <summary>
    /// Provides attached behavior for DataGrid column header management, including context menus,
    /// filtering capabilities, and bulk selection operations.
    /// </summary>
    public static partial class DataGridColumnHeaderBehavior
    {
        #region Dependency Properties

        /// <summary>
        /// Dependency property for enabling column management features (context menus, filtering, etc.)
        /// </summary>
        public static readonly DependencyProperty EnableColumnManagementProperty =
            DependencyProperty.RegisterAttached(
                "EnableColumnManagement",
                typeof(bool),
                typeof(DataGridColumnHeaderBehavior),
                new PropertyMetadata(false, OnEnableColumnManagementChanged));

        /// <summary>
        /// Dependency property for enabling bulk selection operations on rows
        /// </summary>
        public static readonly DependencyProperty EnableBulkSelectionProperty =
        DependencyProperty.RegisterAttached(
                "EnableBulkSelection",
                typeof(bool),
                typeof(DataGridColumnHeaderBehavior),
                new PropertyMetadata(false));

        /// <summary>
        /// Dependency property for specifying which column contains the checkboxes for bulk selection
        /// </summary>
        public static readonly DependencyProperty BulkSelectionColumnProperty =
            DependencyProperty.RegisterAttached(
                "BulkSelectionColumn",
                typeof(string),
                typeof(DataGridColumnHeaderBehavior),
                new PropertyMetadata(null));

        #endregion

        #region Dependency Property Accessors

        /// <summary>
        /// Gets the value of the EnableColumnManagement attached property for the specified object.
        /// </summary>
        /// <param name="obj">The object from which to read the property value.</param>
        /// <returns>True if column management is enabled, false otherwise.</returns>
        public static bool GetEnableColumnManagement(DependencyObject obj)
        {
            return (bool)obj.GetValue(EnableColumnManagementProperty);
        }

        /// <summary>
        /// Sets the value of the EnableColumnManagement attached property for the specified object.
        /// </summary>
        /// <param name="obj">The object on which to set the property value.</param>
        /// <param name="value">True to enable column management features, false to disable.</param>
        public static void SetEnableColumnManagement(DependencyObject obj, bool value)
        {
            obj.SetValue(EnableColumnManagementProperty, value);
        }

        /// <summary>
        /// Gets the value of the EnableBulkSelection attached property for the specified object.
        /// </summary>
        /// <param name="obj">The object from which to read the property value.</param>
        /// <returns>True if bulk selection is enabled, false otherwise.</returns>
        public static bool GetEnableBulkSelection(DependencyObject obj)
        {
            return (bool)obj.GetValue(EnableBulkSelectionProperty);
        }

        /// <summary>
        /// Sets the value of the EnableBulkSelection attached property for the specified object.
        /// </summary>
        /// <param name="obj">The object on which to set the property value.</param>
        /// <param name="value">True to enable bulk selection operations, false to disable.</param>
        public static void SetEnableBulkSelection(DependencyObject obj, bool value)
        {
            obj.SetValue(EnableBulkSelectionProperty, value);
        }

        /// <summary>
        /// Gets the name of the column used for bulk selection checkboxes.
        /// </summary>
        /// <param name="obj">The object from which to read the property value.</param>
        /// <returns>The property name of the column containing checkboxes for bulk selection.</returns>
        public static string GetBulkSelectionColumn(DependencyObject obj)
        {
            return (string)obj.GetValue(BulkSelectionColumnProperty);
        }

        /// <summary>
        /// Sets the name of the column used for bulk selection checkboxes.
        /// </summary>
        /// <param name="obj">The object on which to set the property value.</param>
        /// <param name="value">The property name of the column containing checkboxes for bulk selection.</param>
        public static void SetBulkSelectionColumn(DependencyObject obj, string value)
        {
            obj.SetValue(BulkSelectionColumnProperty, value);
        }

        #endregion

        #region Event Handlers

        /// <summary>
        /// Handles changes to the EnableColumnManagement property and sets up or tears down the behavior.
        /// </summary>
        /// <param name="d">The DataGrid object that the property was changed on.</param>
        /// <param name="e">The event data containing the old and new values.</param>
        private static void OnEnableColumnManagementChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is DataGrid dataGrid)
            {
                if ((bool)e.NewValue)
                {
                    dataGrid.Loaded += DataGrid_Loaded;
                    dataGrid.ColumnDisplayIndexChanged += DataGrid_ColumnDisplayIndexChanged;

                    // Subscribe to column collection changes
                    ((INotifyCollectionChanged)dataGrid.Columns).CollectionChanged += (s, args) => RefreshContextMenus(dataGrid);

                    // Add row context menu if bulk selection is enabled
                    dataGrid.Loaded += (s, args) => SetupRowContextMenus(dataGrid);
                }
                else
                {
                    dataGrid.Loaded -= DataGrid_Loaded;
                    dataGrid.ColumnDisplayIndexChanged -= DataGrid_ColumnDisplayIndexChanged;
                }
            }
        }

        /// <summary>
        /// Handles the DataGrid Loaded event to initialize context menus and behaviors.
        /// </summary>
        /// <param name="sender">The DataGrid that was loaded.</param>
        /// <param name="e">The event arguments.</param>
        private static void DataGrid_Loaded(object sender, RoutedEventArgs e)
        {
            if (sender is DataGrid dataGrid)
            {
                RefreshContextMenus(dataGrid);
            }
        }

        /// <summary>
        /// Handles changes to column display order and refreshes context menus accordingly.
        /// </summary>
        /// <param name="sender">The DataGrid where the column display index changed.</param>
        /// <param name="e">The event arguments containing column information.</param>
        private static void DataGrid_ColumnDisplayIndexChanged(object sender, DataGridColumnEventArgs e)
        {
            if (sender is DataGrid dataGrid)
            {
                RefreshContextMenus(dataGrid);
            }
        }

        #endregion
    }
}