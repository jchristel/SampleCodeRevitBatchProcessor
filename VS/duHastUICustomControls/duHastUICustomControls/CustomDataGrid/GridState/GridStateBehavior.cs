//
//License:
//
//
// Revit Batch Processor Sample Code
//
// BSD License
// Copyright 2025, Jan Christel
// Written by Claude
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

using duHastNet.UI.CustomControls.CustomDataGrid;
using duHastNet.UI.CustomControls.CustomDataGrid.GridState;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Threading;

namespace duHastNet.UI.CustomControls.CustomDataGrid.GridState
{
    /// <summary>
    /// Attached behavior that adds state management capabilities to DataGrid controls
    /// </summary>
    public static class GridStateBehavior
    {
        private static readonly Dictionary<DataGrid, GridStateContext> _gridContexts = new Dictionary<DataGrid, GridStateContext>();
        private static GridStateManager _defaultStateManager;

        #region Dependency Properties

        /// <summary>
        /// Enable state management for this DataGrid
        /// </summary>
        public static readonly DependencyProperty EnableStateManagementProperty =
            DependencyProperty.RegisterAttached(
                "EnableStateManagement",
                typeof(bool),
                typeof(GridStateBehavior),
                new PropertyMetadata(false, OnEnableStateManagementChanged));

        /// <summary>
        /// Unique identifier for this grid's state
        /// </summary>
        public static readonly DependencyProperty GridIdProperty =
            DependencyProperty.RegisterAttached(
                "GridId",
                typeof(string),
                typeof(GridStateBehavior),
                new PropertyMetadata(null));

        /// <summary>
        /// State manager to use (optional - uses default if not specified)
        /// </summary>
        public static readonly DependencyProperty StateManagerProperty =
            DependencyProperty.RegisterAttached(
                "StateManager",
                typeof(GridStateManager),
                typeof(GridStateBehavior),
                new PropertyMetadata(null));

        /// <summary>
        /// Options for state management
        /// </summary>
        public static readonly DependencyProperty StateOptionsProperty =
            DependencyProperty.RegisterAttached(
                "StateOptions",
                typeof(GridStateOptions),
                typeof(GridStateBehavior),
                new PropertyMetadata(null));

        /// <summary>
        /// Auto-save state name (if specified, will auto-save to this state name)
        /// </summary>
        public static readonly DependencyProperty AutoSaveStateNameProperty =
            DependencyProperty.RegisterAttached(
                "AutoSaveStateName",
                typeof(string),
                typeof(GridStateBehavior),
                new PropertyMetadata(null));

        /// <summary>
        /// Auto-load state name (if specified, will auto-load this state on startup)
        /// </summary>
        public static readonly DependencyProperty AutoLoadStateNameProperty =
            DependencyProperty.RegisterAttached(
                "AutoLoadStateName",
                typeof(string),
                typeof(GridStateBehavior),
                new PropertyMetadata(null));

        #endregion

        #region Dependency Property Accessors

        public static bool GetEnableStateManagement(DependencyObject obj)
            => (bool)obj.GetValue(EnableStateManagementProperty);

        public static void SetEnableStateManagement(DependencyObject obj, bool value)
            => obj.SetValue(EnableStateManagementProperty, value);

        public static string GetGridId(DependencyObject obj)
            => (string)obj.GetValue(GridIdProperty);

        public static void SetGridId(DependencyObject obj, string value)
            => obj.SetValue(GridIdProperty, value);

        public static GridStateManager GetStateManager(DependencyObject obj)
            => (GridStateManager)obj.GetValue(StateManagerProperty);

        public static void SetStateManager(DependencyObject obj, GridStateManager value)
            => obj.SetValue(StateManagerProperty, value);

        public static GridStateOptions GetStateOptions(DependencyObject obj)
            => (GridStateOptions)obj.GetValue(StateOptionsProperty);

        public static void SetStateOptions(DependencyObject obj, GridStateOptions value)
            => obj.SetValue(StateOptionsProperty, value);

        public static string GetAutoSaveStateName(DependencyObject obj)
            => (string)obj.GetValue(AutoSaveStateNameProperty);

        public static void SetAutoSaveStateName(DependencyObject obj, string value)
            => obj.SetValue(AutoSaveStateNameProperty, value);

        public static string GetAutoLoadStateName(DependencyObject obj)
            => (string)obj.GetValue(AutoLoadStateNameProperty);

        public static void SetAutoLoadStateName(DependencyObject obj, string value)
            => obj.SetValue(AutoLoadStateNameProperty, value);

