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

using System.Collections.ObjectModel;
using System.Text;

namespace duHastNet.UI.PDFDWGExporterSelectionUI.Utils
{
    public static class FileNamePreviewUtils
    {
        public static string GetFileName(Models.RevitSheet sheet, ObservableCollection<duHastNet.UI.PDFDWGExporterUI.Utils.DocumentSetting> settings)
        {

            StringBuilder pdfFileName = new StringBuilder();

            foreach (var setting in settings)
            {
                // add the prefix
                pdfFileName.Append(setting.Prefix);

                //get the sheet property and its value
                //check for sheet number ( works in english only??)
                if (setting.PropertyName == "Sheet Number")
                    pdfFileName.Append(sheet.SheetNumber.Value);
                else if (setting.PropertyName == "Sheet Name")
                    // sheet name check
                    pdfFileName.Append(sheet.SheetName.Value);
                else
                {
                    // must be another property
                    if (sheet.Properties.Exists(x => x.Name == setting.PropertyName))
                    {
                        var prop = sheet.Properties.Find(x => x.Name == setting.PropertyName);
                        pdfFileName.Append(prop.Value);
                    }
                }


                //add the suffix
                pdfFileName.Append(setting.Suffix);
                //add the separator
                pdfFileName.Append(setting.Separator);
            }

            return pdfFileName.ToString();
        }
    }
}
