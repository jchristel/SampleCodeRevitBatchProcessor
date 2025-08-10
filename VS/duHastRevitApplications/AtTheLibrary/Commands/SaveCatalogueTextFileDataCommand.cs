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

using duHastNet.UI.CustomControls;
using duHastNet.Utils.WPF.Stores;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.IO;
using System.Linq;


namespace duHastNet.AtTheLibrary.Commands
{
    public class SaveCatalogueTextFileDataCommand : Utils.WPF.Commands.CommandBase
    {
        private readonly ViewModels.TypeCatalogueViewModel _typeDataViewModel;
        private ViewModels.TypeCatalogueViewModel TypeDataViewModel
        {
            get => _typeDataViewModel;
        }


        Models.FamilyDataModel _selectedFamily;

        /// <summary>
        /// this command is always available
        /// </summary>
        /// <param name="parameter"></param>
        /// <returns></returns>
        public override bool CanExecute(object parameter)
        {
            // check if there is a family selected
            if (_typeDataViewModel.SelectedFamily == null)
            {
                return false;
            }
            return true;
        }

        private void OnViewModelPropertyChanged(object sender, PropertyChangedEventArgs e)
        {
            // check if the property that changed is the one that we are interested in
            if (e.PropertyName == nameof(ViewModels.TypeCatalogueViewModel.SelectedFamily))
            {
                OnCanExecutedChanged();
            }
        }

        /// <summary>
        /// check if data is valid        
        /// </summary>
        /// <param name="parameter"></param>
        public override void Execute(object parameter)
        {
            try
            {
                // Get the CellEditor from the parameter
                if (parameter is CellEditor cellEditor)
                {
                    // Get the current data as displayed in the grid
                    var (headers, dataRows) = cellEditor.GetCurrentData();

                    // Get data from the view model and do some sanity checking
                    var selectedFamily = _typeDataViewModel.SelectedFamily;

                    if (selectedFamily == null)
                    {
                        TypeDataViewModel.AddMessage("No family selected", MessageTypes.Error);
                        return;
                    }

                    // Validate the data
                    if (headers == null || headers.Count == 0)
                    {
                        // Handle error - no column headers
                        TypeDataViewModel.AddMessage("No header row", MessageTypes.Error);
                    }

                    if (dataRows == null || dataRows.Count == 0)
                    {
                        // Handle error - no data rows
                        TypeDataViewModel.AddMessage("No type data provided. Catalogue file needs to contain at least 1 row.", MessageTypes.Error);
                        return;
                    }

                    //do some sanity checking:
                    if (!CheckTableData(headers, dataRows)) { return; }

                    //convert data to string so it can be written to file
                    List<List<string>> convertedTableData = ConvertTableData(headers, dataRows);
                    if (convertedTableData == null) { return; }

                    // make sure headers contain the original unit data, as well as wiping the first header since type name is usually empty
                    List<string> convertedHeader = ConvertHeaderRow(headers, TypeDataViewModel.CatalogueFileHeadersOriginalUnformatted);

                    // Process and save the data
                    SaveDataToTextFile(selectedFamily.FamilyFilePath.Value, convertedHeader, convertedTableData);
                }
                else
                {
                    //nothing to do here
                }

                return;
            }
            catch (Exception ex)
            {
                // Handle save errors
                TypeDataViewModel.AddMessage($"Failed to save type catalogue text file with error (in execute) {ex}", MessageTypes.Error);
            }
        }