        #endregion

        #region Public Methods

        /// <summary>
        /// Sets the default state manager for all grids
        /// </summary>
        public static void SetDefaultStateManager(GridStateManager stateManager)
        {
            _defaultStateManager = stateManager;
        }

        /// <summary>
        /// Saves the current state of a DataGrid
        /// </summary>
        public static async Task<bool> SaveStateAsync(DataGrid dataGrid, string stateName)
        {
            if (!_gridContexts.TryGetValue(dataGrid, out var context))
                return false;

            var state = CaptureCurrentState(dataGrid, context.GridId, stateName);
            return await context.StateManager.SaveStateAsync(context.GridId, stateName, state);
        }

        /// <summary>
        /// Loads a state for a DataGrid
        /// </summary>
        public static async Task<bool> LoadStateAsync(DataGrid dataGrid, string stateName)
        {
            if (!_gridContexts.TryGetValue(dataGrid, out var context))
                return false;

            var state = await context.StateManager.LoadStateAsync(context.GridId, stateName);
            if (state == null)
                return false;

            return ApplyStateToGrid(dataGrid, state, context.Options);
        }

        /// <summary>
        /// Gets all available states for a DataGrid
        /// </summary>
        public static async Task<List<string>> GetAvailableStatesAsync(DataGrid dataGrid)
        {
            if (!_gridContexts.TryGetValue(dataGrid, out var context))
                return new List<string>();

            return await context.StateManager.GetAvailableStatesAsync(context.GridId);
        }

        /// <summary>
        /// Deletes a saved state
        /// </summary>
        public static async Task<bool> DeleteStateAsync(DataGrid dataGrid, string stateName)
        {
            if (!_gridContexts.TryGetValue(dataGrid, out var context))
                return false;

            return await context.StateManager.DeleteStateAsync(context.GridId, stateName);
        }

        /// <summary>
        /// Gets detailed information about all states
        /// </summary>
        public static async Task<List<DataGridState>> GetStateInfoAsync(DataGrid dataGrid)
        {
            if (!_gridContexts.TryGetValue(dataGrid, out var context))
                return new List<DataGridState>();

            return await context.StateManager.GetStateInfoAsync(context.GridId);
        }

        /// <summary>
        /// Forces an immediate capture and auto-save of the current state
        /// </summary>
        public static async Task ForceAutoSaveAsync(DataGrid dataGrid)
        {
            if (!_gridContexts.TryGetValue(dataGrid, out var context) ||
                string.IsNullOrEmpty(context.AutoSaveStateName))
                return;

            await SaveStateAsync(dataGrid, context.AutoSaveStateName);
        }

        #endregion

        #region Event Handlers

        private static void OnEnableStateManagementChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (!(d is DataGrid dataGrid))
                return;

            if ((bool)e.NewValue)
            {
                SetupStateManagement(dataGrid);
            }
            else
            {
                CleanupStateManagement(dataGrid);
            }
        }

        private static void SetupStateManagement(DataGrid dataGrid)
        {
            var gridId = GetGridId(dataGrid);
            if (string.IsNullOrEmpty(gridId))
            {
                // Generate a default grid ID based on the control name or type
                gridId = dataGrid.Name ?? $"{dataGrid.GetType().Name}_{dataGrid.GetHashCode()}";
                SetGridId(dataGrid, gridId);
            }

            var stateManager = GetStateManager(dataGrid) ?? _defaultStateManager ??
                              new GridStateManager(GetStateOptions(dataGrid));
            var options = GetStateOptions(dataGrid) ?? new GridStateOptions();
            var autoSaveStateName = GetAutoSaveStateName(dataGrid);
            var autoLoadStateName = GetAutoLoadStateName(dataGrid);

            var context = new GridStateContext
            {
                GridId = gridId,
                StateManager = stateManager,
                Options = options,
                AutoSaveStateName = autoSaveStateName,
                AutoLoadStateName = autoLoadStateName
            };

            _gridContexts[dataGrid] = context;

            // Subscribe to events
            dataGrid.Loaded += OnDataGridLoaded;
            dataGrid.Unloaded += OnDataGridUnloaded;
            dataGrid.ColumnDisplayIndexChanged += OnDataGridChanged;
            dataGrid.ColumnReordered += OnDataGridChanged;
            dataGrid.Sorting += OnDataGridSorting;

            // Subscribe to ViewModel events if available
            SubscribeToViewModelEvents(dataGrid, context);
        }

