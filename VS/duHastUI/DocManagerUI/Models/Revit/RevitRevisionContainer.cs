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

using duHastNet.UI.DocManagerUI.Utils.RevitData;

namespace duHastNet.UI.DocManagerUI.Models.Revit
{
    public class RevitRevisionContainer
    {
        private List<RevitRevision> _revisions { get; }

        public RevitRevisionContainer()
        {
            _revisions = new List<RevitRevision>();
        }

        public void AddRevision(RevitRevision revision)
        {
            if (revision == null)
            {
                throw new ArgumentNullException(nameof(revision), "Revision cannot be null.");
            }
            // check if a revision with this ID already exists
            foreach (var existingRevision in _revisions)
            {
                if (existingRevision.RevitRevisionElementId == revision.RevitRevisionElementId)
                {
                    throw new ArgumentException($"A revision with the ID '{revision.RevitRevisionElementId}' already exists.", nameof(revision));
                }
            }

            _revisions.Add(revision);
        }

        public RevitRevision GetRevisionByRevitId(Int64 revisionId)
        {
            if (revisionId <= 0)
            {
                throw new ArgumentException("Revision ID must be positive.", nameof(revisionId));
            }
            foreach (var revision in _revisions)
            {
                if (revision.RevitRevisionElementId == revisionId)
                {
                    return revision;
                }
            }
            throw new KeyNotFoundException($"No revision found with the ID '{revisionId}'.");
        }
        public List<RevitRevision> GetRevisions()
        {
            return _revisions;
        }
    }
}