        /// <summary>
        /// Saves the catalogue data to a text file ( old file is over written 0
        /// </summary>
        /// <param name="selectedFamilyFilePath"></param>
        /// <param name="headers"></param>
        /// <param name="dataRows"></param>
        private void SaveDataToTextFile(string selectedFamilyFilePath, List<string> headers, List<List<string>> dataRows)
        {
            try
            {
                //make sure to change extension to txt
                string catalogueFilePath = Path.GetExtension(selectedFamilyFilePath).Equals(".txt", StringComparison.OrdinalIgnoreCase)
                    ? selectedFamilyFilePath
                    : Path.ChangeExtension(selectedFamilyFilePath, ".txt");

                //save data
                duHastNet.FileIOWrapper.WriteToColumnBasedTextFile csvWriter = new FileIOWrapper.WriteToColumnBasedTextFile();
                csvWriter.WriteToTextFile(
                    filePath: catalogueFilePath,
                    header: headers,
                    data: dataRows);

                //check if that is all ok
                if (csvWriter.ErrorHistory.Count > 0)
                {
                    foreach (var row in csvWriter.ErrorHistory)
                    {
                        TypeDataViewModel.AddMessage(row, MessageTypes.Error);
                    }

                    return;
                }

                // write all status ok message
                TypeDataViewModel.AddMessage($"Successfully updated type catalogue file {catalogueFilePath}!", MessageTypes.Information);
            }
            catch (Exception ex)
            {
                // Handle save errors
                TypeDataViewModel.AddMessage($"Failed to save type catalogue text file with error {ex}", MessageTypes.Error);
            }
        }


        /// <summary>
        /// does some sanity checks on the table data ( type name checks only )
        /// </summary>
        /// <param name="header"></param>
        /// <param name="tableData"></param>
        /// <returns></returns>
        private bool CheckTableData(List<string> header, List<List<object>> tableData)
        {
            try
            {
                //check: type name is defined
                //check: no duplicated type names
                //check: type name column exists and is first column

                // Check: type name column exists and is first column
                const string typeNameColumnExpected = Models.Constants.ColumnHeaderTypeCatalogueFamilyTypeName;
                if (!header[0].Equals(typeNameColumnExpected, StringComparison.OrdinalIgnoreCase))
                {
                    TypeDataViewModel.AddMessage($"First column must be '{typeNameColumnExpected}', but found '{header[0]}'", MessageTypes.Error);
                    return false;
                }


                // Get the index of the type name column (should be 0, but being defensive)
                int typeNameColumnIndex = 0;

                // Check: type name is defined(no empty/ null type names)
                var rowsWithEmptyTypeNames = new List<int>();
                for (int i = 0; i < tableData.Count; i++)
                {
                    var row = tableData[i];

                    // Check if row has enough columns
                    if (row.Count <= typeNameColumnIndex)
                    {
                        TypeDataViewModel.AddMessage($"Row {i + 1} is missing the type name column", MessageTypes.Error);
                        return false;
                    }

                    // Check if type name is empty or null
                    var typeName = row[typeNameColumnIndex]?.ToString()?.Trim();
                    if (string.IsNullOrEmpty(typeName))
                    {
                        rowsWithEmptyTypeNames.Add(i + 1); // +1 for human-readable row numbers
                    }
                }

                if (rowsWithEmptyTypeNames.Any())
                {
                    var rowNumbers = string.Join(", ", rowsWithEmptyTypeNames);
                    TypeDataViewModel.AddMessage($"Type name is missing or empty in row(s): {rowNumbers}", MessageTypes.Error);
                    return false;
                }

                // Check: no duplicated type names
                var typeNames = tableData
                    .Select((row, index) => new {
                        RowNumber = index + 1,
                        TypeName = row[typeNameColumnIndex]?.ToString()?.Trim()
                    })
                    .Where(x => !string.IsNullOrEmpty(x.TypeName))
                    .ToList();

                var duplicateGroups = typeNames
                    .GroupBy(x => x.TypeName, StringComparer.OrdinalIgnoreCase)
                    .Where(g => g.Count() > 1)
                    .ToList();

                if (duplicateGroups.Any())
                {
                    var duplicateMessages = duplicateGroups.Select(group =>
                    {
                        var rowNumbers = string.Join(", ", group.Select(x => x.RowNumber));
                        return $"'{group.Key}' appears in rows: {rowNumbers}";
                    });

                    var allDuplicates = string.Join("; ", duplicateMessages);
                    TypeDataViewModel.AddMessage($"Duplicate type names found: {allDuplicates}", MessageTypes.Error);
                    return false;
                }

                return true;
            }
            catch (Exception ex)
            {
                TypeDataViewModel.AddMessage($"Type data failed check with error: {ex}", MessageTypes.Error);
                return false;
            }
        }


