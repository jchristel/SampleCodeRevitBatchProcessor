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

using duHastNet.Utils.WPF.Interfaces;
using duHastNet.Utils.WPF.States;
using System;

namespace duHastNet.Utils.WPF.Stores
{
    /// <summary>
    /// Manages navigation between ViewModels with simple state persistence (one state per ViewModel)
    /// </summary>
    public partial class NavigationStore
    {
        #region Core Navigation Fields

        private ViewModels.ViewModelBase _currentViewModel;

        #endregion

        #region State Management Fields (shared with partial class)

        // These fields are used by both core navigation and state management
        internal readonly StateManager _stateManager;
        internal readonly object _stateLock = new object();

        #endregion

        #region Core Navigation Properties

        /// <summary>
        /// Gets or sets the current ViewModel, automatically handling state save/load
        /// </summary>
        public ViewModels.ViewModelBase CurrentViewModel
        {
            get => _currentViewModel;
            set
            {
                // Save state of outgoing ViewModel before switching
                if (_currentViewModel != null)
                {
                    SaveCurrentViewModelState();
                }

                _currentViewModel = value;
                OnCurrentViewModelChanged();

                // Load state for incoming ViewModel after switching
                if (_currentViewModel != null)
                {
                    LoadCurrentViewModelState();
                }
            }
        }

        #endregion

        #region Events

        /// <summary>
        /// Fired when the current ViewModel changes
        /// </summary>
        public event Action CurrentViewModelChanged;

        /// <summary>
        /// Fired when state operations occur
        /// </summary>
        public event EventHandler<GridStateEventArgs> StateOperationCompleted;

        #endregion

        #region Constructor

        /// <summary>
        /// Initializes a new instance of NavigationStore with simple state management
        /// </summary>
        /// <param name="stateManager">Optional state manager. If null, a default one will be created.</param>
        public NavigationStore(StateManager stateManager = null)
        {
            _stateManager = stateManager ?? new StateManager();
        }

        #endregion

        #region Core Navigation Methods

        /// <summary>
        /// Raises the CurrentViewModelChanged event
        /// </summary>
        private void OnCurrentViewModelChanged()
        {
            CurrentViewModelChanged?.Invoke();
        }

        /// <summary>
        /// Notify all nested view models of closing event and save final state
        /// </summary>
        public void NotifyClosing()
        {
            // Save current state before closing
            SaveCurrentViewModelState();

            if (_currentViewModel is ICloseable closeable)
            {
                closeable.OnClosing();
            }
        }

        /// <summary>
        /// Gets a unique key for the current ViewModel's state
        /// </summary>
        internal string GetCurrentViewModelKey()
        {
            if (_currentViewModel == null)
                return null;

            // If ViewModel supports state management, use its custom ID
            if (_currentViewModel is IGridStateSupport gridStateSupport)
            {
                var customId = gridStateSupport.GetGridStateId();
                if (!string.IsNullOrEmpty(customId))
                    return customId;
            }

            // Fall back to type name
            return _currentViewModel.GetType().Name;
        }

        /// <summary>
        /// Forces a save of the current ViewModel's state
        /// </summary>
        public void ForceSaveCurrentState()
        {
            SaveCurrentViewModelState();
        }

        #endregion

        #region Navigation Helper Methods

        /// <summary>
        /// Navigates to a new ViewModel instance
        /// </summary>
        /// <typeparam name="T">Type of ViewModel to navigate to</typeparam>
        /// <param name="viewModelFactory">Factory function to create the ViewModel</param>
        public void NavigateTo<T>(Func<T> viewModelFactory) where T : ViewModels.ViewModelBase
        {
            if (viewModelFactory == null)
                throw new ArgumentNullException(nameof(viewModelFactory));

            CurrentViewModel = viewModelFactory();
        }

        /// <summary>
        /// Navigates directly to a ViewModel instance
        /// </summary>
        /// <param name="viewModel">The ViewModel to navigate to</param>
        public void NavigateTo(ViewModels.ViewModelBase viewModel)
        {
            CurrentViewModel = viewModel;
        }

        /// <summary>
        /// Checks if the navigation store currently has a ViewModel
        /// </summary>
        public bool HasCurrentViewModel => _currentViewModel != null;

        /// <summary>
        /// Gets the type of the current ViewModel (for debugging/logging)
        /// </summary>
        public Type CurrentViewModelType => _currentViewModel?.GetType();

        /// <summary>
        /// Clears the current ViewModel (navigates to null)
        /// </summary>
        public void ClearNavigation()
        {
            CurrentViewModel = null;
        }

        /// <summary>
        /// Checks if the current ViewModel supports state management
        /// </summary>
        public bool CurrentViewModelSupportsState => _currentViewModel is IGridStateSupport;

        #endregion

        #region State Event Helpers

        /// <summary>
        /// Raises the StateOperationCompleted event
        /// </summary>
        /// <param name="args">Event arguments</param>
        protected virtual void OnStateOperationCompleted(GridStateEventArgs args)
        {
            StateOperationCompleted?.Invoke(this, args);
        }

        #endregion

        #region Debug Information

        /// <summary>
        /// Gets debug information about the current navigation state
        /// </summary>
        /// <returns>Debug information string</returns>
        public string GetNavigationDebugInfo()
        {
            var info = new System.Text.StringBuilder();
            info.AppendLine("=== NAVIGATION STORE DEBUG ===");
            info.AppendLine($"Current ViewModel: {_currentViewModel?.GetType().Name ?? "None"}");
            info.AppendLine($"Has ViewModel: {HasCurrentViewModel}");
            info.AppendLine($"Supports State: {CurrentViewModelSupportsState}");

            if (_currentViewModel != null)
            {
                info.AppendLine($"ViewModel Type: {CurrentViewModelType.FullName}");
                info.AppendLine($"State Key: {GetCurrentViewModelKey()}");

                if (_currentViewModel is IGridStateSupport stateSupport)
                {
                    info.AppendLine($"State Management Enabled: {stateSupport.StateManagementEnabled}");
                    info.AppendLine($"Grid State ID: {stateSupport.GetGridStateId()}");
                }
            }

            return info.ToString();
        }

        #endregion

        /// <summary>
        /// Saves the current ViewModel's grid state (if it supports state management)
        /// </summary>
        private void SaveCurrentViewModelState()
        {
            try
            {
                var key = GetCurrentViewModelKey();
                if (string.IsNullOrEmpty(key))
                    return;

                // Check if current ViewModel supports state management using the interface
                if (_currentViewModel is IGridStateSupport gridStateSupport &&
                    gridStateSupport.StateManagementEnabled)
                {
                    var state = gridStateSupport.CreateStateFromViewModel();
                    if (state != null)
                    {
                        state.StateName = "Default";
                        state.LastModified = DateTime.Now;

                        // Use the existing SaveViewModelState method
                        SaveViewModelState(key, state);

                        // Raise success event
                        OnStateOperationCompleted(new GridStateEventArgs(state.GridId, state.StateName, state));
                    }
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error saving ViewModel state: {ex.Message}");

                // Raise error event
                var errorArgs = new GridStateEventArgs(GetCurrentViewModelKey() ?? "Unknown", "Default")
                {
                    Exception = ex,
                    Success = false
                };
                OnStateOperationCompleted(errorArgs);
            }
        }
    }
}