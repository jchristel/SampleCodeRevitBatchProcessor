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
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace duHastNet.AtTheLibrary.Models
{
    public class RevitFamiliesDataModel : duHastNet.Utils.WPF.Models.DataModelBase, INotifyPropertyChanged
    {
        private Models.Settings _settings;
        public Settings Settings { get => _settings; set => _settings = value; }

        private Utils.Logging.SimpleLogger _logger;

        public Models.FamiliesDataModelContainer _familiesContainer;

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


        public void AddFamily(Models.FamilyDataModel room)
        {
            _familiesContainer.AddFamily(room);
        }

        public List<Models.FamilyDataModel> GetAllFamilies()
        {
            return _familiesContainer.GetAllFamilies();
        }

        public void ClearFamilies()
        {
            _familiesContainer.ClearFamilies();
        }

        public bool LoadFamiliesData()
        {
            // add rooms to RevitDataModel
            List<Models.FamilyDataModel> families = Utilities.ReadFamilyData.GetFamiliesData(filePath: Settings.DataPath, supportedParameterNames: Settings.SupportedTypeParameterNames);

            // TODO: if no families return (need to pop message to user...)
            if (families == null) return false;

            foreach (Models.FamilyDataModel family in families)
            {
                AddFamily(family);
            }

            return true;
        }

        public void InitialiseLogger(string filePath)
        {
            _logger = new Utils.Logging.SimpleLogger(filePath);
        }

        public void LogMessages(List<(string, Utils.WPF.Stores.MessageTypes)> messages)
        {
            if (_logger == null)
            {
                return;
            }

            _logger.LogMessagesFireAndForget(messages);
        }

        public RevitFamiliesDataModel()
        {
            _familiesContainer = new Models.FamiliesDataModelContainer();
            _settings = new Models.Settings();
        }
    }
}
