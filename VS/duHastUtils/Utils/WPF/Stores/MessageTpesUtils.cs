using System.Collections.Generic;
using System.Linq;

namespace duHastNet.Utils.WPF.Stores
{
    public class MessageTypesUtils
    {
        /// <summary>
        /// Combines multiple message types into a single message type by counting the number of each type and returning the highest priority type.
        /// </summary>
        public static MessageTypes CombineMessageType(List<MessageTypes> messageTypes)
        {
            //count the number of each message type
            int infoCount = messageTypes.Count(x => x == MessageTypes.Information);
            int errorCount = messageTypes.Count(x => x == MessageTypes.Error);
            int logCount = messageTypes.Count(x => x == MessageTypes.Log);

            //if there are any errors, return error
            if (errorCount > 0)
            {
                return MessageTypes.Error;
            }
            // if there are no errors but info messages, return info
            else if (infoCount > 0)
            {
                return MessageTypes.Information;
            }
            // if there are no errors or info messages but log messages, return log
            else if (logCount > 0)
            {
                return MessageTypes.Log;
            }
            // if there are no errors, info or log messages, return information
            else
            {
                return MessageTypes.Information;
            }
        }
    }
}
