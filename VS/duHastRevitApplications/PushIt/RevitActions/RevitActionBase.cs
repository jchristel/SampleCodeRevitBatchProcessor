using System.Collections.Generic;
using System.Linq;

namespace duHastNet.PushIt.RevitActions
{
    public class RevitActionBase
    {
        public Models.RevitDataModel RevitModel { get; set; }

        private List<(string, Utils.WPF.Stores.MessageTypes)> Messages { get; }

        public List<string> GetErrorMessages()
        {
            return Messages.Where(m => m.Item2 == Utils.WPF.Stores.MessageTypes.Error).Select(m => m.Item1).ToList();
        }

        public List<string> GetInformationMessages()
        {
            return Messages.Where(m => m.Item2 == Utils.WPF.Stores.MessageTypes.Information).Select(m => m.Item1).ToList();
        }

        public List<string> GetLogMessages()
        {
            return Messages.Where(m => m.Item2 == Utils.WPF.Stores.MessageTypes.Log).Select(m => m.Item1).ToList();
        }

        public List<(string, Utils.WPF.Stores.MessageTypes)> GetLogMessagesAndLogTypes()
        {
            return Messages;
        }

        public void AddMessage(string message, Utils.WPF.Stores.MessageTypes messageType)
        {
            Messages.Add((message, messageType));
        }

        public void ClearMessages()
        {
            Messages.Clear();
        }

        public (string message, Utils.WPF.Stores.MessageTypes messageType) GetReturnValue(string allOKMessage)
        {
            // get the ovearll error count
            int erroCount = GetErrorMessages().Count;

            // check if any error messages were added
            if (erroCount > 0)
            {
                // return the message
                return (string.Join("\n", GetErrorMessages()), Utils.WPF.Stores.MessageTypes.Error);
            }
            else
            {
                // return the message
                return (allOKMessage, Utils.WPF.Stores.MessageTypes.Information);
            }
        }

        public RevitActionBase()
        {
            Messages = new List<(string, Utils.WPF.Stores.MessageTypes)>();
        }
    }
}
