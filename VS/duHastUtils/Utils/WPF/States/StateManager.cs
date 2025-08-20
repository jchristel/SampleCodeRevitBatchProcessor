// File: Utils/WPF/Stores/StateManager.cs
using duHastNet.Utils.WPF.Interfaces;
using System;
using System.Collections.Generic;

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

        public bool SaveState(string gridId, IGridState state)
        {
            try
            {
                if (string.IsNullOrEmpty(gridId) || state == null)
                    return false;

                state.GridId = gridId;
                state.StateName = "Default";
                state.LastModified = DateTime.Now;

                lock (_lockObject)
                {
                    _stateCache[gridId] = state;
                }

                return true;
            }
            catch
            {
                return false;
            }
        }

        public IGridState LoadState(string gridId)
        {
            if (string.IsNullOrEmpty(gridId))
                return null;

            lock (_lockObject)
            {
                _stateCache.TryGetValue(gridId, out var state);
                return state;
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