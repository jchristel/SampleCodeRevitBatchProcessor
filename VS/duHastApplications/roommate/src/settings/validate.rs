//! Standalone validation over the settings types — the checks that aren't a
//! single type's own `validate()` method. Split from the type definitions in
//! `mod.rs` so "what a field *is*" and "is this whole declaration coherent"
//! stay legible apart. Re-exported from `mod.rs`, so callers still use
//! `crate::settings::validate_drofus_fields`.

use super::{DrofusFieldConfig, FieldType};

/// Dry-run one strftime pattern so a typo (e.g. `%Q`) fails at startup, not
/// silently at compare time. `StrftimeItems` yields an `Item::Error` for any
/// specifier chrono doesn't know — walking the items is exactly the parse the
/// comparison will do later, minus a value.
fn validate_strftime(label: &str, which: &str, pattern: &str) -> anyhow::Result<()> {
    use chrono::format::{Item, StrftimeItems};
    if StrftimeItems::new(pattern).any(|item| matches!(item, Item::Error)) {
        anyhow::bail!(
            "drofus_fields entry '{}' has an invalid {} strftime pattern: '{}'",
            label,
            which,
            pattern
        );
    }
    Ok(())
}

/// Fail fast on a malformed dRofus field declaration — same "loud startup
/// error over a silent no-op" discipline as hierarchy tiers and builtin
/// properties:
/// - a `label` the dRofus CSV never declared. Can't run inside
///   `load_settings` itself: dRofus loads *after* settings in `main.rs`, so
///   the label set isn't known yet at that point — this runs as a separate
///   step once both are loaded.
/// - a `Date` field with no `format` — unusable without one.
/// - a `format`/`revit_format` given on a non-`Date` field — meaningless,
///   almost certainly a mistake rather than intentional.
/// - a `format`/`revit_format` that isn't a valid strftime pattern — it would
///   never parse any value, making the declaration a silent no-op.
pub fn validate_drofus_fields(fields: &[DrofusFieldConfig], all_labels: &[String]) -> anyhow::Result<()> {
    for field in fields {
        if !all_labels.iter().any(|l| l == &field.label) {
            anyhow::bail!("drofus_fields references unknown dRofus field label: '{}'", field.label);
        }
    }
    validate_drofus_field_shapes(fields)
}

