
using duHastNet.Utils.WPF.Interfaces;
using System;
using System.Collections.Generic;
using Newtonsoft.Json;

namespace duHastNet.Utils.WPF.States
{
    public class GridState : IGridState
    {
        public string GridId { get; set; }
        public string StateName { get; set; }
        public DateTime CreatedDate { get; set; }
        public DateTime LastModified { get; set; }
        public string Version { get; set; } = "1.0";
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();

        public string GetSummary()
        {
            return $"Grid: {GridId}, State: {StateName}";
        }

        public IGridState Clone()
        {
            var serialized = Serialize();
            var clone = new GridState();
            clone.Deserialize(serialized);
            return clone;
        }

        public string Serialize()
        {
            try
            {
                return JsonConvert.SerializeObject(this);
            }
            catch
            {
                return null;
            }
        }

        public bool Deserialize(string serializedState)
        {
            try
            {
                var deserialized = JsonConvert.DeserializeObject<GridState>(serializedState);
                if (deserialized != null)
                {
                    GridId = deserialized.GridId;
                    StateName = deserialized.StateName;
                    CreatedDate = deserialized.CreatedDate;
                    LastModified = deserialized.LastModified;
                    Version = deserialized.Version;
                    Metadata = deserialized.Metadata;
                    return true;
                }
            }
            catch
            {
                // Ignore errors
            }
            return false;
        }

        public List<string> Validate()
        {
            var errors = new List<string>();
            if (string.IsNullOrEmpty(GridId))
                errors.Add("GridId is required");
            return errors;
        }
    }
}