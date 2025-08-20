using duHastNet.Utils.WPF.Interfaces;
using duHastNet.Utils.WPF.States;
using System;
using System.Collections.Generic;

namespace duHastNet.Utils.WPF.Stores
{
    /// <summary>
    /// Simplified state repository - stores and retrieves ViewModel states without automatic coordination
    /// Also provides basic navigation functionality
    /// </summary>
    public class NavigationStore
    {
        #region Private Fields

        private readonly StateManager _stateManager;
        private readonly object _stateLock = new object();
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

        /// <summary>
        /// Fired when state operations occur (optional for debugging/logging)
        /// </summary>
        public event EventHandler<GridStateEventArgs> StateOperationCompleted;

        #endregion

        #region Constructor

        /// <summary>
        /// Initializes a new instance of NavigationStore as a simple state repository
        /// </summary>
        /// <param name="stateManager">Optional state manager. If null, a default one will be created.</param>
        public NavigationStore(StateManager stateManager = null)
        {
            _stateManager = stateManager ?? new StateManager();
        }

        #endregion

        #region Core State Management Methods

        /// <summary>
        /// Saves state for a specific ViewModel
        /// </summary>
        /// <param name="viewModel">The ViewModel requesting the save</param>
        /// <param name="state">The state to save</param>
        public void SaveViewModelState(IGridStateSupport viewModel, IGridState state)
        {
            if (viewModel == null || state == null)
                return;

            try
            {
                var stateKey = viewModel.GetGridStateId();
                if (string.IsNullOrEmpty(stateKey))
                {
                    System.Diagnostics.Debug.WriteLine($"Cannot save state: ViewModel {viewModel.GetType().Name} returned empty state key");
                    return;
                }

                // Ensure state has proper metadata
                state.GridId = stateKey;
                state.StateName = "Default";
                state.LastModified = DateTime.Now;

                // Save to state manager
                _stateManager.SaveState(stateKey, state);

                System.Diagnostics.Debug.WriteLine($"Saved state for ViewModel: {viewModel.GetType().Name} with key: {stateKey}");

                // Raise success event
                OnStateOperationCompleted(new GridStateEventArgs(state.GridId, state.StateName, state));
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error saving state for {viewModel.GetType().Name}: {ex.Message}");

                // Raise error event
                OnStateOperationCompleted(new GridStateEventArgs(
                    viewModel.GetGridStateId() ?? "Unknown",
                    "Default",
                    ex));
            }
        }

        /// <summary>
        /// Loads state for a specific ViewModel
        /// </summary>
        /// <param name="viewModel">The ViewModel requesting the load</param>
        /// <returns>The saved state, or null if not found</returns>
        public IGridState LoadViewModelState(IGridStateSupport viewModel)
        {
            if (viewModel == null)
                return null;

            var stateKey = viewModel.GetGridStateId();
            return LoadViewModelState(stateKey);
        }

