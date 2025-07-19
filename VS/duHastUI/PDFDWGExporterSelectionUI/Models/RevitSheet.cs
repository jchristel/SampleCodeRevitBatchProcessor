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

using System.Collections.Generic;

namespace duHastNet.UI.PDFDWGExporterSelectionUI.Models
{
    public class RevitSheet(string sheetNumber, string sheetName, string revitElementId)
    {
        /// <summary>
        /// add a is selected for export property
        /// </summary>
        public bool IsSelected { get; set; } = false;

        /// <summary>
        /// The revit sheet name property
        /// </summary>
        public SheetProperty SheetName { get; set; } = new(Models.Constants.PropertyNameSheetName, sheetName);

        /// <summary>
        /// the revit sheet number property
        /// </summary>
        public SheetProperty SheetNumber { get; set; } = new(Models.Constants.PropertyValueSheetNumber, sheetNumber);

        /// <summary>
        /// The revit element id of this sheet
        /// </summary>
        public SheetProperty RevitElementId { get; set; } = new(Models.Constants.PropertyValueSheetRevitId, revitElementId);

        /// <summary>
        /// All other sheet properties
        /// </summary>
        public List<SheetProperty> Properties { get; } = [];

        public void AddSheetProperty(SheetProperty sheetProperty)
        {
            // add a new sheet property but only if not already exists
            if (sheetProperty != null)
            {
                //check if property already exists
                if (!Properties.Exists(x => x.Name == sheetProperty.Name))
                {
                    Properties.Add(sheetProperty);
                }
                else
                {
                    //get the existing property the new one is conflicting with
                    var existingProperty = Properties.Find(x => x.Name == sheetProperty.Name);
                    //throw an exception
                    throw new Exceptions.PropertyConflictException(existingProperty, sheetProperty);
                }
            }
        }

        /// <summary>
        /// pdf file name preview
        /// </summary>
        public string PDFPreviewName { get; set; }

        /// <summary>
        /// dwg preview name
        /// </summary>
        public string DWGPreviewName { get; set; }
    }
}
