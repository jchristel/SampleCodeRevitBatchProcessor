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
using System.Xml.Serialization;
using System.IO;

namespace duHastNet.UI.FamilyReloaderUI.Utils
{
    public static class MatchStatusUtils
    {
        public static List<Models.RevitFamily> UpdateMatchStatus(List<Models.RevitFamily> families, Models.Settings settings)
        {

            try
            {
                // check if there is a target directory
                if (settings.TargetDirectory == null ||
                    settings.TargetDirectory == string.Empty ||
                    !File.Exists(settings.TargetDirectory)
                    )
                {
                    return families;
                }

                // get all families from directory
                List<string> familiesFound = duHastNet.Utils.FilesIO.FilesGet.GetFiles(
                    settings.TargetDirectory,
                    "*.rfa",
                    settings.IncludeSubdirectories
                 );

                // check if any families where actually found
                if (familiesFound.Count == 0) { return families; }

                ///build a dictionary where key is the file name without extension and the value is a list of file paths
                Dictionary<string, List<string>> familyLookup = new Dictionary<string, List<string>>();
                foreach (var f in familiesFound)
                {
                    var fileName = Path.GetFileNameWithoutExtension(f);
                    if (familyLookup.TryGetValue(fileName, out List<string> existingPaths))
                    {
                        // Key exists, add to existing list
                        existingPaths.Add(f);
                    }
                    else
                    {
                        // Key doesn't exist, create new list
                        familyLookup[fileName] = new List<string> { f };
                    }
                }

                //loop over families and check for matches
                for (int i = 0; i < families.Count; i++)
                {
                    if (familyLookup.TryGetValue(families[i].FamilyName, out List<string> matchingFamilies))
                    {
                        // Found matches
                        if (matchingFamilies.Count == 1)
                        {
                            // no match found
                            families[i].MatchStatus = MatchStatus.SingleMatch;
                            families[i].FamilyFilePath = matchingFamilies[0];
                        }
                        else
                        {
                            families[i].MatchStatus = MatchStatus.MultipleMatches;
                            families[i].FamilyFilePath = string.Empty;
                        }
                    }
                    else
                    {
                        // no match found
                        families[i].MatchStatus = MatchStatus.NoMatch;
                        families[i].FamilyFilePath = string.Empty;
                    }
                }
                return families;
            }
            catch (Exception)
            {
                return families;
            }
        }
    }
}
