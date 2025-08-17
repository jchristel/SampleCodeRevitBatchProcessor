using System;

namespace duHastNet.Utils.WPF.Interfaces
{
    // <summary>
    /// Event arguments for grid state events
    /// </summary>
    public class GridStateEventArgs : EventArgs
    {
        public string GridId { get; set; }
        public string StateName { get; set; }
        public IGridState State { get; set; }
        public Exception Exception { get; set; }
        public bool Success { get; set; }

        public GridStateEventArgs(string gridId, string stateName, IGridState state = null)
        {
            GridId = gridId;
            StateName = stateName;
            State = state;
            Success = true;
        }

        public GridStateEventArgs(string gridId, string stateName, Exception exception)
        {
            GridId = gridId;
            StateName = stateName;
            Exception = exception;
            Success = false;
        }
    }
}

