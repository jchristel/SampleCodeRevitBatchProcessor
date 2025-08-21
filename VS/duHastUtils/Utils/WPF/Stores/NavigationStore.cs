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
using System;

namespace duHastNet.Utils.WPF.Stores
{
    /// <summary>
    /// Pure navigation store - manages ViewModels and navigation without state management
    /// </summary>
    public class NavigationStore
    {
        #region Private Fields

        private ViewModels.ViewModelBase _currentViewModel;

        #endregion

        #region Navigation Properties

        /// <summary>
        /// Gets or sets the current ViewModel (for navigation)
        /// </summary>
        public ViewModels.ViewModelBase CurrentViewModel
        {
            get => _currentViewModel;
            set
            {
                _currentViewModel = value;
                OnCurrentViewModelChanged();
            }
        }

        #endregion

        #region Events

        /// <summary>
        /// Fired when the current ViewModel changes (for navigation)
        /// </summary>
        public event Action CurrentViewModelChanged;

        #endregion

        #region Navigation Methods

        /// <summary>
        /// Notify the current ViewModel that the application/window is closing
        /// </summary>
        public void NotifyClosing()
        {
            System.Diagnostics.Debug.WriteLine("NavigationStore.NotifyClosing() called");
            System.Diagnostics.Debug.WriteLine($"CurrentViewModel is: {_currentViewModel?.GetType().Name ?? "null"}");

            if (_currentViewModel is ICloseable closeable)
            {
                System.Diagnostics.Debug.WriteLine($"Calling OnClosing() on {_currentViewModel.GetType().Name}");
                closeable.OnClosing();
                System.Diagnostics.Debug.WriteLine($"OnClosing() completed for {_currentViewModel.GetType().Name}");
            }
            else
            {
                System.Diagnostics.Debug.WriteLine("CurrentViewModel does not implement ICloseable or is null");
            }
        }

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

        #endregion

        #region Event Helpers

        /// <summary>
        /// Raises the CurrentViewModelChanged event
        /// </summary>
        protected virtual void OnCurrentViewModelChanged()
        {
            CurrentViewModelChanged?.Invoke();
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

            if (_currentViewModel != null)
            {
                info.AppendLine($"ViewModel Type: {CurrentViewModelType.FullName}");
            }

            return info.ToString();
        }

        #endregion
    }
}