        /// <summary>
        /// Loads state by state key
        /// </summary>
        /// <param name="stateKey">The state key to load</param>
        /// <returns>The saved state, or null if not found</returns>
        public IGridState LoadViewModelState(string stateKey)
        {
            if (string.IsNullOrEmpty(stateKey))
                return null;

            try
            {
                var state = _stateManager.LoadState(stateKey);

                if (state != null)
                {
                    System.Diagnostics.Debug.WriteLine($"Loaded state for key: {stateKey}");
                }
                else
                {
                    System.Diagnostics.Debug.WriteLine($"No saved state found for key: {stateKey}");
                }

                return state;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error loading state for key {stateKey}: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Checks if a state exists for the specified ViewModel
        /// </summary>
        /// <param name="viewModel">The ViewModel to check</param>
        /// <returns>True if a state exists</returns>
        public bool HasViewModelState(IGridStateSupport viewModel)
        {
            if (viewModel == null)
                return false;

            var stateKey = viewModel.GetGridStateId();
            return HasViewModelState(stateKey);
        }

        /// <summary>
        /// Checks if a state exists for the specified state key
        /// </summary>
        /// <param name="stateKey">The state key to check</param>
        /// <returns>True if a state exists</returns>
        public bool HasViewModelState(string stateKey)
        {
            if (string.IsNullOrEmpty(stateKey))
                return false;

            return _stateManager.StateExists(stateKey);
        }

        /// <summary>
        /// Clears state for a specific ViewModel
        /// </summary>
        /// <param name="viewModel">The ViewModel whose state should be cleared</param>
        public void ClearViewModelState(IGridStateSupport viewModel)
        {
            if (viewModel == null)
                return;

            var stateKey = viewModel.GetGridStateId();
            ClearViewModelState(stateKey);
        }

        /// <summary>
        /// Clears state for a specific state key
        /// </summary>
        /// <param name="stateKey">The state key to clear</param>
        public void ClearViewModelState(string stateKey)
        {
            if (string.IsNullOrEmpty(stateKey))
                return;

            _stateManager.ClearState(stateKey);
            System.Diagnostics.Debug.WriteLine($"Cleared state for key: {stateKey}");
        }

        /// <summary>
        /// Clears all saved states
        /// </summary>
        public void ClearAllStates()
        {
            _stateManager.ClearAllStates();
            System.Diagnostics.Debug.WriteLine("Cleared all saved states");
        }

        #endregion

        #region Navigation Methods

        /// <summary>
        /// Notify the current ViewModel that the application/window is closing
        /// </summary>
        public void NotifyClosing()
        {
            // In DocumentSelectionViewModel.OnClosing()
            System.Diagnostics.Debug.WriteLine("Navigation Store.NotifyClosing() called");

            if (_currentViewModel is ICloseable closeable)
            {
                closeable.OnClosing();
            }
        }

        #endregion

        #region Settings Integration

        /// <summary>
        /// Loads states from application settings
        /// Called during application startup
        /// </summary>
        /// <param name="gridStatesFromSettings">Serialized states from settings</param>
        public void LoadStatesFromSettings(Dictionary<string, string> gridStatesFromSettings)
        {
            if (gridStatesFromSettings == null)
                return;

            var statesToLoad = new Dictionary<string, IGridState>();

            foreach (var kvp in gridStatesFromSettings)
            {
                try
                {
                    if (!string.IsNullOrEmpty(kvp.Value))
                    {
                        var state = new States.GridState();
                        if (state.Deserialize(kvp.Value))
                        {
                            statesToLoad[kvp.Key] = state;
                        }
                    }
                }
                catch (Exception ex)
                {
                    System.Diagnostics.Debug.WriteLine($"Error loading state for {kvp.Key}: {ex.Message}");
                }
            }

            if (statesToLoad.Count > 0)
            {
                _stateManager.LoadStatesFromExternal(statesToLoad);
                System.Diagnostics.Debug.WriteLine($"Loaded {statesToLoad.Count} states from settings");
            }
        }

        /// <summary>
        /// Gets states formatted for saving to application settings
        /// Called during application shutdown
        /// </summary>
        /// <returns>Dictionary of serialized states for settings</returns>
        public Dictionary<string, string> GetStatesForSettings()
        {
            var settingsData = new Dictionary<string, string>();
            var allStates = _stateManager.GetAllStates();

            foreach (var kvp in allStates)
            {
                try
                {
                    var serialized = kvp.Value?.Serialize();
                    if (!string.IsNullOrEmpty(serialized))
                    {
                        settingsData[kvp.Key] = serialized;
                    }
                }
                catch (Exception ex)
                {
                    System.Diagnostics.Debug.WriteLine($"Error serializing state for {kvp.Key}: {ex.Message}");
                }
            }

            System.Diagnostics.Debug.WriteLine($"Prepared {settingsData.Count} states for settings");
            return settingsData;
        }

        #endregion

        #region Utility and Debug Methods

        /// <summary>
        /// Gets the number of stored states
        /// </summary>
        public int StoredStateCount
        {
            get
            {
                lock (_stateLock)
                {
                    return _stateManager.GetAllStates().Count;
                }
            }
        }

        /// <summary>
        /// Gets all saved states (for debugging/inspection)
        /// </summary>
        /// <returns>Dictionary of all saved states</returns>
        public Dictionary<string, IGridState> GetAllStates()
        {
            return _stateManager.GetAllStates();
        }

        /// <summary>
        /// Gets debug information about stored states
        /// </summary>
        /// <returns>Debug information string</returns>
        public string GetDebugInfo()
        {
            var info = new System.Text.StringBuilder();
            info.AppendLine("=== NAVIGATION STORE DEBUG ===");
            info.AppendLine($"Stored States: {StoredStateCount}");

            var allStates = _stateManager.GetAllStates();
            foreach (var kvp in allStates)
            {
                info.AppendLine($"  - {kvp.Key}: {kvp.Value?.GetSummary() ?? "null"}");
            }

            return info.ToString();
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

        /// <summary>
        /// Raises the StateOperationCompleted event
        /// </summary>
        /// <param name="args">Event arguments</param>
        protected virtual void OnStateOperationCompleted(GridStateEventArgs args)
        {
            StateOperationCompleted?.Invoke(this, args);
        }

        #endregion
    }
}