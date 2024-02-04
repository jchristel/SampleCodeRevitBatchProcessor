using System;
using IronPython.Hosting;
using Microsoft.Scripting.Hosting;
using Serilog;
using RBP_Launcher.Utilities.Output;

namespace RBP_Launcher
{
    public class RunnerIronPython: Interfaces.IScriptRunner
    {
        public RunnerIronPython()
        {
            _searchPath = new List<string>();
        }

        public RunnerIronPython(List<string> searchPath)
        {
            _searchPath = searchPath;
        }

        // contains any search path provided
        private readonly List<string> _searchPath;


        public bool ExecuteScript(string scriptFilePath, List<string>? scriptArguments = null)
        {
            bool executedWithoutExceptions = true;
            try
            {
                ScriptRuntimeSetup setup = Python.CreateRuntimeSetup(null);
                ScriptRuntime runtime = new ScriptRuntime(setup);
                //assign args if required
                if (scriptArguments != null)
                {
                    //add the script path as first entry
                    scriptArguments.Insert(0, scriptFilePath);
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
                //var scope = engine.CreateScope();
                // alternative scope as per https://github.com/architecture-building-systems/revitpythonshell/blob/master/RpsRuntime/ScriptExecutor.cs
                var scope = Python.CreateModule(engine, "__main__");
                //make sure __file__ is set
                scope.SetVariable("__file__", scriptFilePath);

                // add default search paths
                AddDefaultSearchPath(engine: engine, scriptFilePath: scriptFilePath);
                // add config provided search path:
                AddSearchPathsFromSettings(engine:engine);

                try
                {
                    //run Python scripts from file
                    engine.ExecuteFile(scriptFilePath, scope);
                }
                catch(IronPython.Runtime.Exceptions.SystemExitException sysEx)
                {
                    // check the exit code
                    object? otherCode = null;
                    int exitCode = sysEx.GetExitCode(out otherCode);
                    // only do something if the exit code is not 0 ( all ok )
                    if (exitCode != 0) 
                    {
                        executedWithoutExceptions = false;
                        Log.Error($"Script {scriptFilePath} finished with system exit exception: {exitCode} and other code: {otherCode}");
                    }
                }
                catch (Exception ex)
                {
                    executedWithoutExceptions = false;
                    Log.Error($"Script {scriptFilePath} finished with exception: {ex}");
                }

                // Flush and close the StreamWriter
                outputWriter.Flush();
                outputWriter.Close();

                // Access the redirected output
                string output = outputStream.GetOutput();
                ServiceLocator.OutputObserver?.Update($"Redirected IronPython Output: {output}");

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

        /// <summary>
        /// Adds:
        ///     - script file path
        ///     - library file path
        /// to search path
        /// </summary>
        /// <param name="engine"></param>
        /// <param name="scriptFilePath"></param>
        private void AddDefaultSearchPath(ScriptEngine engine, string scriptFilePath)
        {
            // add the script file path
            //https://github.com/architecture-building-systems/revitpythonshell/blob/master/RpsRuntime/ScriptExecutor.cs
            var path = engine.GetSearchPaths();
            path.Add(Path.GetDirectoryName(scriptFilePath));
            // add the /lib folder
            string? latestInstallPath = Utilities.IronPythonInstall.GetLatestVersionInstallPath();
            if (latestInstallPath != null)
            {
                path.Add(Path.Join(latestInstallPath, "Lib"));
            }
            else
            {
                Log.Error("Was not able to determine latest Iron Python install path in {ClassName}.{MethodName}", nameof(RunnerIronPython), nameof(AddDefaultSearchPath));
                // this is bad..get out
                throw new Exception("Was not able to determine latest Iron Python install path");
            }
            // update the path variable
            engine.SetSearchPaths(path);
                    
        }

        /// <summary>
        /// Add the search paths defined in the settings file to the engine.
        /// </summary>
        private void AddSearchPathsFromSettings(ScriptEngine engine)
        {
            if(_searchPath != null && _searchPath.Count>0)
                { 
                var searchPaths = engine.GetSearchPaths();
                foreach (var path in _searchPath)
                {
                    searchPaths.Add(path);
                }
                engine.SetSearchPaths(searchPaths);
            }
        }
    }
}
