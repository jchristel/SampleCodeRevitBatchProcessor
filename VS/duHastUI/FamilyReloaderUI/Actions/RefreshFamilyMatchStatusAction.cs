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


namespace duHastNet.UI.FamilyReloaderUI.Actions
{
    public class RefreshFamilyMatchStatusAction : duHastNet.Utils.Logging.LogActionsBase
    {
        public Models.FamiliesDataModel RevitModel { get; set; }


        public (string message, duHastNet.Utils.WPF.Stores.MessageTypes messageType) GetReturnValue(string allOKMessage)
        {
            // get the ovearll error count
            int erroCount = GetErrorMessages().Count;

            // check if any error messages were added
            if (erroCount > 0)
            {
                // return the message
                return (string.Join("\n", GetErrorMessages()), duHastNet.Utils.WPF.Stores.MessageTypes.Error);
            }
            else
            {
                // return the message
                return (allOKMessage, duHastNet.Utils.WPF.Stores.MessageTypes.Information);
            }
        }


        public (string messageAction, duHastNet.Utils.WPF.Stores.MessageTypes messageActionType) Execute()
        {
            try
            {
                var families = Utils.MatchStatusUtils.UpdateMatchStatus(RevitModel.RevitFamilies, RevitModel.Settings);
                RevitModel.RevitFamilies = families;
                AddMessage("Succesfully updated match status of families", duHastNet.Utils.WPF.Stores.MessageTypes.Information);
            }
            catch (System.Exception ex)
            {
                //log the exception
                AddMessage($"Error refreshing family data: {ex.Message}", duHastNet.Utils.WPF.Stores.MessageTypes.Error);
            }

            // get the ovearll error count
            int erroCount = GetErrorMessages().Count;

            // check if any error messages were added
            if (erroCount > 0)
            {
                if (erroCount > 3)
                {
                    //return abridged message
                    return ($"{erroCount} Errors occured. Refer to log file for details.", duHastNet.Utils.WPF.Stores.MessageTypes.Error);
                }
                else
                {
                    // return the message
                    return (string.Join("\n", GetErrorMessages()), duHastNet.Utils.WPF.Stores.MessageTypes.Error);
                }
            }
            else
            {
                // return the message
                return ("Refreshed families", duHastNet.Utils.WPF.Stores.MessageTypes.Information);
            }
        }

        public RefreshFamilyMatchStatusAction(Models.FamiliesDataModel revitModel)
        {
            RevitModel = revitModel;
        }
    }
}
