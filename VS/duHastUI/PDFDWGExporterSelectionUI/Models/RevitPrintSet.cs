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
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace duHastNet.UI.PDFDWGExporterSelectionUI.Models
{
    public class RevitPrintSet
    {
        /// <summary>
        /// the revit print set name
        /// </summary>
        string _name;

        public string Name {
            get => _name; 
            set => _name = value;
        }

        /// <summary>
        /// a lsit off Revit sheet ids belonging to this print set
        /// </summary>
        private List<RevitSheet> _revitSheets;

        public List<RevitSheet> RevitSheets
        {
            get => _revitSheets;
        }


        /// <summary>
        /// adds an revit sheet to the print set
        /// </summary>
        /// <param name="revitSheet"></param>
        /// <exception cref="Exceptions.SheetConflictException"></exception>
        public void AddRevitSheet(RevitSheet revitSheet)
        {
            //check if id allready in use
            if(!RevitSheets.Exists(x=> x.RevitElementId.Value == revitSheet.RevitElementId.Value))
            {
                _revitSheets.Add(revitSheet);
            }
            else
            {
                // get the existing sheet
                var existingSheet = RevitSheets.Find(x => x.RevitElementId.Value == revitSheet.RevitElementId.Value);
                //pop an exception
                throw new Exceptions.SheetConflictException(existingSheet, revitSheet);
            }
        }

        public RevitPrintSet(string name) {
            _name = name;
            _revitSheets = new List<RevitSheet>();
        }
    }
}
