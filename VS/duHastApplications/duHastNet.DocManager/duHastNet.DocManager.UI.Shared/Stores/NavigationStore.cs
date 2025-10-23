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

using CommunityToolkit.Mvvm.ComponentModel;
using duHastNet.DocManager.UI.Shared.Interfaces;

namespace duHastNet.DocManager.UI.Shared.Stores
{
    /// <summary>
    /// Shared navigation store for use across Standalone and Revit-integrated versions
    /// Manages ViewModels and navigation with state management
    /// </summary>
    public partial class NavigationStore : ObservableObject
    {
        #region Observable Properties

        /// <summary>
        /// Gets or sets the current ViewModel for navigation
        /// </summary>
        [ObservableProperty]
        private ObservableObject? _currentViewModel;

        #endregion

        #region Lifecycle Management

        /// <summary>
        /// Called when CurrentViewModel is about to change
        /// Handles cleanup of the previous ViewModel
        /// </summary>
        partial void OnCurrentViewModelChanging(ObservableObject? value)
        {
            // Call ICloseable.OnClosing() if implemented
            if (CurrentViewModel is ICloseable closeable)
            {
                System.Diagnostics.Debug.WriteLine(
                    $"Calling OnClosing() on {CurrentViewModel.GetType().Name}");
                closeable.OnClosing();
            }

            // Dispose if implementing IDisposable
            if (CurrentViewModel is IDisposable disposable)
            {
                System.Diagnostics.Debug.WriteLine(
                    $"Disposing {CurrentViewModel.GetType().Name}");
                disposable.Dispose();
            }
        }

        /// <summary>
        /// Notify the current ViewModel that the application/window is closing
        /// </summary>
        public void NotifyClosing()
        {
            if (CurrentViewModel is ICloseable closeable)
            {
                closeable.OnClosing();
            }

            if (CurrentViewModel is IDisposable disposable)
            {
                disposable.Dispose();
            }
        }

        #endregion

        #region Navigation Methods

        /// <summary>
        /// Navigates to a new ViewModel instance using a factory
        /// </summary>
        /// <typeparam name="T">Type of ViewModel to navigate to</typeparam>
        /// <param name="viewModelFactory">Factory function to create the ViewModel</param>
        public void NavigateTo<T>(Func<T> viewModelFactory) where T : ObservableObject
        {
            if (viewModelFactory == null)
                throw new ArgumentNullException(nameof(viewModelFactory));

            CurrentViewModel = viewModelFactory();
        }

        /// <summary>
        /// Navigates directly to a ViewModel instance
        /// </summary>
        /// <param name="viewModel">The ViewModel to navigate to</param>
        public void NavigateTo(ObservableObject? viewModel)
        {
            CurrentViewModel = viewModel;
        }

        /// <summary>
        /// Clears the current ViewModel (navigates to null)
        /// </summary>
        public void ClearNavigation()
        {
            CurrentViewModel = null;
        }

        #endregion

        #region Query Methods

        /// <summary>
        /// Checks if the navigation store currently has a ViewModel
        /// </summary>
        public bool HasCurrentViewModel => CurrentViewModel != null;

        /// <summary>
        /// Gets the type of the current ViewModel (for debugging/logging)
        /// </summary>
        public Type? CurrentViewModelType => CurrentViewModel?.GetType();

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
            info.AppendLine($"Current ViewModel: {CurrentViewModel?.GetType().Name ?? "None"}");
            info.AppendLine($"Has ViewModel: {HasCurrentViewModel}");

            if (CurrentViewModel != null)
            {
                info.AppendLine($"ViewModel Type: {CurrentViewModelType?.FullName}");
            }

            return info.ToString();
        }

        #endregion
    }
}