/// The label-independent half of `validate_drofus_fields`: per-field
/// type/format consistency and strftime pattern validity. Split out for the
/// one caller that can't know the label set yet — an `Upload`-sourced project
/// with no CSV uploaded so far, whose declarations should still be checked
/// for everything checkable without data.
pub fn validate_drofus_field_shapes(fields: &[DrofusFieldConfig]) -> anyhow::Result<()> {
    for field in fields {
        match (field.field_type, &field.format) {
            (FieldType::Date, None) => {
                anyhow::bail!("drofus_fields entry '{}' has type = \"date\" but no format", field.label);
            }
            (other, Some(_)) if other != FieldType::Date => {
                anyhow::bail!("drofus_fields entry '{}' sets format but type is not \"date\"", field.label);
            }
            (FieldType::Date, Some(format)) => validate_strftime(&field.label, "format", format)?,
            _ => {}
        }
        if let Some(revit_format) = &field.revit_format {
            if field.field_type != FieldType::Date {
                anyhow::bail!(
                    "drofus_fields entry '{}' sets revit_format but type is not \"date\"",
                    field.label
                );
            }
            validate_strftime(&field.label, "revit_format", revit_format)?;
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::settings::CompareMode;

    /// A minimal `DrofusFieldConfig` for tests that only care about one
    /// aspect of the declaration.
    fn field(label: &str) -> DrofusFieldConfig {
        DrofusFieldConfig {
            label: label.to_string(),
            field_type: FieldType::default(),
            format: None,
            revit_format: None,
            qa: None,
        }
    }

    /// A declaration referencing a label the dRofus CSV never declared fails
    /// startup rather than silently never applying.
    #[test]
    fn test_validate_drofus_fields_rejects_unknown_label() {
        let fields = vec![DrofusFieldConfig { qa: Some(CompareMode::Ignore), ..field("Nonexistent") }];
        let all_labels = vec!["NetArea".to_string(), "Department".to_string()];

        assert!(validate_drofus_fields(&fields, &all_labels).is_err());
    }

    /// A declaration referencing a real label, with only a `qa` override and
    /// no `type`, passes validation (today's shipped behavior, generalized).
    #[test]
    fn test_validate_drofus_fields_accepts_known_label() {
        let fields = vec![DrofusFieldConfig { qa: Some(CompareMode::Exact), ..field("NetArea") }];
        let all_labels = vec!["NetArea".to_string(), "Department".to_string()];

        assert!(validate_drofus_fields(&fields, &all_labels).is_ok());
    }

    /// `type = "date"` with no `format` is unusable -- fails validation.
    #[test]
    fn test_validate_drofus_fields_date_without_format_fails() {
        let fields = vec![DrofusFieldConfig { field_type: FieldType::Date, ..field("LastSync") }];
        let all_labels = vec!["LastSync".to_string()];

        assert!(validate_drofus_fields(&fields, &all_labels).is_err());
    }

    /// `type = "date"` with a `format` passes validation.
    #[test]
    fn test_validate_drofus_fields_date_with_format_passes() {
        let fields = vec![DrofusFieldConfig {
            field_type: FieldType::Date,
            format: Some("%-m/%-d/%Y %-I:%M:%S %p %z".to_string()),
            ..field("LastSync")
        }];
        let all_labels = vec!["LastSync".to_string()];

        assert!(validate_drofus_fields(&fields, &all_labels).is_ok());
    }

    /// A `format` on a non-date field is meaningless -- fails validation.
    #[test]
    fn test_validate_drofus_fields_format_on_non_date_fails() {
        let fields = vec![DrofusFieldConfig { format: Some("whatever".to_string()), ..field("NetArea") }];
        let all_labels = vec!["NetArea".to_string()];

        assert!(validate_drofus_fields(&fields, &all_labels).is_err());
    }

    /// A strftime typo (`%Q` is not a chrono specifier) fails at startup --
    /// otherwise the pattern would pass config validation and just silently
    /// never parse anything at compare time.
    #[test]
    fn test_validate_drofus_fields_malformed_strftime_fails() {
        let fields = vec![DrofusFieldConfig {
            field_type: FieldType::Date,
            format: Some("%Q/%-d/%Y".to_string()),
            ..field("LastSync")
        }];
        let all_labels = vec!["LastSync".to_string()];

        assert!(validate_drofus_fields(&fields, &all_labels).is_err());
    }

    /// `revit_format` follows `format`'s rules: legal (and dry-run-validated)
    /// on a date field, rejected on any other type.
    #[test]
    fn test_validate_drofus_fields_revit_format_rules() {
        let all_labels = vec!["LastSync".to_string(), "NetArea".to_string()];

        let good = vec![DrofusFieldConfig {
            field_type: FieldType::Date,
            format: Some("%-m/%-d/%Y %-I:%M:%S %p %z".to_string()),
            revit_format: Some("%Y-%m-%d %H:%M:%S".to_string()),
            ..field("LastSync")
        }];
        assert!(validate_drofus_fields(&good, &all_labels).is_ok());

        let on_non_date = vec![DrofusFieldConfig {
            revit_format: Some("%Y-%m-%d".to_string()),
            ..field("NetArea")
        }];
        assert!(validate_drofus_fields(&on_non_date, &all_labels).is_err());

        let malformed = vec![DrofusFieldConfig {
            field_type: FieldType::Date,
            format: Some("%Y-%m-%d".to_string()),
            revit_format: Some("%Q".to_string()),
            ..field("LastSync")
        }];
        assert!(validate_drofus_fields(&malformed, &all_labels).is_err());
    }
}
