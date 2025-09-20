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
namespace duHastNet.DocManager.Core.Models.Config
{
    /// <summary>
    /// Document data for import operations
    /// </summary>
    public class DocumentImportData
    {
        /// <summary>
        /// Document identifier (alphanumeric)
        /// </summary>
        public string Number { get; set; } = string.Empty;

        /// <summary>
        /// Full document name
        /// </summary>
        public string Name { get; set; } = string.Empty;

        /// <summary>
        /// Revision indicator (can be number, character, or both)
        /// </summary>
        public string Revision { get; set; } = string.Empty;

        /// <summary>
        /// Date when this document revision was issued
        /// </summary>
        public DateTime RevisionDate { get; set; }

        /// <summary>
        /// Optional description for the revision batch
        /// </summary>
        public string? RevisionDescription { get; set; }

        /// <summary>
        /// Custom properties for this document
        /// </summary>
        public Dictionary<string, string> CustomProperties { get; set; } = new();
    }
}
