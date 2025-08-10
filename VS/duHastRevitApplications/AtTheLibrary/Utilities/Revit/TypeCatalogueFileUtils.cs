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
using System.IO;
using System.Collections.Generic;

namespace duHastNet.AtTheLibrary.Utilities.Revit
{
    public static class TypeCatalogueFileUtils
    {
        /// <summary>
        /// Returns the formatted header row and data rows from the type catalogue file
        /// </summary>
        /// <param name="filePath"></param>
        /// <param name="typeCatalogueViewModel"></param>
        /// <returns></returns>
        public static (List<string>, List<List<string>>) GetCatalogueFileData(string filePath, ViewModels.TypeCatalogueViewModel typeCatalogueViewModel)
        {
            duHastNet.RevitUtils.Families.TypeCatalogueFileReader reader = new RevitUtils.Families.TypeCatalogueFileReader();
            try
            {
                //make sure to change extension to txt
                string catalogueFilePath = Path.GetExtension(filePath).Equals(".txt", StringComparison.OrdinalIgnoreCase)
                    ? filePath
                    : Path.ChangeExtension(filePath, ".txt");

                //attempt to read the file
                bool success = reader.LoadCatalogueFile(catalogueFilePath);
                if (!success)
                {
                    foreach (var message in reader.GetErrorMessages())
                    {
                        typeCatalogueViewModel.AddMessage(message, Utils.WPF.Stores.MessageTypes.Error);
                    }
                    return (null, null);
                }

                // return header and data rows
                return (reader.FormattedHeaderRow, reader.DataRows);
            }
            catch (Exception ex)
            {
                typeCatalogueViewModel.AddMessage(ex.Message, Utils.WPF.Stores.MessageTypes.Error);
                return (null, null);
            }
        }
    }
}
