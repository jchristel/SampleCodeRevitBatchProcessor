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

using System.Reflection.Metadata;

namespace duHastNet.DocManager.Revit.Utilities.RevitData
{
    public class RevitSheet
    {
        public string SheetNumber { get; set; }
        public string SheetName { get; set; }


        private List<RevitRevisionOnSheet> _revisionsOnSheet;
        public List<RevitRevisionOnSheet> RevisionsOnSheet { get { return _revisionsOnSheet; } }
        
        
        private List<RevitDocumentProperty> _documentProperties;
        public List<RevitDocumentProperty> DocumentProperties { get { return _documentProperties; } }

        public RevitSheet(
            string sheetNumber, 
            string sheetName)
        {
            
            SheetNumber = sheetNumber;
            SheetName = sheetName;
            _revisionsOnSheet = [];
            _documentProperties = [];
        }

        public void AddRevisionOnSheet(RevitRevisionOnSheet revisionOnSheet)
        {
            if (revisionOnSheet == null)
            {
                throw new ArgumentNullException(nameof(revisionOnSheet), "Revision on sheet cannot be null.");
            }

            // check if a revision with this identifier number already exists
            foreach (var existingRevisionOnSheet in _revisionsOnSheet)
            {
                if (existingRevisionOnSheet.Conflicts(revisionOnSheet))
                {
                    throw new Exceptions.RevisionOnSheetDuplicateException(existingRevisionOnSheet, revisionOnSheet);
                }
            }

            // no conflict found - add revision on sheet to list
            _revisionsOnSheet.Add(revisionOnSheet);
        }

        public void AddDocumentProperty(RevitDocumentProperty documentProperty)
        {
            //null check
            if (documentProperty == null)
            {
                throw new ArgumentNullException(nameof(documentProperty), "Property cannot be null.");
            }

            //check if a property with this name allready exists
            foreach (var existingProperty in _documentProperties)
            {
                if (existingProperty.Conflicts(documentProperty))
                {
                    throw new Exceptions.DocumentPropertyDuplicateException(existingProperty, documentProperty);
                }
            }

            //no conflict found - add property to list
            _documentProperties.Add(documentProperty);
        }
        
        public override string ToString()
        {
            return $"Sheet Number: {SheetNumber}, Sheet Name: {SheetName}, Revisions on Sheet: {string.Join("; \n", RevisionsOnSheet)}, Document Properties: {string.Join("; \n", DocumentProperties)}";
        }
    }
}
