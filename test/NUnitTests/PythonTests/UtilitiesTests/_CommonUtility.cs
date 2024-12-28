using PythonTests.Setup;

namespace PythonTests.UtilitiesTests
{
    /// <summary>
    /// Delegate for writing report data.
    /// </summary>
    /// <param name="parameters">A dictionary containing the parameters for the write_report_data function.</param>
    /// <returns>A dynamic result object containing the status and message of the write operation.</returns>
    public delegate dynamic WriteReportDataDelegate(Dictionary<string, object> parameters);

    /// <summary>
    /// Delegate for reading report data.
    /// </summary>
    /// <param name="parameters">A dictionary containing the parameters for the read_report_data function.</param>
    /// <returns>A dynamic result object containing the status and message of the write operation.</returns>
    public delegate dynamic ReadReportDataDelegate(Dictionary<string, object> parameters);

    
    
}
