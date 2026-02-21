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
using System.Windows.Input;

namespace duHastNet.AtTheLibrary.ViewModels
{
    public class TypeCatalogueViewModel : Utils.WPF.ViewModels.ViewModelBase
    {
        private readonly Utils.WPF.Stores.NavigationStore _navigationStore;
        private readonly Utils.WPF.Stores.MessageStore _messageStore;
        private readonly Models.RevitFamiliesDataModel _revitDataModel;

        public Utils.WPF.ViewModels.GlobalMessageViewModel GlobalMessageViewModel { get; }

        //command to navigate back to families selection view model
        private readonly Commands.NavigateCommand _navigateCommand;
        //command to save type catalogue text file
        private readonly Commands.SaveCatalogueTextFileDataCommand _saveCatalogueTextFileDataCommand;

        private Models.RevitFamiliesDataModel RevitDataModel { get; set; }

        /// <summary>
        /// The family of which to display the catalogue file.
        /// Raises PropertyChanged so SaveCatalogueTextFileDataCommand.CanExecute
        /// re-evaluates when the selection changes.
        /// </summary>
        private Models.FamilyDataModel _selectedFamily;
        public Models.FamilyDataModel SelectedFamily
        {
            get => _selectedFamily;
            set
            {
                _selectedFamily = value;
                OnPropertyChanged(nameof(SelectedFamily));
            }
        }

        /// <summary>
        /// As read from type catalogue file but with unit data removed
        /// </summary>
        private List<string> _catalogueFileHeadersOriginal;

        //make these accessible
        public List<string> CatalogueFileHeadersOriginal
        {
            get => _catalogueFileHeadersOriginal;
        }

        /// <summary>
        /// As read from type catalogue file
        /// </summary>
        private List<string> _catalogueFileHeadersOriginalUnformatted;

        //make these accessible
        public List<string> CatalogueFileHeadersOriginalUnformatted
        {
            get => _catalogueFileHeadersOriginalUnformatted;
        }

        private List<List<string>> _catalogueFileDataOriginal;

        #region data Properties

        private List<string> _headerRow;
        private List<List<object>> _dataRows;
        private List<string> _readOnlyColumns;

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

        /// <summary>
        /// contains read only columns ( which there are none in this case )
        /// </summary>
        public List<string> ReadOnlyColumns
        {
            get => _readOnlyColumns;
            set
            {
                _readOnlyColumns = value;
                OnPropertyChanged(nameof(ReadOnlyColumns));
            }
        }

        #endregion

        #region Commands

        // Command properties delegate to the .Command property on each command object,
        // since the command classes no longer inherit ICommand directly.
        public ICommand SelectFamiliesCommand => _navigateCommand.Command;
        public ICommand SaveCatalogueTextFileDataCommand => _saveCatalogueTextFileDataCommand.Command;

        #endregion Commands

        /// <summary>
        /// Called when navigating away. Unsubscribes from any external events.
        /// GlobalMessageViewModel is a registered child and cleaned up automatically by base.
        /// </summary>
        public override void OnClosing()
        {
            base.OnClosing();
        }

        /// <summary>
        /// Disposes commands that hold PropertyChanged subscriptions on external ViewModels.
        /// </summary>
        public override void Dispose()
        {
            // SaveCatalogueTextFileDataCommand subscribes to this ViewModel's PropertyChanged
            _saveCatalogueTextFileDataCommand?.Dispose();

            base.Dispose();
        }

        /// <summary>
        /// Adds a message to the global message store which will then be displayed in the UI
        /// </summary>
        /// <param name="message"></param>
        /// <param name="messageType"></param>
        public void AddMessage(string message, Utils.WPF.Stores.MessageTypes messageType)
        {

            if (messageType == duHastNet.Utils.WPF.Stores.MessageTypes.Error)
            {
                //let user dismiss the message themselves for error messages, since they might want to copy the message text for further use, and errors are more important to see for a longer time
                _messageStore.EnqueueMessage(message, messageType);
            }
            else if (messageType == duHastNet.Utils.WPF.Stores.MessageTypes.Information)
            {
                //just flash message to user for information messages, since they are less important and user might not need to copy the message text, and it is better to dismiss them after a short time to avoid too many messages building up in the UI
                _messageStore.EnqueueMessage(message, messageType, dismissAfterSeconds: 2);
            }
            else
            {
                //default to short display time for other message types
                _messageStore.EnqueueMessage(message, messageType, dismissAfterSeconds: 5);
            }
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
            return duHastNet.Utils.DataConversion.TypeConverter.ConvertStringToType(cellEntryAsstring, property.StorageType);

        }

        /// <summary>
        /// Loads the catalogue text file data from file
        /// </summary>
        private void LoadData()
        {
            // read catalogue file and get header data ( formatted and unformatted ) and row data
            (_catalogueFileHeadersOriginal, _catalogueFileHeadersOriginalUnformatted, _catalogueFileDataOriginal) = Utilities.Revit.TypeCatalogueFileUtils.GetCatalogueFileData(SelectedFamily.FamilyFilePath.Value, this);

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
            }
            ;

            //update data rows
            DataRows = dataRows;

            //no read only columns
            ReadOnlyColumns = new List<string>();
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