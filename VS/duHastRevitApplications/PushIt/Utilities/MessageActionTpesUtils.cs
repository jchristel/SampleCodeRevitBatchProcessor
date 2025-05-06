using System.Collections.Generic;
using System.Linq;

namespace duHastNet.PushIt.Utilities
{
    public class MessageActionTypesUtils
    {
        /// <summary>
        /// Combines multiple message types into a single message type by counting the number of each type and returning the highest priority type.
        /// </summary>
        public static Utils.WPF.Stores.MessageTypes CombineMessageActionType(List<Utils.WPF.Stores.MessageTypes> messageTypes)
        {
            //count the number of each message type
            int infoCount = messageTypes.Count(x => x == Utils.WPF.Stores.MessageTypes.Information);
            int errorCount = messageTypes.Count(x => x == Utils.WPF.Stores.MessageTypes.Error);
            int logCount = messageTypes.Count(x => x == Utils.WPF.Stores.MessageTypes.Log);

            //if there are any errors, return error
            if (errorCount > 0)
            {
                return Utils.WPF.Stores.MessageTypes.Error;
            }
            // if there are no errors but info messages, return info
            else if (infoCount > 0)
            {
                return Utils.WPF.Stores.MessageTypes.Information;
            }
            // if there are no errors or info messages but log messages, return log
            else if (logCount > 0)
            {
                return Utils.WPF.Stores.MessageTypes.Log;
            }
            // if there are no errors, info or log messages, return information
            else
            {
                return Utils.WPF.Stores.MessageTypes.Information;
            }
        }
    }
}
