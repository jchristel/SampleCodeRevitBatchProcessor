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
namespace duHastNet.PushIt.Utilities
{
    public class PushModeUtils
    {
        private static readonly string SplitIDentifier = "SPLIT";
        private static readonly string NewIDentifier = "NEW";
        private static readonly string PushIDentifier = "PUSH";
        private static readonly string Separator = "::";
        public static string GetPushModeString(PushMode pushOperationMode)
        {
            return pushOperationMode switch
            {
                PushMode.Push => PushIDentifier,
                PushMode.Split => SplitIDentifier,
                PushMode.New => NewIDentifier,
                _ => throw new ArgumentOutOfRangeException(nameof(pushOperationMode), pushOperationMode, null),
            };
        }


        public static bool IsSplitRoomMode(string idValue)
        {
            //check if the id value is empty
            if (string.IsNullOrEmpty(idValue))
            {
                return false;
            }
            else
            {
                return idValue.Contains(SplitIDentifier);
            }
        }


        public static bool IsNewRoomMode(string idValue)
        {
            //check if the id value is empty
            if (string.IsNullOrEmpty(idValue))
            {
                return false;
            }
            else
            {
                return idValue.Contains(NewIDentifier);
            }
        }


        public static string GetSplitModeIdValue(string idValue, int counter)
        {
            //check if the id value is empty
            if (string.IsNullOrEmpty(idValue))
            {
                return $"{SplitIDentifier}{Separator}{counter}";
            }
            else
            {
                return $"{idValue}{Separator}{SplitIDentifier}{Separator}{counter}";
            }
        }

        /// <summary>
        /// Parses and returns the integer counter embedded in a split room ID.
        /// e.g. "A.1.01::SPLIT::2" returns 2.
        /// Returns 0 if the ID is not a valid split ID or the counter cannot be parsed.
        /// </summary>
        public static int GetSplitCounterFromId(string idValue)
        {
            if (string.IsNullOrEmpty(idValue)) return 0;
            string[] parts = idValue.Split([Separator], StringSplitOptions.None);
            // expected format: {parentId}::SPLIT::{counter}  → parts[0], parts[1]=="SPLIT", parts[2]==counter
            if (parts.Length >= 3 && parts[parts.Length - 2] == SplitIDentifier)
            {
                if (int.TryParse(parts[parts.Length - 1], out int counter))
                    return counter;
            }
            return 0;
        }

        public static string GetIdWithoutSplitModeIndicator(string idValue)
        {
            //check if the id value is empty
            if (string.IsNullOrEmpty(idValue))
            {
                return idValue;
            }
            else
            {
                return idValue.Split([Separator], StringSplitOptions.None)[0];
            }
        }

        public static string GetNewModeIdValue()
        {
            DateTime now = DateTime.Now;
            string timestamp = now.ToString("yyyy-MM-dd HH:mm:ss.fff");
            string username = Environment.UserName;

            return $"{NewIDentifier}{Separator}{username}{Separator}{timestamp}";
        }
    }
}
