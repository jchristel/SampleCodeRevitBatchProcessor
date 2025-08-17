//
//License:
//
//
// Revit Batch Processor Sample Code
//
// BSD License
// Copyright 2025, Jan Christel
// All rights reserved.

using System;
using System.Collections.Generic;
using System.Linq;

namespace duHastNet.UI.CustomControls.CustomDataGrid.GridState
{
    /// <summary>
    /// Results from validating a DataGrid state for compatibility
    /// </summary>
    public class GridStateValidationResult
    {
        private readonly List<string> _errors = new List<string>();
        private readonly List<string> _warnings = new List<string>();

        /// <summary>
        /// Gets whether the validation passed (no errors)
        /// </summary>
        public bool IsValid => _errors.Count == 0;

        /// <summary>
        /// Gets the list of validation errors
        /// </summary>
        public IReadOnlyList<string> Errors => _errors.AsReadOnly();

        /// <summary>
        /// Gets the list of validation warnings
        /// </summary>
        public IReadOnlyList<string> Warnings => _warnings.AsReadOnly();

        /// <summary>
        /// Gets whether there are any warnings
        /// </summary>
        public bool HasWarnings => _warnings.Count > 0;

        /// <summary>
        /// Adds an error to the validation result
        /// </summary>
        /// <param name="error">The error message to add</param>
        public void AddError(string error)
        {
            if (!string.IsNullOrEmpty(error))
            {
                _errors.Add(error);
            }
        }

        /// <summary>
        /// Adds a warning to the validation result
        /// </summary>
        /// <param name="warning">The warning message to add</param>
        public void AddWarning(string warning)
        {
            if (!string.IsNullOrEmpty(warning))
            {
                _warnings.Add(warning);
            }
        }

        /// <summary>
        /// Gets a summary of the validation result
        /// </summary>
        /// <returns>Summary string</returns>
        public string GetSummary()
        {
            if (IsValid && !HasWarnings)
                return "Validation passed";

            var parts = new List<string>();

            if (_errors.Count > 0)
                parts.Add($"{_errors.Count} error(s)");

            if (_warnings.Count > 0)
                parts.Add($"{_warnings.Count} warning(s)");

            return string.Join(", ", parts);
        }

        /// <summary>
        /// Gets the full validation report
        /// </summary>
        /// <returns>Detailed validation report</returns>
        public string GetFullReport()
        {
            var report = new System.Text.StringBuilder();

            report.AppendLine("=== GRID STATE VALIDATION REPORT ===");
            report.AppendLine($"Status: {(IsValid ? "VALID" : "INVALID")}");
            report.AppendLine($"Summary: {GetSummary()}");

            if (_errors.Count > 0)
            {
                report.AppendLine();
                report.AppendLine("ERRORS:");
                foreach (var error in _errors)
                {
                    report.AppendLine($"  - {error}");
                }
            }

            if (_warnings.Count > 0)
            {
                report.AppendLine();
                report.AppendLine("WARNINGS:");
                foreach (var warning in _warnings)
                {
                    report.AppendLine($"  - {warning}");
                }
            }

            return report.ToString();
        }
    }
}