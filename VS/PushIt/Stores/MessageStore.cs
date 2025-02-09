using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PushIt.Stores
{
    public enum MessageTypes
    {
        Error,
        Information
    }
    public class MessageStore
    {
        public string CurrentMessage { get; private set; }
        public MessageTypes CurrentMessageType { get; private set; }

        public void SetCurrentMessage(string message, MessageTypes messageType)
        {
            CurrentMessage = message;
            CurrentMessageType = messageType;
        }

    }
}
