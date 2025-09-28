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


namespace duHastNet.DocManager.Core.Models
{
    public class RevisionContainer
    {
        private List<Revision> _revisions;

        #region get revisions

        /// <summary>
        /// returns all revisions
        /// </summary>
        /// <returns></returns>
        public IEnumerable<Revision> GetAllRevisions()
        {
            return _revisions;
        }

        #endregion get revisions

        #region edit revisions

        /// <summary>
        /// adds a document to the container
        /// </summary>
        /// <param name="rev"></param>
        public void AddRevision(Revision rev)
        {
            //null check
            if (rev == null)
            {
                throw new ArgumentNullException(nameof(rev), "Revision cannot be null.");
            }

            //check if a document with this number allready exists
            foreach (var existingRevision in _revisions)
            {
                if (existingRevision.Conflicts(rev))
                {
                    throw new Exceptions.RevisionDuplicateException(existingRevision, rev);
                }
            }

            //no conflict found - add document
            _revisions.Add(rev);
        }

        #endregion edit revisions

        public RevisionContainer() 
        { 
            _revisions = [];
        }
    }
}
