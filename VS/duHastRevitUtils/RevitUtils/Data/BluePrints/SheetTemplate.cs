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

namespace duHastNet.RevitUtils.Data.BluePrints
{
    /// <summary>
    /// this class contains 
    /// - room refrence information
    /// - sheet information
    /// </summary>
    public class SheetTemplate
    {
        /// <summary>
        /// room propertions
        /// </summary>
        public Elements.Room RoomInfo { get; set; } = new Elements.Room();

        /// <summary>
        /// sheets in the template representing the room layout sheets required for a given room
        /// </summary> 
        public List<Elements.Sheet> Sheets { get; } = new List<Elements.Sheet>();

        /// <summary>
        /// Adds a sheet to the template.
        /// </summary>
        /// <param name="sheet"></param>
        /// <returns></returns>
        public bool AddSheet(Elements.Sheet sheet)
        {
            bool result = false;
            if (sheet != null)
            {
                Sheets.Add(sheet);
                result = true;
            }
            return result;
        }

        public SheetTemplate() { }
    }
}