        /// <summary>
        /// Convertes the table data using the Selected family properties to get the appropriate type to convert from
        /// </summary>
        /// <param name="header"></param>
        /// <param name="tableData"></param>
        /// <returns></returns>
        private List<List<string>> ConvertTableData(List<string> header, List<List<object>> tableData)
        {
            List<List<string>> convertedData = new List<List<string>>();
            try
            {
                //assume column 0 index is always a string
                //any other header entry has a matching property in Selected Family properties
                //which provides the data type to convert from

                // Process each row
                for (int rowIndex = 0; rowIndex < tableData.Count; rowIndex++)
                {
                    var row = tableData[rowIndex];
                    var convertedRow = new List<string>();

                    // Process each column in the row
                    for (int colIndex = 0; colIndex < header.Count; colIndex++)
                    {
                        string convertedValue = "";

                        // Check if the row has enough columns
                        if (colIndex >= row.Count)
                        {
                            convertedValue = ""; // Default to empty string for missing columns
                        }
                        else
                        {
                            var cellValue = row[colIndex];

                            if (colIndex == 0)
                            {
                                // Column 0 is always treated as string (Type Name)
                                convertedValue = cellValue?.ToString()?.Trim() ?? "";
                            }
                            else
                            {
                                // For other columns, find matching property in Selected Family
                                var headerName = header[colIndex];
                                var familyProperty = _typeDataViewModel.SelectedFamily.GetPropertyByName(headerName);

                                if (familyProperty == null)
                                {
                                    // Property not found in family - treat as string
                                    convertedValue = cellValue?.ToString()?.Trim() ?? "";
                                    TypeDataViewModel.AddMessage($"Property '{headerName}' not found in family '{_typeDataViewModel.SelectedFamily.FamilyName.Value}', treating as string", MessageTypes.Error);
                                }
                                else
                                {
                                    // Convert based on the property's storage type
                                    convertedValue = ConvertValueToString(cellValue, familyProperty.StorageType, headerName, rowIndex + 1);
                                }
                            }
                        }

                        convertedRow.Add(convertedValue);
                    }

                    convertedData.Add(convertedRow);
                }

                return convertedData;
            }
            catch (Exception ex)
            {
                TypeDataViewModel.AddMessage($"Failed to convert table data with error: {ex}", MessageTypes.Error);
                return null;
            }
        }


        /// <summary>
        /// 
        /// </summary>
        /// <param name="currentHeader"></param>
        /// <param name="oldHeader"></param>
        /// <returns></returns>
        private List<string> ConvertHeaderRow(List<string> currentHeader, List<string> oldHeader)
        {
            //build a dictioanry containing the formatted header to the unformatted header
            Dictionary<string, string> headerMapping = new Dictionary<string, string>();

            foreach (string oldEntry in oldHeader)
            {
                string formattedHeaderEntry = duHastNet.RevitUtils.Families.TypeCatalogueFileReader.GetParameterNameFromHeaderEntry(oldEntry);
                headerMapping[formattedHeaderEntry] = oldEntry;
            }

            List<string> convertedHeader = new List<string> { "" };

            //skip the first entry since already added as empty value      
            for (int i = 1; i< currentHeader.Count; i++)
            {
                string oldEntryRetrieved;
                if (headerMapping.TryGetValue(currentHeader[i], out oldEntryRetrieved))
                {
                    // Key was found, use the retrieved value
                    convertedHeader.Add(oldEntryRetrieved);
                }
                else
                {
                    //this should not happen!!
                    TypeDataViewModel.AddMessage($"Failed to find header with unit data for header: {currentHeader[i]}", MessageTypes.Error);
                    // Key not found, use original header 
                    convertedHeader.Add(currentHeader[i]);
                }
            }

            return convertedHeader;
        }


