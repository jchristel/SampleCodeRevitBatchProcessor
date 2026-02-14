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