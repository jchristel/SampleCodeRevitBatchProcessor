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
using System.Runtime.Remoting.Channels;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Input;

namespace PushIt.ViewModels
{
    public class GlobalMessageViewModel : ViewModelBase
    {
        private readonly Stores.MessageStore _messageStore;

        public string CurrentMessage => _messageStore.CurrentMessage;
        public bool IsErrorMessage  => _messageStore.CurrentMessageType == Stores.MessageTypes.Error;
        public bool IsInformationMessage => _messageStore.CurrentMessageType == Stores.MessageTypes.Information;
        public bool HasMessage => _messageStore.HasCurrentMessage;


        public ICommand ClearMessageCommand { get; }


        private void MessageStore_CurrentMessageChanged()
        {   
           OnPropertyChanged(nameof(CurrentMessage));
            OnPropertyChanged(nameof(HasMessage));
        }

        private void MessageStore_CurrentMessageTypeChanged()
        {
            OnPropertyChanged(nameof(IsErrorMessage));
            OnPropertyChanged(nameof(IsInformationMessage));
        }

        public override void OnClosing()
        {
            _messageStore.CurrentMessageChanged -= MessageStore_CurrentMessageChanged;
            _messageStore.CurrentMessageTypeChanged -= MessageStore_CurrentMessageTypeChanged;
        }

        public GlobalMessageViewModel(Stores.MessageStore messageStore)
        {
            _messageStore = messageStore;
            _messageStore.CurrentMessageChanged += MessageStore_CurrentMessageChanged;
            _messageStore.CurrentMessageTypeChanged += MessageStore_CurrentMessageTypeChanged;

            ClearMessageCommand = new Commands.ClearMessageCommand(_messageStore);

        }
    }
}
