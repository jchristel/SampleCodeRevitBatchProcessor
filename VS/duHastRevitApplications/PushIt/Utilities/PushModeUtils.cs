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
        private static string SplitIDentifier = "SPLIT";
        private static string NewIDentifier = "NEW";
        private static string PushIDentifier = "PUSH";
        private static string Separator = "::";
        public static string GetPushModeString(PushMode pushOperationMode)
        {
            switch (pushOperationMode)
            {
                case PushMode.Push:
                    return PushIDentifier;
                case PushMode.Split:
                    return SplitIDentifier;
                case PushMode.New:
                    return NewIDentifier;
                default:
                    throw new ArgumentOutOfRangeException(nameof(pushOperationMode), pushOperationMode, null);
            }
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


        public static string GetSplitModeIdValue(string idValue)
        {
            //check if the id value is empty
            if (string.IsNullOrEmpty(idValue))
            {
                return SplitIDentifier;
            }
            else
            {
                return $"{idValue}{Separator}{SplitIDentifier}";
            }
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
                return idValue.Split(new string[] { Separator }, StringSplitOptions.None)[0];
            }
        }

        public static string GetNewModeIdValue(string idValue)
        {
            DateTime now = DateTime.Now;
            string timestamp = now.ToString("yyyy-MM-dd HH:mm:ss.fff");
            string username = Environment.UserName;

            return $"{NewIDentifier}{Separator}{username}{Separator}{timestamp}";
        }
    }
}
