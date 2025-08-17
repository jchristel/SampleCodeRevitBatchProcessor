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

using System;
using System.Collections.Generic;

namespace duHastNet.Utils.WPF.Interfaces
{
    /// <summary>
    /// Represents the state of a grid that can be saved and restored
    /// This interface allows the NavigationStore to work with grid state without depending on specific implementations
    /// </summary>
    public interface IGridState
    {
        /// <summary>
        /// Unique identifier for the grid that this state belongs to
        /// </summary>
        string GridId { get; set; }

        /// <summary>
        /// Human-readable name for this state
        /// </summary>
        string StateName { get; set; }

        /// <summary>
        /// When this state was created
        /// </summary>
        DateTime CreatedDate { get; set; }

        /// <summary>
        /// When this state was last modified
        /// </summary>
        DateTime LastModified { get; set; }

        /// <summary>
        /// Version of the state format for compatibility
        /// </summary>
        string Version { get; set; }

        /// <summary>
        /// Gets a summary description of this state for display purposes
        /// </summary>
        /// <returns>Human-readable summary of the state</returns>
        string GetSummary();

        /// <summary>
        /// Creates a deep copy of this state
        /// </summary>
        /// <returns>A new instance that is a copy of this state</returns>
        IGridState Clone();

        /// <summary>
        /// Serializes this state to a string for persistence
        /// </summary>
        /// <returns>Serialized string representation</returns>
        string Serialize();

        /// <summary>
        /// Deserializes state from a string
        /// </summary>
        /// <param name="serializedState">Serialized state string</param>
        /// <returns>True if deserialization was successful</returns>
        bool Deserialize(string serializedState);

        /// <summary>
        /// Validates that this state is internally consistent
        /// </summary>
        /// <returns>List of validation errors, empty if valid</returns>
        List<string> Validate();

        /// <summary>
        /// Additional metadata that can be used by specific implementations
        /// </summary>
        Dictionary<string, object> Metadata { get; set; }
    }
}