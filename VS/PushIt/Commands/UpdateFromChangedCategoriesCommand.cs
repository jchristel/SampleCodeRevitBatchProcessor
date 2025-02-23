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

using duHast.PushIt.ViewModels;
using System;
using System.Collections.Generic;
using System.ComponentModel;

namespace duHast.PushIt.Commands
{
    public class UpdateFromChangedCategoriesCommand : Utils.WPF.Commands.CommandBase
    {
       
   
        private readonly Models.RevitDataModel _revitDataModel;
        private readonly ViewModels.RoomsSelectionViewModel _roomsSelectionViewModel;
        //private readonly Services.NavigationService _reservationViewNavigationService;

        private readonly Utils.WPF.Stores.MessageStore _messageStore;
        private readonly Action _action;

        /// <summary>
        /// this command is always available
        /// </summary>
        /// <param name="parameter"></param>
        /// <returns></returns>
        public override bool CanExecute(object parameter)
        {
            //always available
            return true;
        }

        private void OnViewModelPropertyChanged(object sender, PropertyChangedEventArgs e)
        {
            //nothing required in this command
        }

        public override void Execute(object parameter)
        {
            try
            {
                // before invoking the action, check if the category selection is changed in compared to the settings stored in the data model
                // if so, update the data model and invoke the action
                //otherwise pop message to user that no changes were made

                // get the current category selection from the view model
                List<string> supportedCategoryNamesFromViewModel = new List<string>();
                var selectedCategories = _roomsSelectionViewModel.SupportedCategories;
                foreach (SupportedCategoryViewModel category in selectedCategories)
                {
                    if (category.IsSelected)
                    {
                        supportedCategoryNamesFromViewModel.Add(category.CategoryName);
                    }
                }

                //check if any categories are selected
                if (supportedCategoryNamesFromViewModel.Count == 0)
                {
                    _messageStore.SetCurrentMessage("Please select at least one category to proceed.", Utils.WPF.Stores.MessageTypes.Error);
                    return;
                }

                // compare the category selection from the view model with the one stored in the data model
                bool needUpdate = false;

                // if the count of the categories is different, we need to update
                if (supportedCategoryNamesFromViewModel.Count != _revitDataModel.Settings.SupportedCategories.Count)
                {
                    needUpdate = true;
                }
                else
                {
                    // if the count is the same, check if the category names are the same
                    foreach (string categoryName in supportedCategoryNamesFromViewModel)
                    {
                        // if a category name is not in the list of supported categories, we need to update
                        if (!_revitDataModel.Settings.SupportedCategories.Contains(categoryName))
                        {
                            needUpdate = true;
                            break;
                        }
                    }
                }

                // if no update is needed, pop message to user and return
                if (!needUpdate)
                {
                    _messageStore.SetCurrentMessage("No changes in category selection detected.", Utils.WPF.Stores.MessageTypes.Information);
                    return;
                }

                //update the categories in the settings
                _revitDataModel.Settings.SupportedCategories = supportedCategoryNamesFromViewModel;

                // update the data model with the new category selection
                _action?.Invoke();
                _messageStore.SetCurrentMessage("Refreshed data after category update.", Utils.WPF.Stores.MessageTypes.Information);

            }
            catch (Exception ex)
            {
                _messageStore.SetCurrentMessage($"Failed to refresh data after category update: {ex.Message}", Utils.WPF.Stores.MessageTypes.Error);
            }
        }

        public UpdateFromChangedCategoriesCommand(
           ViewModels.RoomsSelectionViewModel roomsSelectionViewModel,
           Models.RevitDataModel revitDataModel,
           Utils.WPF.Stores.MessageStore messageStore,
           Action action
           )
        {
            _revitDataModel = revitDataModel;
            _roomsSelectionViewModel = roomsSelectionViewModel;
            _messageStore = messageStore;
            _action = action;
        }
    }
}
