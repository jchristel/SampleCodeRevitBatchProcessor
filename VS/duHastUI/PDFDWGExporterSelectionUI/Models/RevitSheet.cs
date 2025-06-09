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
    public class RevitSheet
    {

        /// <summary>
        /// add a is selected for export property
        /// </summary>
        private bool _isSelected = false;
        public bool IsSelected
        {
            get { return _isSelected; }
            set { _isSelected = value; }
        }

        /// <summary>
        /// The revit sheet name property
        /// </summary>
        private SheetProperty _sheetName;
        public SheetProperty SheetName
        {
            get => _sheetName;
            set => _sheetName = value;
        }

        /// <summary>
        /// the revit sheet number property
        /// </summary>
        private SheetProperty _sheetNumber;
        public SheetProperty SheetNumber
        {
            get => _sheetNumber;
            set => _sheetNumber = value;
        }


        /// <summary>
        /// The revit element id of this sheet
        /// </summary>
        private SheetProperty _revitElementId;
        public SheetProperty RevitElementId
        {
            get => _revitElementId;
            set => _revitElementId = value;
        }

        /// <summary>
        /// All other sheet properties
        /// </summary>
        private List<SheetProperty> _properties;
        public List<SheetProperty> Properties
        {
            get => _properties;
        }


        public void AddSheetProperty(SheetProperty sheetProperty)
        {
            // add a new sheet property but only if not already exists
            if (sheetProperty != null)
            {
                //check if property allready exists
                if (!Properties.Exists(x => x.Name == sheetProperty.Name))
                {
                    _properties.Add(sheetProperty);
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
        private string _pdfPreviewName;
        public string PDFPreviewName
        {
            get { return _pdfPreviewName; }
            set { _pdfPreviewName = value; }
        }

        /// <summary>
        /// dwg preview name
        /// </summary>
        private string _dwgPreviewName;
        public string DWGPreviewName
        {
            get { return _dwgPreviewName; }
            set { _dwgPreviewName = value; }
        }

        public RevitSheet(string sheetNumber, string sheetName, string revitElementId)
        {
            _sheetName = new SheetProperty(name: Models.Constants.PropertyNameSheetName, value: sheetName);
            _sheetNumber = new SheetProperty(name: Models.Constants.PropertyValueSheetNumber, value: sheetNumber);
            _revitElementId = new SheetProperty(name: Models.Constants.PropertyValueSheetRevitId, value: revitElementId);

            _properties = new List<SheetProperty>();
        }
    }
}
