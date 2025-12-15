//
//License:
//
//
// Revit Batch Processor Sample Code
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


using duHastNet.DocManager.Core.Interfaces;
using duHastNet.DocManager.Core.Models.CurrentFolder.FilingRules;

namespace duHastNet.DocManager.UI.Shared.ViewModels
{
    /// <summary>
    /// ViewModel wrapper for IFilingRule to provide UI-friendly properties for ListView binding
    /// Translates between the domain model (IFilingRule) and the View (ListView)
    /// </summary>
    public class FilingRuleViewModel
    {
        /// <summary>
        /// Reference to the underlying domain rule
        /// Used for operations like Remove, Edit, and syncing to settings
        /// </summary>
        public IFilingRule UnderlyingRule { get; }

        /// <summary>
        /// The filing rule type as an enum for easy comparison
        /// </summary>
        public FilingRuleType RuleTypeEnum { get; }

        /// <summary>
        /// Display-friendly rule type name
        /// Examples: "Begins With", "Contains", "Not Begins With", "Not Contains", "Default"
        /// </summary>
        public string RuleType { get; }

        /// <summary>
        /// The filter value to match against
        /// For CatchAll rules, displays "(N/A)" instead of empty string
        /// </summary>
        public string FilterValue { get; }

        /// <summary>
        /// The target directory path where matched files will be moved
        /// </summary>
        public string TargetPath { get; }

        /// <summary>
        /// Indicates if this is a Default/CatchAll rule
        /// </summary>
        public bool IsDefault => RuleTypeEnum == FilingRuleType.Default;

        /// <summary>
        /// Creates a display model from a domain filing rule
        /// </summary>
        /// <param name="rule">The underlying IFilingRule to wrap</param>
        public FilingRuleViewModel(IFilingRule rule)
        {
            UnderlyingRule = rule ?? throw new ArgumentNullException(nameof(rule));

            // Determine rule type enum and display name based on concrete type
            RuleTypeEnum = GetRuleTypeEnum(rule);
            RuleType = GetRuleTypeDisplayName(RuleTypeEnum);

            // Format filter value for display (show "(N/A)" for CatchAll)
            FilterValue = FormatFilterValue(rule.ComparisonValue, RuleTypeEnum);

            // Target path as-is
            TargetPath = rule.TargetDirectory ?? string.Empty;
        }

        /// <summary>
        /// Determines the FilingRuleType enum from the concrete rule instance
        /// </summary>
        private static FilingRuleType GetRuleTypeEnum(IFilingRule rule)
        {
            return rule switch
            {
                BeginsWith => FilingRuleType.BeginsWith,
                Contains => FilingRuleType.Contains,
                NotBeginsWith => FilingRuleType.NotBeginsWith,
                NotContains => FilingRuleType.NotContains,
                CatchAll => FilingRuleType.Default,
                _ => throw new ArgumentException($"Unknown rule type: {rule.GetType().Name}", nameof(rule))
            };
        }

        /// <summary>
        /// Gets a user-friendly display name for the rule type
        /// </summary>
        private static string GetRuleTypeDisplayName(FilingRuleType ruleType)
        {
            return ruleType switch
            {
                FilingRuleType.BeginsWith => "Begins With",
                FilingRuleType.Contains => "Contains",
                FilingRuleType.NotBeginsWith => "Not Begins With",
                FilingRuleType.NotContains => "Not Contains",
                FilingRuleType.Default => "Default",
                _ => ruleType.ToString()
            };
        }

        /// <summary>
        /// Formats the filter value for display
        /// CatchAll rules show "(N/A)" instead of empty string
        /// </summary>
        private static string FormatFilterValue(string? comparisonValue, FilingRuleType ruleType)
        {
            // CatchAll rules don't use comparison value
            if (ruleType == FilingRuleType.Default)
            {
                return "(N/A)";
            }

            // Return value as-is, or empty string if null
            return comparisonValue ?? string.Empty;
        }
    }
}
