using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace duHastNet.DocManager.Core.Models.Results
{
    /// <summary>
    /// Result of a save operation
    /// </summary>
    public class SaveResult : ResultBase
    {
        /// <summary>
        /// Indicates whether the save was successful
        /// </summary>
        public bool IsSaveSuccessful { get; set; }

        /// <summary>
        /// Path to the file that was saved
        /// </summary>
        public string? FilePath { get; set; }

        /// <summary>
        /// Implementation of abstract Success property - maps to IsSaveSuccessful
        /// </summary>
        public override bool Success
        {
            get => IsSaveSuccessful;
            set => IsSaveSuccessful = value;
        }

        /// <summary>
        /// Initializes a new instance of SaveResult
        /// </summary>
        public SaveResult()
        {
            Message = "Save operation completed";
        }
    }
}
