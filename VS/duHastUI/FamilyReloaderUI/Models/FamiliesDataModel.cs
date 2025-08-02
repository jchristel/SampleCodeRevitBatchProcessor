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


using System.Collections.Generic;
using System.Linq;
using System.Collections.ObjectModel;
using System.ComponentModel;

namespace duHastNet.UI.FamilyReloaderUI.Models
{
    public class FamiliesDataModel : duHastNet.Utils.WPF.Models.DataModelBase
    {
        /// <summary>
        /// contains the user settings for the UI
        /// </summary>
        private Models.Settings _settings;
        public Models.Settings Settings { get => _settings; set => _settings = value; }

        private duHastNet.Utils.Logging.SimpleLogger _logger;

        /// <summary>
        /// contains the Revit sheets in the model
        /// </summary>
        private List<Models.RevitFamily> _revitFamilies;
        public List<Models.RevitFamily> RevitFamilies
        {
            get => _revitFamilies;
            set 
            { 
                _revitFamilies = value;
                //RaisePropertyChanged(nameof(RevitFamilies));
            }
        }

        //event handlers for property changed
        public event PropertyChangedEventHandler PropertyChanged;
        protected void OnPropertyChanged(string propertyName)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }

        public void RaisePropertyChanged(string name)
        {
            OnPropertyChanged(name);
        }


        /// <summary>
        /// returns selected families where the match status is single
        /// </summary>
        /// <returns></returns>
        public List<Models.RevitFamily> GetFamiliesToReload()
        {
            // Find people who are over 25 AND live in New York
            var result = RevitFamilies.Where(p => p.IsSelected == true && p.MatchStatus == Utils.MatchStatus.SingleMatch).ToList();
            return result;
        }

        /// <summary>
        /// finds the match status for each family in given directory structure
        /// </summary>
        public void UpdateFamilyMatchStatus()
        {
            // update the match status of each family
            RevitFamilies = Utils.MatchStatusUtils.UpdateMatchStatus(_revitFamilies, _settings);
        }

        /// <summary>
        /// called from main
        /// </summary>
        /// <param name="filePath"></param>
        public void InitialiseLogger(string filePath)
        {
            _logger = new duHastNet.Utils.Logging.SimpleLogger(filePath);
        }

        public void LogMessages(List<(string, duHastNet.Utils.WPF.Stores.MessageTypes)> messages)
        {
            if (_logger == null)
            {
                return;
            }

            _logger.LogMessagesFireAndForget(messages);
        }

        /// <summary>
        /// Constructor for the sheets data model
        /// </summary>
        public FamiliesDataModel(
            List<Models.RevitFamily> revitFamilies,
            Models.Settings settings
            )
        {
            //store settings object
            _settings = settings;
            
            // store families
            _revitFamilies = revitFamilies;

        }
    }
}
