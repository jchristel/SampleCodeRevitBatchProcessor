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
using System.IO;

namespace duHastNet.RevitUtils.Families
{
    public class TypeCatalogueFileReader : duHastNet.Utils.Logging.LogActionsBase
    {
        /// <summary>
        /// separator string indicating start and end of unit descriptor
        /// </summary>
        public static string UnitSeparator = "##";

        /// <summary>
        /// separator string indicating start of Element ID
        /// </summary>
        public static string ElementIdSeparator = "[";

        /// <summary>
        /// place holder for the catalogue file header row
        /// </summary>
        List<string> _unformattedHeaderRow  = null;
        public List<string> UnformattedHeaderRow
        {
            get { return _unformattedHeaderRow; }
            private set { _unformattedHeaderRow = value; }
        }
        
        /// <summary>
        /// contains the header row without unit type formatting or parameter ids
        /// </summary>
        List<string> _formattedHeaderRow= null;
        public List<string> FormattedHeaderRow
        {
            get { return _formattedHeaderRow; }
        }

        /// <summary>
        /// contains the actual data rows
        /// </summary>
        List<List<string>> _dataRows = null;
        public List<List<string>> DataRows
        {
            get { return _dataRows; }
        }

        public bool LoadCatalogueFile(string filePath)
        {
            //wrap the action in a try catch block
            try
            {
                if (!File.Exists(filePath))
                {
                    AddMessage($"File {filePath} does not exist.", Utils.WPF.Stores.MessageTypes.Error);
                    return false;
                }

                // read the file
                duHastNet.FileIOWrapper.ReadFromColumnBasedTextFile reader = new FileIOWrapper.ReadFromColumnBasedTextFile ();
                var data = reader.ReadFromTextFile(filePath);

                //check for errors during read
                if (reader.ErrorHistory.Count > 0) {
                    foreach (string line in reader.ErrorHistory)
                    {
                        AddMessage(line, Utils.WPF.Stores.MessageTypes.Error);
                    }
                    return false;
                }

                //store unformatted header row
                UnformattedHeaderRow = data[0];

                //store data rows
                for (int i = 1; i < data.Count; i++)
                {
                    _dataRows.Add(data[i]);
                }

                // get parameter names from header row
                _formattedHeaderRow = GetParameterNamesFromHeaderRow(data[0]);
                
                return true;
            }
            catch (Exception ex)
            {
                AddMessage(ex.Message, Utils.WPF.Stores.MessageTypes.Error);
                return false;
            }
        }

        public List<string> GetParameterNamesFromHeaderRow(List<string> headerRow)
        {
            List<string> parameterNames = new List<string>();
            foreach (var entry in headerRow)
            {
                // get the first occurence of ## of [
                int firstIndexUnitSeparator = entry.IndexOf(UnitSeparator);
                int firstIndexElementIdSeparator = entry.IndexOf(ElementIdSeparator);

                int nameEndIndex = firstIndexUnitSeparator;
                if (firstIndexElementIdSeparator != -1 && firstIndexElementIdSeparator<firstIndexUnitSeparator)
                {
                    nameEndIndex = firstIndexElementIdSeparator;
                }

                //If no separators found, use the entire string ( first column value is usually empty)
                if (nameEndIndex == -1)
                {
                    parameterNames.Add(entry);
                }
                else
                {
                    parameterNames.Add(entry.Substring(0, nameEndIndex));
                }
            }
            return parameterNames;
        }
    }
}
