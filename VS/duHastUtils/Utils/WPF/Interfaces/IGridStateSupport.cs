using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

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
