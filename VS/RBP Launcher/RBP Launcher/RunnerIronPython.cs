using System;
using IronPython.Hosting;
using Microsoft.Scripting.Hosting;
using Serilog;

namespace RBP_Launcher
{
    public class RunnerIronPython:IScriptRunner
    {
        public bool ExecuteScript(string scriptFilePath, List<string> scriptArguments = null)
        {
            bool executedWithoutExceptions = true;
            try
            {
                ScriptRuntimeSetup setup = Python.CreateRuntimeSetup(null);
                ScriptRuntime runtime = new ScriptRuntime(setup);
                //assign args if required
                if (scriptArguments != null && scriptArguments.Count > 0)
                { 
                    runtime.GetSysModule().SetVariable("argv", scriptArguments);
                }

                // get the engine
                ScriptEngine engine = Python.GetEngine(runtime);

                // Redirect standard output and error
                var outputStream = new  Utilities.RedirectedOutput();

                // Create a StreamWriter using the custom RedirectedOutput stream
                var outputWriter = new StreamWriter(outputStream);

                // Set the custom TextWriter as the standard output and error for the engine
                engine.Runtime.IO.SetOutput(outputWriter.BaseStream, outputWriter);
                engine.Runtime.IO.SetErrorOutput(outputWriter.BaseStream, outputWriter);


                // set up a scope
                var scope = engine.CreateScope();

                //run Python scripts from file
                engine.ExecuteFile(scriptFilePath, scope);

                // Flush and close the StreamWriter
                outputWriter.Flush();
                outputWriter.Close();

                // Access the redirected output
                string output = outputStream.GetOutput();
                Console.WriteLine($"Redirected Output: {output}");

            }
            catch (Microsoft.Scripting.SyntaxErrorException syntaxError)
            {
                Log.Error(syntaxError, "A syntax error occurred in {ClassName}.{MethodName}", nameof(RunnerIronPython), nameof(ExecuteScript));
                executedWithoutExceptions = false;
            }
            catch (Exception ex)
            {
                Log.Error(ex, "An error occurred in {ClassName}.{MethodName}", nameof(RunnerIronPython), nameof(ExecuteScript));
                executedWithoutExceptions = false;
            }

            return executedWithoutExceptions;

        }
    }
}
