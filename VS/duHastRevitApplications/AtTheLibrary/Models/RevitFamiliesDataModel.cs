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
using System.ComponentModel;

namespace duHastNet.AtTheLibrary.Models
{
    public class RevitFamiliesDataModel : duHastNet.Utils.WPF.Models.DataModelBase, INotifyPropertyChanged
    {
        private Models.Settings _settings;

        public Settings Settings { get => _settings; set => _settings = value; }

        private Utils.Logging.SimpleLogger _logger;

        //contains all families read from file
        public Models.FamiliesDataModelContainer _familiesContainer;

        //contains all uniques parameter names from all families
        public Models.FamiliesParameterDataModelContainer _parameterDataContainer;
        public Models.FamiliesParameterDataModelContainer ParameterDataContainer { get => _parameterDataContainer; set => _parameterDataContainer = value; }

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


        /// <summary>
        /// reds family data from file into the data model
        /// </summary>
        /// <returns></returns>
        public bool LoadFamiliesData()
        {
            // add rooms to RevitDataModel
            List<Models.FamilyDataModel> families = Utilities.ReadFamilyData.GetFamiliesData(
                filePath: Settings.DataPath
                );

            // TODO: if no families return (need to pop message to user...)
            if (families == null) return false;

            // clear all families before loading again
            ClearFamilies();

            //clear parameters before adding them again
            ClearParameters();

            // add families and parameter to respective containers
            foreach (Models.FamilyDataModel family in families)
            {
                AddFamily(family);

                //load parameter data
                var paraNames = family.GetAllProperties();
                if (paraNames.Count > 0)
                {
                    foreach (var para in paraNames)
                    {
                        AddParameter(para);
                    }
                }
            }

            return true;
        }

        /// <summary>
        /// adds a family parameter to the data model
        /// is required for column add and remove operations and column pre selection
        /// </summary>
        /// <param name="parameter">The parameter to be added</param>
        public void AddParameter(Models.FamilyDataProperty parameter)
        {
            _parameterDataContainer.AddParameter(
                parameter, 
                Settings.EnabledTypeParameterNames,
                Settings.ShownTypeParameterNames);
        }

        public void ClearParameters()
        {
            _parameterDataContainer.ClearParameters();
        }

        public List<string> GetAllParameterNames()
        {
            return _parameterDataContainer.GetAllParameterNames();
        }

        public List<string> GetAllEnabeledParameterNames()
        {
            return _parameterDataContainer.GetAllEnabledParameterNames();
        }

        public List<string> GetAllShownParameterNames()
        {
            return _parameterDataContainer.GetAllShownParameterNames();
        }

        public List<Models.ParameterDataProperty> GetAllParameterProperties()
        {
            return _parameterDataContainer.GetParameterDataProperties();
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
            _parameterDataContainer = new FamiliesParameterDataModelContainer();
            _settings = new Models.Settings();
        }
    }
}
