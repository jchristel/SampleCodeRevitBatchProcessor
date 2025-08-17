// File: Utils/WPF/Stores/StateManager.cs
using duHastNet.Utils.WPF.Interfaces;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace duHastNet.Utils.WPF.Stores
{
    public class StateManager
    {
        private readonly Dictionary<string, IGridState> _stateCache;
        private readonly object _lockObject = new object();

        public StateManager()
        {
            _stateCache = new Dictionary<string, IGridState>();
        }

        public Task<bool> SaveState(string gridId, IGridState state)
        {
            try
            {
                if (string.IsNullOrEmpty(gridId) || state == null)
                    return Task.FromResult(false);

                state.GridId = gridId;
                state.StateName = "Default";
                state.LastModified = DateTime.Now;

                lock (_lockObject)
                {
                    _stateCache[gridId] = state;
                }

                return Task.FromResult(true);
            }
            catch
            {
                return Task.FromResult(false);
            }
        }

        public Task<IGridState> LoadState(string gridId)
        {
            if (string.IsNullOrEmpty(gridId))
                return Task.FromResult<IGridState>(null);

            lock (_lockObject)
            {
                _stateCache.TryGetValue(gridId, out var state);
                return Task.FromResult(state);
            }
        }

        public bool StateExists(string gridId)
        {
            if (string.IsNullOrEmpty(gridId))
                return false;

            lock (_lockObject)
            {
                return _stateCache.ContainsKey(gridId);
            }
        }

        public bool ClearState(string gridId)
        {
            if (string.IsNullOrEmpty(gridId))
                return false;

            lock (_lockObject)
            {
                return _stateCache.Remove(gridId);
            }
        }

        public void ClearAllStates()
        {
            lock (_lockObject)
            {
                _stateCache.Clear();
            }
        }

        public Dictionary<string, IGridState> GetAllStates()
        {
            lock (_lockObject)
            {
                return new Dictionary<string, IGridState>(_stateCache);
            }
        }

        public void LoadStatesFromExternal(Dictionary<string, IGridState> externalStates)
        {
            if (externalStates == null) return;

            lock (_lockObject)
            {
                foreach (var kvp in externalStates)
                {
                    if (kvp.Value != null)
                    {
                        _stateCache[kvp.Key] = kvp.Value;
                    }
                }
            }
        }

        public string GetDebugInfo()
        {
            lock (_lockObject)
            {
                return $"StateManager: {_stateCache.Count} stored states";
            }
        }
    }
}