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


using CsvHelper;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Data;
using System.Windows.Input;

namespace duHastNet.AtTheLibrary.ViewModels
{
    public class TypeCatalogueViewModel : Utils.WPF.ViewModels.ViewModelBase
    {
        private readonly Utils.WPF.Stores.NavigationStore _navigationStore;
        private readonly Utils.WPF.Stores.MessageStore _messageStore;
        private readonly Models.RevitFamiliesDataModel _revitDataModel;
        private readonly Utils.WPF.ViewModels.ErrorsViewModel _errorsViewModel;

        public Utils.WPF.ViewModels.GlobalMessageViewModel GlobalMessageViewModel { get; }

        //command to navigate back to families selection view model
        private readonly Commands.NavigateCommand _navigateCommand;
        //command to save type catalogue text file
        private readonly Commands.SaveCatalogueTextFileDataCommand _saveCatalogueTextFileDataCommand;

        private Models.RevitFamiliesDataModel RevitDataModel { get; set; }

        /// <summary>
        /// the family of which to display the catalogue file
        /// </summary>
        public Models.FamilyDataModel SelectedFamily { get; set; }

        /// <summary>
        /// As read from type catalogue file
        /// </summary>
        private List<string> _catalogueFileHeadersOriginal;
        private List<List<string>> _catalogueFileDataOriginal;

        #region data Properties

        private List<string> _headerRow;
        private List<List<object>> _dataRows;

        /// <summary>
        /// contains the header row
        /// </summary>
        public List<string> HeaderRow
        {
            get => _headerRow;
            set
            {
                _headerRow = value;
                OnPropertyChanged(nameof(HeaderRow));
            }
        }

        /// <summary>
        /// contains the data rows
        /// </summary>
        public List<List<object>> DataRows
        {
            get => _dataRows;
            set
            {
                _dataRows = value;
                OnPropertyChanged(nameof(DataRows));
            }
        }

        #endregion

        #region Commands

        //commands

        // switch to families selection view model
        public ICommand SelectFamiliesCommand { get { return _navigateCommand; } }
        //save type catalogue text file
        public ICommand SaveCatalogueTextFileDataCommand { get { return _saveCatalogueTextFileDataCommand; } }

        #endregion Commands

        /// <summary>
        /// Adds a message to the global message store which will then be displayed in the UI
        /// </summary>
        /// <param name="message"></param>
        /// <param name="messageType"></param>
        public void AddMessage(string message, Utils.WPF.Stores.MessageTypes messageType)
        {

            _messageStore.SetCurrentMessage(message, messageType);
        }

        #region load data


        private object GetCellValue(string cellEntryAsstring, int cellColumnIndex)
        {
            
            if (cellColumnIndex == 0)
            {
                //family type name is always a string
                return cellEntryAsstring;
            }

            //check if we have a column name at the given index
            string columnName = _catalogueFileHeadersOriginal[cellColumnIndex];

            // get the property type from the family
            var property = SelectedFamily.GetPropertyByName(columnName);
            // if no matching property return unchanged
            if (property == null) { return cellEntryAsstring; }

            //convert value to type
            return duHastNet.Utils.DataConversion.TypeConverter.ConvertStringToType (cellEntryAsstring, property.StorageType);

        }

        /// <summary>
        /// Loads the catalogue text file data from file
        /// </summary>
        private void LoadData()
        {
            // read catalogue file
            (_catalogueFileHeadersOriginal, _catalogueFileDataOriginal) = Utilities.Revit.TypeCatalogueFileUtils.GetCatalogueFileData(SelectedFamily.FamilyFilePath.Value, this);

            //check for null values indicating falure to read
            if (_catalogueFileDataOriginal == null || _catalogueFileHeadersOriginal == null)
            {
                return;
            }

            // Create header row
            var defaultHeaderRow = _catalogueFileHeadersOriginal.ToList();
            //insert "Family Type Name" as first column ( by default this is an empty field )
            defaultHeaderRow[0] = Models.Constants.ColumnHeaderTypeCatalogueFamilyTypeName;
            HeaderRow = defaultHeaderRow;

            // populate data rows ( assumes that headers and data rows are aligned in terms of index and value )
            var dataRows = new List<List<object>>();

            foreach (var row in _catalogueFileDataOriginal)
            {
                var rowEntries = new List<object>();
                for (int i = 0; i < row.Count; i++)
                {
                    var rowEntry = row[i];
                    if (rowEntry != null)
                    {
                        // convert the row entry depending on the data type stored in the matching family property
                        var rowEntryConverted = GetCellValue(
                            cellEntryAsstring: rowEntry,
                            cellColumnIndex: i);
                        
                        rowEntries.Add(rowEntryConverted);
                    }
                }
                dataRows.Add(rowEntries);
            };

            //update data rows
            DataRows = dataRows;
        }

        #endregion

        public TypeCatalogueViewModel(Models.RevitFamiliesDataModel revitDataModel, Utils.WPF.Stores.NavigationStore navigationStore,
            Utils.WPF.Stores.MessageStore messageStore,
            Utils.WPF.ViewModels.GlobalMessageViewModel globalMessageViewModel,
            Func<ViewModels.FamiliesSelectionViewModel> createViewModel,
            Models.FamilyDataModel selectedFamily
            )
        {

            this.RevitDataModel = revitDataModel;
            this.SelectedFamily = selectedFamily;

            //store services
            _navigationStore = navigationStore;
            _messageStore = messageStore;
            _revitDataModel = revitDataModel;

            //store the global message view model
            GlobalMessageViewModel = globalMessageViewModel;
            RegisterChild(GlobalMessageViewModel); // Register as child

            //view model switch to families selection view model
            _navigateCommand = new Commands.NavigateCommand(
                navigationStore: _navigationStore,
                createViewModel: createViewModel
            );

            //command to save type catlogue text file
            _saveCatalogueTextFileDataCommand = new Commands.SaveCatalogueTextFileDataCommand(
                typeDataViewModel: this,
                selectedFamily: selectedFamily
             );

            // load data and ini cell editor
            LoadData();
        }
    }
}