        /// <summary>
        /// Converts a single cell value to string based on the target storage type
        /// </summary>
        /// <param name="value">The value to convert</param>
        /// <param name="targetType">The target storage type from the family property</param>
        /// <param name="columnName">Column name for error reporting</param>
        /// <param name="rowNumber">Row number for error reporting</param>
        /// <returns>String representation of the converted value</returns>
        private string ConvertValueToString(object value, Type targetType, string columnName, int rowNumber)
        {
            try
            {
                // Handle null or empty values
                if (value == null)
                    return "";

                string stringValue = value.ToString().Trim();
                if (string.IsNullOrEmpty(stringValue))
                    return "";

                // If target type is string, return as-is
                if (targetType == typeof(string))
                    return stringValue;

                // Convert based on target type
                if (targetType == typeof(int))
                {
                    if (int.TryParse(stringValue, out int intResult))
                        return intResult.ToString();
                    else
                        throw new FormatException($"Cannot convert '{stringValue}' to integer");
                }
                else if (targetType == typeof(double))
                {
                    if (double.TryParse(stringValue, out double doubleResult))
                        return doubleResult.ToString("G"); // General format preserves precision
                    else
                        throw new FormatException($"Cannot convert '{stringValue}' to double");
                }
                else if (targetType == typeof(bool))
                {
                    // Handle various boolean representations
                    string lowerValue = stringValue.ToLower();
                    if (lowerValue == "true" || lowerValue == "yes" || lowerValue == "1" || lowerValue == "on")
                        return "1";
                    else if (lowerValue == "false" || lowerValue == "no" || lowerValue == "0" || lowerValue == "off")
                        return "0";
                    else if (bool.TryParse(stringValue, out bool boolResult))
                        return boolResult ? "1" : "0";
                    else
                        throw new FormatException($"Cannot convert '{stringValue}' to boolean");
                }
                else if (targetType == typeof(DateTime))
                {
                    if (DateTime.TryParse(stringValue, out DateTime dateResult))
                        return dateResult.ToString("yyyy-MM-dd HH:mm:ss");
                    else
                        throw new FormatException($"Cannot convert '{stringValue}' to DateTime");
                }
                else
                {
                    // For any other type, return as string
                    TypeDataViewModel.AddMessage($"Unknown storage type '{targetType.Name}' for column '{columnName}', treating as string", MessageTypes.Error);
                    return stringValue;
                }
            }
            catch (FormatException ex)
            {
                string errorMsg = $"Row {rowNumber}, Column '{columnName}': {ex.Message}";
                TypeDataViewModel.AddMessage(errorMsg, MessageTypes.Error);

                // Return the original string value as fallback
                return value?.ToString()?.Trim() ?? "";
            }
            catch (Exception ex)
            {
                string errorMsg = $"Row {rowNumber}, Column '{columnName}': Unexpected conversion error - {ex.Message}";
                TypeDataViewModel.AddMessage(errorMsg, MessageTypes.Error);

                // Return the original string value as fallback
                return value?.ToString()?.Trim() ?? "";
            }
        }


        public SaveCatalogueTextFileDataCommand(
           ViewModels.TypeCatalogueViewModel typeDataViewModel,
           Models.FamilyDataModel selectedFamily
        )
        {
            _typeDataViewModel = typeDataViewModel;
            _selectedFamily = selectedFamily;

            // Subscribe to property changes to update CanExecute
            _typeDataViewModel.PropertyChanged += OnViewModelPropertyChanged;
        }
    }

}
