//! Standalone validation over the settings types — the checks that aren't a
//! single type's own `validate()` method. Split from the type definitions in
//! `mod.rs` so "what a field *is*" and "is this whole declaration coherent"
//! stay legible apart. Re-exported from `mod.rs`, so callers still use
//! `crate::settings::validate_drofus_fields`.

use super::{Band, ColourMode, ColourPlan, Colouring, DrofusFieldConfig, FieldType};

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

/// Fail fast on a malformed colour-plan library — same "loud startup error over
/// a silent no-op" discipline as the other validators. Two checks:
/// - **At most one `active` plan** (more than one is ambiguous: which does the
///   viewer picker default to?). Same single-selection rule as the settings
///   dir's `is_default`, but within one file so it runs in the normal load step.
/// - **`Bands` colourings are a sorted, disjoint partition** (see
///   `validate_bands`).
///
/// Property names are deliberately **not** validated: a name that doesn't
/// resolve on a room just renders that room "no data" grey in the browser (the
/// `room_label` "an unresolvable name contributes nothing" precedent), and room
/// properties are source-native and vary, so a hard fail here would reject
/// legitimate configs.
pub fn validate_colour_plans(plans: &[ColourPlan]) -> anyhow::Result<()> {
    let active: Vec<&str> = plans.iter().filter(|p| p.active).map(|p| p.name.as_str()).collect();
    if active.len() > 1 {
        anyhow::bail!(
            "more than one colour plan is marked active ({:?}) — at most one may be active",
            active
        );
    }
    for plan in plans {
        match &plan.mode {
            ColourMode::PropertyCompare { colouring: Colouring::Bands { bands }, .. } => {
                validate_bands(&plan.name, bands)?;
            }
            // A date-range `format`, when given, must be a real strftime pattern
            // — same dry-run as `drofus_fields`, so a typo fails at load rather
            // than silently never parsing any room date at colour time.
            ColourMode::DateRange { format: Some(format), .. } => {
                validate_strftime(&plan.name, "date-range format", format)?;
            }
            _ => {}
        }
    }
    Ok(())
}

