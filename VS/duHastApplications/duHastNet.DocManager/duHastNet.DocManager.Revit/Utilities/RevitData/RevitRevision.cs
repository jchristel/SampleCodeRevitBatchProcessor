//
//License:
//
//
// Revit Batch Processor Sample Code
//
// BSD License
// Copyright 2026, Jan Christel
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

namespace duHastNet.DocManager.Revit.Utilities.RevitData
{
    /// <summary>
    /// A simple class to represent a Revit revision, with a date and description.
    /// </summary>
    public class RevitRevision
    {
        public Int64 RevitRevisionElementId { get; set; }
        public string RevisionDate { get; set; }
        public string RevisionDescription { get; set; }
        public RevitRevision(Int64 revitRevisionElementId, string revisionDate, string revisionDescription) 
        { 
            RevitRevisionElementId = revitRevisionElementId;
            RevisionDate = revisionDate;
            RevisionDescription = revisionDescription;
        }

        public RevitRevision() 
        { 
            RevitRevisionElementId = 0;
            RevisionDate = string.Empty;
            RevisionDescription = string.Empty;
        }

        public bool Conflicts(RevitRevision other)
        {
            //check for conflict by element id, as there cannot be two revisions with the same element id in Revit.
            return RevitRevisionElementId == other.RevitRevisionElementId;
        }

        public override string ToString()
        {
                return $"Revision Element Id: {RevitRevisionElementId}, Revision Date: {RevisionDate}, Revision Description: {RevisionDescription}";
        }
    }
}
