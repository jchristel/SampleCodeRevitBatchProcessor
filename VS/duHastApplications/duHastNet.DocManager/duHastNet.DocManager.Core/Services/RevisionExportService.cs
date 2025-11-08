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

using CsvHelper;
using CsvHelper.Configuration;
using duHastNet.DocManager.Core.Models;
using System.Globalization;

namespace duHastNet.DocManager.Core.Services;

/// <summary>
/// Service responsible for exporting revisions to CSV format
/// </summary>
public class RevisionExportService
{
    /// <summary>
    /// Exports revisions to a CSV file
    /// </summary>
    /// <param name="filePath">Path where CSV file will be saved</param>
    /// <param name="revisions">Collection of revisions to export</param>
    /// <returns>True if export successful, false otherwise</returns>
    public bool ExportRevisions(
        string filePath,
        IEnumerable<Revision> revisions)
    {
        try
        {
            // Convert to list for multiple enumeration
            var revisionsList = revisions.ToList();

            using var writer = new StreamWriter(filePath);
            using var csv = new CsvWriter(writer, new CsvConfiguration(CultureInfo.InvariantCulture)
            {
                HasHeaderRecord = true
            });

            // Write header row
            WriteHeader(csv);

            // Write data rows
            foreach (var revision in revisionsList)
            {
                WriteRevisionRow(csv, revision);
            }

            return true;
        }
        catch
        {
            return false;
        }
    }

    /// <summary>
    /// Writes the CSV header row
    /// </summary>
    private void WriteHeader(CsvWriter csv)
    {
        csv.WriteField("Id");
        csv.WriteField("Revision Date");
        csv.WriteField("Description");
        csv.WriteField("Document Count");
        csv.NextRecord();
    }

    /// <summary>
    /// Writes a single revision row
    /// </summary>
    private void WriteRevisionRow(CsvWriter csv, Revision revision)
    {
        csv.WriteField(revision.Id);
        csv.WriteField(revision.RevisionDate.ToString("yyyy-MM-dd"));
        csv.WriteField(revision.Description ?? string.Empty);
        csv.WriteField(revision.DocumentIds.Count);
        csv.NextRecord();
    }
}
