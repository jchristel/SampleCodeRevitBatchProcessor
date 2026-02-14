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

namespace duHastNet.Utils.WPF.Interfaces
{
    // <summary>
    /// Interface for ViewModels that support grid state management
    /// </summary>
    public interface IGridStateSupport
    {
        /// <summary>
        /// Whether state management is enabled for this ViewModel
        /// </summary>
        bool StateManagementEnabled { get; }

        /// <summary>
        /// Creates a state object representing the current state of the ViewModel's grid
        /// </summary>
        /// <returns>Current grid state, or null if state cannot be captured</returns>
        IGridState CreateStateFromViewModel();

        /// <summary>
        /// Applies a saved state to the ViewModel's grid
        /// </summary>
        /// <param name="state">The state to apply</param>
        /// <returns>True if state was successfully applied</returns>
        bool ApplyStateToViewModel(IGridState state);

        /// <summary>
        /// Gets a unique identifier for this ViewModel's grid state
        /// This can be used to distinguish between different grid configurations
        /// </summary>
        /// <returns>Unique state identifier</returns>
        string GetGridStateId();
    }
}
