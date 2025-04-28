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
using System.Collections.ObjectModel;
using System.Text.RegularExpressions;
using static System.Net.Mime.MediaTypeNames;


namespace duHastNet.UI.PDFDWGExporterUI.Utils
{
    public static class SettingsStringParser
    {

        /// <summary>
        /// parse the settings string for PDF export
        /// <paramref name="settingsString"/> is the settings string to parse 
        /// </summary>
        public static ObservableCollection<DocumentSetting> ParsePdfSettingsString(string settingsString, List<string> availableParameters)
        {
            ObservableCollection<DocumentSetting> settings = new ObservableCollection<DocumentSetting>();

            return settings;

        }

        public static string ConvertSettingsToPDFString(ObservableCollection<DocumentSetting> settings)
        {
            StringBuilder sb = new StringBuilder();
            foreach (DocumentSetting setting in settings)
            {
                sb.Append(setting.Prefix);
                sb.Append(setting.PropertyName);
                sb.Append(setting.Suffix);
                sb.Append(setting.Separator);
            }
            return sb.ToString();
        }


        private static bool IsInMatchCollection(string value, MatchCollection matches)
        {
            foreach (Match match in matches)
            {
                if (match.Groups[1].Value == value)
                {
                    return true;
                }
            }
            return false;
        }


        /// <summary>
        /// parse the settings string for DWG export
        /// sample: "*Parameter1**Parameter2*-DWG-*Parameter3*[*Parameter4*]"
        /// </summary>
        /// <param name="settingsString"></param>
        /// <returns></returns>
        public static ObservableCollection<DocumentSetting> ParseDwgSettingsString(string settingsString, List<string> availableParameters)
        {
            ObservableCollection<DocumentSetting> documentSettings = new ObservableCollection<DocumentSetting>();
            string pattern = @"\*(.*?)\*"; // Matches anything between asterisks

            MatchCollection matches = Regex.Matches(settingsString, pattern);
            string[] fixedText = Regex.Split(settingsString, pattern);

            //check if the first entry in fixed Text is empty, if so remove it
            if (fixedText.Length > 0 && fixedText[0] == string.Empty)
            {
                fixedText = fixedText.Skip(1).ToArray();
            }

            //loop over matches and add to document settings if that parameter is still available
            for (int i = 0; i < matches.Count; i++)
            {
                string matchValue = matches[i].Groups[1].Value;
                // strip the leading and trailing asterisks
                string matchValueTrimmed = matchValue.Trim('*');
                if (availableParameters.Contains(matchValue))
                {
                    DocumentSetting setting = new DocumentSetting();
                    setting.PropertyName = matchValueTrimmed;

                    // check if there is a preceding fixed text
                    int indexOf = Array.IndexOf(fixedText, matchValueTrimmed);
                    if (indexOf > 0)
                    {
                        string prior_value = fixedText[indexOf - 1];
                        // check if the prior value is a parameter in match value
                        if (!IsInMatchCollection("*" + prior_value + "*", matches))
                        {
                            setting.Prefix = prior_value;
                        }
                    } 
                    // check if the last entry is not a parameter and therefore a suffix
                    if (indexOf == fixedText.Length-2)
                    {
                        string past_value = fixedText[indexOf+1];
                        // check if the prior value is a parameter in match value
                        if (!IsInMatchCollection("*" + past_value + "*", matches))
                        {
                            setting.Suffix = past_value;
                        }
                    }

                    // add the settings to the collection
                    documentSettings.Add(setting);

                }
            }

            return documentSettings;
        }

        public static string ConvertSettingsToDwgString(ObservableCollection<DocumentSetting> settings)
        {
            StringBuilder sb = new StringBuilder();
            foreach (DocumentSetting setting in settings)
            {
                sb.Append(setting.Prefix);
                sb.Append(setting.PropertyName);
                sb.Append(setting.Suffix);
                sb.Append(setting.Separator);
            }
            return sb.ToString();
        }
    }
}
