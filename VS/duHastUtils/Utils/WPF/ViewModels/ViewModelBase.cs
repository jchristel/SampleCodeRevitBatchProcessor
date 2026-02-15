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
using duHastNet.Utils.WPF.Interfaces;
using System;
using System.Collections.Generic;

namespace duHastNet.Utils.WPF.ViewModels
{
    /// <summary>
    /// Base class for ViewModels using Community Toolkit.
    /// Provides automatic hierarchical cleanup via ICloseable and IDisposable patterns.
    /// </summary>
    public partial class ViewModelBase : ObservableObject, ICloseable, IDisposable
    {
        #region ICloseable

        /// <summary>
        /// List of child ViewModels that will be automatically cleaned up
        /// </summary>
        protected List<ICloseable> _childViewModels = new List<ICloseable>();

        /// <summary>
        /// Registers a child ViewModel for automatic cleanup when this ViewModel closes
        /// </summary>
        /// <param name="child">The child ViewModel to register</param>
        protected void RegisterChild(ICloseable child)
        {
            _childViewModels.Add(child);
        }

        /// <summary>
        /// Called when the ViewModel is being navigated away from or closed.
        /// Performs UI-related cleanup and propagates to child ViewModels.
        /// </summary>
        public virtual void OnClosing()
        {
            // Close all children first
            foreach (var child in _childViewModels)
            {
                child.OnClosing();
            }
            _childViewModels.Clear();
        }

        #endregion

        #region IDisposable

        private bool _disposed = false;

        /// <summary>
        /// Disposes of resources used by this ViewModel.
        /// Propagates disposal to child ViewModels that implement IDisposable.
        /// </summary>
        public virtual void Dispose()
        {
            if (_disposed)
                return;

            // Dispose child ViewModels that implement IDisposable
            foreach (var child in _childViewModels)
            {
                if (child is IDisposable disposable)
                {
                    disposable.Dispose();
                }
            }

            _disposed = true;
        }

        #endregion
    }
}