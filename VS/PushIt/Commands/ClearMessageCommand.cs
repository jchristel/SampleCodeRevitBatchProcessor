using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PushIt.Commands
{
    public class ClearMessageCommand : CommandBase
    {
        private readonly Stores.MessageStore _messageStore;
        public override bool CanExecute(object parameter)
        {
            return true;
        }

        public override void Execute(object parameter)
        {
            _messageStore.ClearCurrentMessage();
        }

        public void RaiseCanExecuteChanged()
        {
            OnCanExecutedChanged();
        }

        public ClearMessageCommand(Stores.MessageStore messageStore)
        {
            _messageStore = messageStore;
        }
    }
}