        private static void CleanupStateManagement(DataGrid dataGrid)
        {
            if (_gridContexts.TryGetValue(dataGrid, out var context))
            {
                // Unsubscribe from events
                dataGrid.Loaded -= OnDataGridLoaded;
                dataGrid.Unloaded -= OnDataGridUnloaded;
                dataGrid.ColumnDisplayIndexChanged -= OnDataGridChanged;
                dataGrid.ColumnReordered -= OnDataGridChanged;
                dataGrid.Sorting -= OnDataGridSorting;

                UnsubscribeFromViewModelEvents(dataGrid, context);

                _gridContexts.Remove(dataGrid);
            }
        }

        private static async void OnDataGridLoaded(object sender, RoutedEventArgs e)
        {
            var dataGrid = sender as DataGrid;
            if (!_gridContexts.TryGetValue(dataGrid, out var context))
                return;

            // Auto-load state if specified
            if (!string.IsNullOrEmpty(context.AutoLoadStateName))
            {
                // Delay slightly to ensure the grid is fully loaded
                await Task.Delay(100);
                await LoadStateAsync(dataGrid, context.AutoLoadStateName);
            }
        }

        private static async void OnDataGridUnloaded(object sender, RoutedEventArgs e)
        {
            var dataGrid = sender as DataGrid;
            if (!_gridContexts.TryGetValue(dataGrid, out var context))
                return;

            // Auto-save state if specified
            if (!string.IsNullOrEmpty(context.AutoSaveStateName))
            {
                await SaveStateAsync(dataGrid, context.AutoSaveStateName);
            }
        }

        private static void OnDataGridChanged(object sender, DataGridColumnEventArgs e)
        {
            var dataGrid = sender as DataGrid;
            ScheduleAutoSave(dataGrid);
        }

        private static void OnDataGridSorting(object sender, DataGridSortingEventArgs e)
        {
            var dataGrid = sender as DataGrid;
            // Delay auto-save to allow sorting to complete
            dataGrid.Dispatcher.BeginInvoke(new Action(() => ScheduleAutoSave(dataGrid)),
                DispatcherPriority.Background);
        }

        private static void SubscribeToViewModelEvents(DataGrid dataGrid, GridStateContext context)
        {
            // Subscribe to ViewModel events for filter changes
            if (dataGrid.DataContext is INotifyPropertyChanged viewModel)
            {
                // Store weak reference to avoid memory leaks
                context.ViewModelPropertyChangedHandler = (sender, e) =>
                {
                    // Handle filter-related property changes
                    if (e.PropertyName?.Contains("Filter") == true)
                    {
                        ScheduleAutoSave(dataGrid);
                    }
                };

                viewModel.PropertyChanged += context.ViewModelPropertyChangedHandler;
            }
        }

        private static void UnsubscribeFromViewModelEvents(DataGrid dataGrid, GridStateContext context)
        {
            if (dataGrid.DataContext is INotifyPropertyChanged viewModel &&
                context.ViewModelPropertyChangedHandler != null)
            {
                viewModel.PropertyChanged -= context.ViewModelPropertyChangedHandler;
            }
        }

        private static void ScheduleAutoSave(DataGrid dataGrid)
        {
            if (!_gridContexts.TryGetValue(dataGrid, out var context) ||
                string.IsNullOrEmpty(context.AutoSaveStateName) ||
                !context.Options.AutoSave)
                return;

            var state = CaptureCurrentState(dataGrid, context.GridId, context.AutoSaveStateName);
            context.StateManager.ScheduleAutoSave(context.GridId, context.AutoSaveStateName, state);
        }

        #endregion

        #region Helper Methods

        private static DataGridState CaptureCurrentState(DataGrid dataGrid, string gridId, string stateName)
        {
            if (dataGrid is DynamicDataGrid dynamicGrid)
            {
                return GridStateSerializer.CaptureState(dynamicGrid, gridId, stateName);
            }
            else
            {
                return GridStateSerializer.CaptureState(dataGrid, gridId, stateName);
            }
        }

        private static bool ApplyStateToGrid(DataGrid dataGrid, DataGridState state, GridStateOptions options)
        {
            if (dataGrid is DynamicDataGrid dynamicGrid)
            {
                return GridStateSerializer.ApplyState(dynamicGrid, state, options);
            }
            else
            {
                return GridStateSerializer.ApplyState(dataGrid, state, options);
            }
        }

        #endregion
    }
}