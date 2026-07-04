//! dRofus reference data: loaded once at startup, joined onto rooms at response
//! assembly — never merged into the stored snapshot.
//!
//! Two disciplines from STRATEGY.md live here. *Store raw, join late:* the
//! parsed map sits in `AppState` and is attached at `/rooms` assembly, so the
//! Revit snapshot stays untouched and the join is reversible. *Separate
//! sub-object because separate lifecycle:* dRofus will later refresh on its own
//! trigger (a mid-session poll), independent of the Revit push, so it must not
//! be fused into the room's own properties — keeping it separate keeps the seam
//! where the refresh boundary actually is.
//!
//! The file loader is the degenerate (fetch-once-at-boot) case of that pollable
//! source; when the real API connector lands it slots in as a new `DrofusSource`
//! variant, this loader its only new surface.

use std::collections::BTreeMap;

use anyhow::Context;
use serde::Serialize;

use crate::settings::DrofusSource;

/// One dRofus row, resolved. `fields` is dRofus-field-label → value (row 1
/// labels as keys). Kept as strings — same raw discipline as custom props.
#[derive(Debug, Clone, Serialize)]
pub struct DrofusRecord {
    pub fields: BTreeMap<String, String>,
}

/// The whole dRofus dataset, resolved once at startup.
pub struct DrofusData {
    /// Which room property holds the linking id (CSV row 2, col 0).
    /// Read the room property of THIS name to get its dRofus key.
    pub link_property: String,

    /// dRofus id → record. Direct value match; ids are unique, so a plain map.
    pub by_id: BTreeMap<String, DrofusRecord>,
}

/// Read the two-header-row CSV into DrofusData. Fail fast (startup) on a
/// malformed file — same contract as load_settings.
///
/// CSV shape:
///   row 1: dRofus field labels  (DrofusRoomId, NetArea, Department, …)
///   row 2: Revit param names    (RevitDrofusKey, d_net_area, d_dept, …)
///   row 3+: data rows
/// Row 2, col 0 = the Revit room property whose value is the dRofus id (link).
pub fn load_drofus(source: &DrofusSource) -> anyhow::Result<DrofusData> {
    let DrofusSource::File { path } = source; // only variant today
    let mut rdr = csv::ReaderBuilder::new()
        .has_headers(false) // both header rows are data to us; we parse them by hand
        .from_path(path)
        .with_context(|| format!("could not open dRofus CSV: {}", path.display()))?;

    let mut records = rdr.records();

    // Row 1: dRofus field labels.
    let labels = records
        .next()
        .context("dRofus CSV missing row 1 (field labels)")??;
    // Row 2: Revit param names. Col 0 is the link property name.
    let revit_names = records
        .next()
        .context("dRofus CSV missing row 2 (Revit param names)")??;

    let link_property = revit_names
        .get(0)
        .context("dRofus CSV row 2 col 0 (link property) is empty")?
        .to_string();

    // Data rows: col 0 is the dRofus id (the key), cols 1+ are values keyed by
    // the row-1 label at the same column index.
    let mut by_id = BTreeMap::new();
    for row in records {
        let row = row?;
        let id = match row.get(0) {
            Some(id) if !id.is_empty() => id.to_string(),
            _ => continue, // skip blank-key rows rather than fail the whole load
        };
        let mut fields = BTreeMap::new();
        for col in 1..labels.len() {
            if let (Some(label), Some(val)) = (labels.get(col), row.get(col)) {
                fields.insert(label.to_string(), val.to_string());
            }
        }
        by_id.insert(id, DrofusRecord { fields });
    }

    tracing::info!(
        "loaded {} dRofus record(s); link property = {}",
        by_id.len(),
        link_property
    );
    Ok(DrofusData { link_property, by_id })
}
