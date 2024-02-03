using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace RBP_Launcher.Utilities
{
    // Console observer implementation
    public class ConsoleOutputObserver : RBP_Launcher.Interfaces.IOutputObserver
    {
        private readonly List<string> greenKeywords = new List<string> { Output.KeyWords.True };
        private readonly List<string> redKeywords = new List<string> { Output.KeyWords.Error, Output.KeyWords.Exception, Output.KeyWords.False };
        public void Update(string message)
        {
            // Check if the message contains any green keywords
            foreach (var keyword in greenKeywords)
            {
                int index = -1;
                while ((index = message.IndexOf(keyword, index + 1, StringComparison.OrdinalIgnoreCase)) != -1)
                {
                    // Print the part before the keyword in red
                    Console.ForegroundColor = ConsoleColor.White;
                    Console.Write(message.Substring(0, index));

                    // Print the keyword in green
                    Console.ForegroundColor = ConsoleColor.Green;
                    Console.Write(keyword);

                    // Update the message to exclude the part already printed
                    message = message.Substring(index + keyword.Length);
                }
            }

            // Check if the message contains any yellow keywords
            foreach (var keyword in redKeywords)
            {
                int index = -1;
                while ((index = message.IndexOf(keyword, index + 1, StringComparison.OrdinalIgnoreCase)) != -1)
                {
                    // Print the part before the keyword in red
                    Console.ForegroundColor = ConsoleColor.White;
                    Console.Write(message.Substring(0, index));

                    // Print the keyword in yellow
                    Console.ForegroundColor = ConsoleColor.Red;
                    Console.Write(keyword);

                    // Update the message to exclude the part already printed
                    message = message.Substring(index + keyword.Length);
                }
            }

            // Print the remaining part of the message in red
            Console.ForegroundColor = ConsoleColor.White;
            Console.WriteLine(message);

            Console.ResetColor(); // Reset color to default
        }
    }
}
