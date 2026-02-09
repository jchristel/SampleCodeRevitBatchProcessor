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
    public class RevitSheetContainer
    {
        private List<RevitSheet> _sheets { get; }
        public RevitSheetContainer()
        {
            _sheets = new List<RevitSheet>();
        }

        public void AddSheet(RevitSheet sheet)
        {
            if (sheet == null)
            {
                throw new ArgumentNullException(nameof(sheet), "Sheet cannot be null.");
            }
            // check if a sheet with this sheet number already exists
            foreach (var existingSheet in _sheets)
            {
                if (existingSheet.SheetNumber == sheet.SheetNumber)
                {
                    throw new ArgumentException($"A sheet with the number '{sheet.SheetNumber}' already exists.", nameof(sheet));
                }
            }

            _sheets.Add(sheet);
        }
    }
}