/// Bands must be authored as a sorted, disjoint partition of the value line:
/// each band `[lo, hi)` and, in `Vec` order, band *n*'s `hi` `<=` band *n+1*'s
/// `lo`. Rejecting overlap *and* out-of-order here (rather than picking a winner
/// at colour time) is what lets the browser do a simple ordered first-match
/// scan — a single consecutive check catches both, since an out-of-order pair
/// has the earlier band's `hi` above the later band's `lo`. Open ends: a `None`
/// upper (+∞) is only valid on the last band, a `None` lower (−∞) only on the
/// first (any other position fails the consecutive check). Gaps between bands
/// are allowed and render grey — a deliberate gap, not a bug.
fn validate_bands(plan: &str, bands: &[Band]) -> anyhow::Result<()> {
    // A single band must be non-empty: `[lo, hi)` with `lo >= hi` covers
    // nothing (a copy-paste or swapped-bounds mistake).
    for band in bands {
        if let (Some(lo), Some(hi)) = (band.lo, band.hi) {
            if lo >= hi {
                anyhow::bail!(
                    "colour plan '{}' has an empty/reversed band [{}, {}) — lo must be < hi",
                    plan, lo, hi
                );
            }
        }
    }
    for pair in bands.windows(2) {
        let (a, b) = (&pair[0], &pair[1]);
        // Disjoint + sorted iff a.hi <= b.lo. `None` on a.hi (+∞ but not last)
        // or b.lo (−∞ but not first) is an overlap/out-of-order by definition.
        let disjoint = matches!((a.hi, b.lo), (Some(hi), Some(lo)) if hi <= lo);
        if !disjoint {
            anyhow::bail!(
                "colour plan '{}' has overlapping or out-of-order bands: [{:?}, {:?}) then [{:?}, {:?}) \
                 — each band's hi must be <= the next band's lo, sorted ascending",
                plan, a.lo, a.hi, b.lo, b.hi
            );
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::settings::{CompareMode, CompareOp};

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

    // ---------- colour plans ----------

    /// A property-compare/bands plan with the given bands, `active` as stated.
    fn bands_plan(name: &str, active: bool, bands: Vec<Band>) -> ColourPlan {
        ColourPlan {
            name: name.to_string(),
            active,
            mode: ColourMode::PropertyCompare {
                property_a: "A".to_string(),
                property_b: "B".to_string(),
                op: CompareOp::Diff,
                colouring: Colouring::Bands { bands },
            },
        }
    }

    fn band(lo: Option<f64>, hi: Option<f64>) -> Band {
        Band { lo, hi, colour: "#000000".to_string() }
    }

    /// At most one plan may be `active`; two is a loud error naming both.
    #[test]
    fn test_validate_colour_plans_rejects_multiple_active() {
        let plans = vec![bands_plan("A", true, vec![]), bands_plan("B", true, vec![])];
        let msg = format!("{:#}", validate_colour_plans(&plans).unwrap_err());
        assert!(msg.contains("active"), "message names the problem: {msg}");

        // Exactly one active is fine.
        assert!(validate_colour_plans(&[bands_plan("A", true, vec![]), bands_plan("B", false, vec![])]).is_ok());
    }

    /// A sorted, disjoint set of bands (including open ends and a deliberate
    /// gap) passes; overlapping, out-of-order, and reversed bands each fail.
    #[test]
    fn test_validate_colour_plans_band_partition() {
        // Open-low, a gap (5..10 uncovered), open-high — all valid.
        let ok = bands_plan("ok", false, vec![
            band(None, Some(0.0)),
            band(Some(0.0), Some(5.0)),
            band(Some(10.0), None),
        ]);
        assert!(validate_colour_plans(&[ok]).is_ok());

        // Overlap: [0,10) then [5,15).
        let overlap = bands_plan("ov", false, vec![band(Some(0.0), Some(10.0)), band(Some(5.0), Some(15.0))]);
        let msg = format!("{:#}", validate_colour_plans(&[overlap]).unwrap_err());
        assert!(msg.contains("overlapping or out-of-order") && msg.contains("'ov'"), "{msg}");

        // Out-of-order: [10,20) then [0,5).
        let unsorted = bands_plan("us", false, vec![band(Some(10.0), Some(20.0)), band(Some(0.0), Some(5.0))]);
        assert!(validate_colour_plans(&[unsorted]).is_err());

        // Reversed single band: [10, 0).
        let reversed = bands_plan("rev", false, vec![band(Some(10.0), Some(0.0))]);
        let msg = format!("{:#}", validate_colour_plans(&[reversed]).unwrap_err());
        assert!(msg.contains("reversed") || msg.contains("lo must be < hi"), "{msg}");

        // Open-high band not last → invalid (its +∞ upper overlaps the next).
        let open_high_mid = bands_plan("ohm", false, vec![band(Some(0.0), None), band(Some(10.0), Some(20.0))]);
        assert!(validate_colour_plans(&[open_high_mid]).is_err());
    }

    /// A date-range `format`, when given, must be a valid strftime pattern —
    /// same dry-run as `drofus_fields`. Absent format is fine (native parsing).
    #[test]
    fn test_validate_colour_plans_daterange_format() {
        let plan = |format: Option<&str>| ColourPlan {
            name: "dates".to_string(),
            active: false,
            mode: ColourMode::DateRange {
                property: "LastSync".to_string(),
                near_date: "2026-06-30".to_string(),
                scheme: "RdYlGn".to_string(),
                format: format.map(|s| s.to_string()),
            },
        };
        assert!(validate_colour_plans(&[plan(Some("%Y-%m-%d"))]).is_ok());
        assert!(validate_colour_plans(&[plan(None)]).is_ok(), "no format = native parsing, fine");
        let msg = format!("{:#}", validate_colour_plans(&[plan(Some("%Q-%d"))]).unwrap_err());
        assert!(msg.contains("date-range format") && msg.contains("'dates'"), "{msg}");
    }
}
