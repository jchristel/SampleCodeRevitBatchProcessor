use std::{
    collections::BTreeMap,
    path::PathBuf,
    sync::{Arc, Mutex},
};

use anyhow::Context;
use axum::{
    extract::State,
    http::StatusCode,
    routing::post,
    Json, Router,
};
use clap::Parser;
use serde::{Deserialize, Serialize};
use tower_http::{cors::CorsLayer, services::ServeDir, trace::TraceLayer};

// ---------- Settings ----------

/// Top-level server settings, parsed once at startup from a TOML file.
#[derive(Debug, Deserialize)]
struct Settings {
    pub sources: Sources,

    /// Dev-only: when present, seeds the server with a snapshot from disk at
    /// startup so no manual POST is needed. Omit in prod.
    #[serde(default)]
    pub test_data: Option<TestData>,

    /// Ordered classification tiers, outermost first. Empty if the section is
    /// omitted (a project with no classification defined).
    #[serde(default)]
    pub hierarchy: Vec<HierarchyTier>,
}

/// External data sources joined onto the Revit snapshot.
#[derive(Debug, Deserialize)]
struct Sources {
    pub drofus: DrofusSource,
}

/// dRofus source. `#[serde(tag = "type")]` lets the TOML `type` field pick the
/// variant — adding an `Api` variant later is a loader-only change; all
/// consumers of `AppState` stay untouched.
#[derive(Debug, Deserialize)]
#[serde(tag = "type", rename_all = "lowercase")]
enum DrofusSource {
    /// Current: load from a local file.
    File { path: PathBuf },
    // Future: Api { url: String, api_key: String },
}

/// Dev-only seed data. Kept separate from `drofus` so removing this test seam
/// later is a one-section deletion with no other changes.
#[derive(Debug, Deserialize)]
struct TestData {
    /// Path to a pre-exported snapshot (same JSON shape a POST sends).
    pub snapshot_path: PathBuf,
}

/// One tier of the classification hierarchy. A tier is keyed by a code and/or a
/// name property — at least one must be present (validated at startup), since a
/// tier naming neither is unkeyable.
#[derive(Debug, Clone, Deserialize)]
struct HierarchyTier {
    /// Human label for the tier ("Building", "Department").
    name: String,
    /// Room property holding this tier's code. Optional per-tier.
    #[serde(default)]
    code_property: Option<String>,
    /// Room property holding this tier's display name. Optional per-tier.
    #[serde(default)]
    name_property: Option<String>,
}

impl HierarchyTier {
    /// A tier must name at least one property or it can't be keyed. Validated
    /// at startup so a misconfigured tier is a loud error, not a silent
    /// "undefined" for every room.
    fn validate(&self) -> anyhow::Result<()> {
        if self.code_property.is_none() && self.name_property.is_none() {
            anyhow::bail!(
                "hierarchy tier '{}' names neither code_property nor name_property",
                self.name
            );
        }
        Ok(())
    }
}

// ---------- CLI ----------

#[derive(Parser)]
struct Args {
    /// Path to the TOML settings file.
    #[arg(long)]
    settings: PathBuf,
}

fn load_settings(path: &PathBuf) -> anyhow::Result<Settings> {
    let raw = std::fs::read_to_string(path)
        .with_context(|| format!("could not read settings file: {}", path.display()))?;
    let settings: Settings = toml::from_str(&raw).context("failed to parse settings TOML")?;
    // Fail fast on unkeyable tiers — better a startup error than a silent
    // classification that groups every room under "undefined".
    for tier in &settings.hierarchy {
        tier.validate()?;
    }
    Ok(settings)
}

// ---------- JSON contract (must match the Revit extractor's serializer) ----------

/// A 2D point in Revit model space. Units are decimal feet, Y points UP.
#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
struct Point2D {
    x: f64,
    y: f64,
}

/// A single closed loop of points. A room has one outer loop and zero or more
/// inner loops (holes, e.g. a column or shaft punched through the room).
#[derive(Debug, Clone, Serialize, Deserialize)]
struct Loop {
    points: Vec<Point2D>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct Level {
    id: String,
    name: String,
    elevation: f64,
}

/// Everything known about a room's properties, split into two tiers.
/// ALWAYS present on a Room (never Option): the block is guaranteed, even when
/// `custom` is empty. Consumers read it without a presence check.
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
struct RoomProperties {
    /// Revit built-ins — guaranteed to exist because Revit builds them in.
    /// Typed struct: the extractor can rely on these, so they get real fields.
    #[serde(default)]
    builtin: BuiltinProperties,

    /// Project-varying params (shared/project params). Shape is unknown at
    /// compile time, so an open bag. `#[serde(default)]` → an older/sparse
    /// payload deserializes to empty rather than failing.
    #[serde(default)]
    custom: BTreeMap<String, CustomValue>,
}

/// Sentinel used as the default for ElementId fields. Revit's
/// ElementId.InvalidElementId has Value == -1; serde's default for i64 is 0,
/// which would silently alias a real element, so we override it.
fn default_invalid_id() -> i64 {
    -1
}

/// Built-in Revit room properties — the fixed set that Revit guarantees on
/// every Room element. All fields are `#[serde(default)]` so a sparse payload
/// (e.g. a room with no area yet placed) deserialises without error.
///
/// Serde rename matches `p.Definition.Name` from the Python extractor so the
/// JSON keys are the Revit parameter display names ("Area", "Number", etc.).
///
/// NOTE: `id` / `name` / `level_id` stay on `Room` itself (the viewer already
/// reads them there). `Name` is included here too because it travels with the
/// rest of the built-ins in the extractor and consumers may want it without
/// unpacking the Room wrapper.
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
struct BuiltinProperties {
    // ---- Identity / labelling ----
    /// Room number as Revit reports it (distinct from the display name).
    #[serde(default, rename = "Number")]
    number: String,
    /// Room display name (mirrors Room.name; included for completeness).
    #[serde(default, rename = "Name")]
    name: String,
    /// Free-text department label.
    #[serde(default, rename = "Department")]
    department: String,
    /// Occupancy classification string.
    #[serde(default, rename = "Occupancy")]
    occupancy: String,
    /// Free-text comments field.
    #[serde(default, rename = "Comments")]
    comments: String,

    // ---- Measurements (metric, converted by the Python extractor) ----
    /// Placed area (m²).
    #[serde(default, rename = "Area")]
    area: f64,
    /// Room perimeter (mm).
    #[serde(default, rename = "Perimeter")]
    perimeter: f64,
    /// Room volume (m³).
    #[serde(default, rename = "Volume")]
    volume: f64,
    /// Offset of the room's base from its host level (mm).
    #[serde(default, rename = "Base Offset")]
    base_offset: f64,
    /// Offset of the room's top from the Upper Limit level (mm).
    /// Paired with `upper_limit`; together they define the vertical extent.
    #[serde(default, rename = "Limit Offset")]
    limit_offset: f64,
    /// Height when the room is set to Unbounded (mm).
    #[serde(default, rename = "Unbounded Height")]
    unbounded_height: f64,
    /// Height at which the room boundary is computed (mm).
    #[serde(default, rename = "Computation Height")]
    computation_height: f64,

    // ---- Finish schedules ----
    #[serde(default, rename = "Floor Finish")]
    floor_finish: String,
    #[serde(default, rename = "Ceiling Finish")]
    ceiling_finish: String,
    #[serde(default, rename = "Wall Finish")]
    wall_finish: String,
    #[serde(default, rename = "Base Finish")]
    base_finish: String,

    // ---- Level references (ElementId as i64; -1 = not set) ----
    /// ElementId of the phase in which this room exists.
    #[serde(default = "default_invalid_id", rename = "Phase")]
    phase: i64,
    /// ElementId of the level used as the upper bounding reference.
    /// `limit_offset` is the vertical distance above this level.
    #[serde(default = "default_invalid_id", rename = "Upper Limit")]
    upper_limit: i64,

    // ---- IFC export ----
    #[serde(default, rename = "IFC Predefined Type")]
    ifc_predefined_type: String,
    #[serde(default, rename = "IfcGUID")]
    ifc_guid: String,
    #[serde(default, rename = "Export to IFC As")]
    export_to_ifc_as: String,
    #[serde(default, rename = "Export to IFC")]
    export_to_ifc: String,
}

/// One custom property: the raw string value plus an optional storage-type
/// hint from Revit. Paired in one struct (not two parallel maps) so value and
/// type can't drift and an absent type degrades to "treat as string".
#[derive(Debug, Clone, Serialize, Deserialize)]
struct CustomValue {
    /// Raw value, always a string. Revit hands most params back as strings;
    /// any typing is deferred and done server-side, lazily.
    value: String,

    /// Revit's declared StorageType, forwarded as guidance only:
    /// "String" | "Integer" | "Double" | "ElementId". Optional — absent means
    /// "treat as string". This is a HINT: declared type and parseable content
    /// can disagree (a String param holding "12.5", an empty Double), so any
    /// coercion keyed off it must fall back to `value` on failure.
    ///
    /// Set by the Python extractor's DataProperty.storage_type field
    /// (str(p.StorageType) on the Revit parameter).
    #[serde(default)]
    storage_type: Option<String>,
}

impl CustomValue {
    /// Best-effort typed read guided by the storage-type hint, falling back to
    /// the raw string's natural parse, and never panicking. Returns None only
    /// when nothing sensible can be produced. Callers that just want the string
    /// read `.value` directly and ignore this.
    fn as_f64(&self) -> Option<f64> {
        // Hint steers intent, but content wins: try to parse regardless, since
        // the declared type can lie (e.g. a String param holding "12.5").
        self.value.trim().parse::<f64>().ok()
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct Room {
    id: String,
    name: String,
    level_id: String,
    loops: Vec<Loop>,

    /// Always present (see RoomProperties). `#[serde(default)]` lets a v2-shaped
    /// payload (no properties block) still deserialize to an empty block —
    /// though the SUPPORTED_SCHEMA check hard-rejects v2 before it reaches the
    /// snapshot store. The default is a serde belt-and-braces, not an acceptance
    /// window.
    #[serde(default)]
    properties: RoomProperties,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct RoomPayload {
    schema_version: u32,
    levels: Vec<Level>,
    rooms: Vec<Room>,
}

/// Schema version this server accepts. Hard-require v3: a v2 producer missing
/// the properties block will 422 loud rather than silently landing empty
/// properties. No transition window — update the extractor and the server
/// together.
const SUPPORTED_SCHEMA: u32 = 3;

// ---------- dRofus ----------

/// One dRofus row, resolved. `fields` is dRofus-field-label → value (row 1
/// labels as keys). Kept as strings — same raw discipline as custom props.
#[derive(Debug, Clone, Serialize)]
struct DrofusRecord {
    fields: BTreeMap<String, String>,
}

/// The whole dRofus dataset, resolved once at startup.
struct DrofusData {
    /// Which room property holds the linking id (CSV row 2, col 0).
    /// Read the room property of THIS name to get its dRofus key.
    link_property: String,

    /// dRofus id → record. Direct value match; ids are unique, so a plain map.
    by_id: BTreeMap<String, DrofusRecord>,
}

/// Read the two-header-row CSV into DrofusData. Fail fast (startup) on a
/// malformed file — same contract as load_settings.
///
/// CSV shape:
///   row 1: dRofus field labels  (DrofusRoomId, NetArea, Department, …)
///   row 2: Revit param names    (RevitDrofusKey, d_net_area, d_dept, …)
///   row 3+: data rows
/// Row 2, col 0 = the Revit room property whose value is the dRofus id (link).
fn load_drofus(source: &DrofusSource) -> anyhow::Result<DrofusData> {
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

// ---------- Classification ----------

/// One tier's resolved value for a room. `undefined` is a REPRESENTED value,
/// not an absence — every room gets one of these per tier, so the grouping tree
/// is uniform-depth and a viewer can render "undefined Sub-department" as its
/// own group rather than dropping the room.
#[derive(Debug, Clone, Serialize)]
struct TierValue {
    tier: String,
    /// None when this tier (or a tier above it) had no data — i.e. undefined.
    #[serde(skip_serializing_if = "Option::is_none")]
    code: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    name: Option<String>,
    /// True once classification has fallen through to undefined at this tier.
    undefined: bool,
}

/// Look up a named property on a room by its Revit parameter display name,
/// checking built-ins first then the custom bag. Used by both the dRofus join
/// and the classifier so the lookup strategy is consistent and lives in one
/// place.
///
/// Names match `p.Definition.Name` from the Python extractor, which is also
/// what dRofus link_property and hierarchy tier configs will reference.
/// Returns `None` when the field is absent or holds its zero/empty default.
fn lookup_property(room: &Room, name: &str) -> Option<String> {
    let b = &room.properties.builtin;

    // String built-ins: return Some only when non-empty.
    let str_builtin = match name {
        "Number"             => Some(b.number.as_str()),
        "Name"               => Some(b.name.as_str()),
        "Department"         => Some(b.department.as_str()),
        "Occupancy"          => Some(b.occupancy.as_str()),
        "Comments"           => Some(b.comments.as_str()),
        "Floor Finish"       => Some(b.floor_finish.as_str()),
        "Ceiling Finish"     => Some(b.ceiling_finish.as_str()),
        "Wall Finish"        => Some(b.wall_finish.as_str()),
        "Base Finish"        => Some(b.base_finish.as_str()),
        "IFC Predefined Type"=> Some(b.ifc_predefined_type.as_str()),
        "IfcGUID"            => Some(b.ifc_guid.as_str()),
        "Export to IFC As"   => Some(b.export_to_ifc_as.as_str()),
        "Export to IFC"      => Some(b.export_to_ifc.as_str()),
        _                    => None,
    };
    if let Some(s) = str_builtin {
        return if s.is_empty() { None } else { Some(s.to_string()) };
    }

    // Numeric built-ins: convert to string; treat zero as absent since that is
    // the serde default when the extractor omits the field.
    let f64_builtin = match name {
        "Area"               => Some(b.area),
        "Perimeter"          => Some(b.perimeter),
        "Volume"             => Some(b.volume),
        "Base Offset"        => Some(b.base_offset),
        "Limit Offset"       => Some(b.limit_offset),
        "Unbounded Height"   => Some(b.unbounded_height),
        "Computation Height" => Some(b.computation_height),
        _                    => None,
    };
    if let Some(v) = f64_builtin {
        return if v == 0.0 { None } else { Some(v.to_string()) };
    }

    // ElementId built-ins: -1 means not set (Revit InvalidElementId).
    let id_builtin = match name {
        "Phase"       => Some(b.phase),
        "Upper Limit" => Some(b.upper_limit),
        _             => None,
    };
    if let Some(id) = id_builtin {
        return if id == -1 { None } else { Some(id.to_string()) };
    }

    // Fall through to the custom bag for project/shared params.
    room.properties
        .custom
        .get(name)
        .map(|v| v.value.clone())
        .filter(|s| !s.is_empty())
}

/// Resolve one room to a full-depth classification path.
///
/// RULE: once a tier has no data, that tier AND every tier below it are
/// `undefined`. A room missing tier 1 is undefined all the way down —
/// still visualizable as a distinct group.
///
/// NOTE: resolved fresh per `/rooms` request, not cached. The result is a
/// function of (static hierarchy + current snapshot); caching it would require
/// recomputation on every new snapshot push or dRofus re-poll. At this scale
/// the per-request cost is negligible — prefer correctness over a premature
/// optimisation.
fn classify_room(room: &Room, tiers: &[HierarchyTier]) -> Vec<TierValue> {
    let mut path = Vec::with_capacity(tiers.len());
    let mut fell_through = false;

    for tier in tiers {
        let code = tier
            .code_property
            .as_deref()
            .and_then(|p| lookup_property(room, p));
        let name = tier
            .name_property
            .as_deref()
            .and_then(|p| lookup_property(room, p));

        let has_data = code.is_some() || name.is_some();

        if fell_through || !has_data {
            fell_through = true; // once undefined, stay undefined downward
            path.push(TierValue {
                tier: tier.name.clone(),
                code: None,
                name: None,
                undefined: true,
            });
        } else {
            path.push(TierValue {
                tier: tier.name.clone(),
                code,
                name,
                undefined: false,
            });
        }
    }
    path
}

// ---------- Shared state ----------

/// In-memory store of the last payload received. Mutex is fine: this is a
/// single-user local tool, not a high-concurrency service.
struct AppState {
    latest: Mutex<Option<RoomPayload>>,

    /// Resolved dRofus data, loaded once at startup. Joined onto rooms at
    /// response assembly — the stored snapshot is never mutated by the join.
    drofus: Option<DrofusData>,

    /// Classification tiers loaded from settings. Resolved per-room inside
    /// `/rooms` assembly; not cached (see classify_room).
    hierarchy: Vec<HierarchyTier>,
}

impl AppState {
    fn new(drofus: DrofusData, hierarchy: Vec<HierarchyTier>) -> Self {
        Self {
            latest: Mutex::new(None),
            drofus: Some(drofus),
            hierarchy,
        }
    }

    /// Shared setter used by both the push handler and the startup seed so the
    /// two paths can never drift to different representations.
    fn set_snapshot(&self, payload: RoomPayload) {
        *self.latest.lock().unwrap() = Some(payload);
    }
}

type Shared = Arc<AppState>;

// ---------- Startup helpers ----------

fn seed_if_test(state: &AppState, test_data: Option<&TestData>) -> anyhow::Result<()> {
    if let Some(test) = test_data {
        let raw = std::fs::read_to_string(&test.snapshot_path).with_context(|| {
            format!(
                "could not read test snapshot: {}",
                test.snapshot_path.display()
            )
        })?;
        // Parse into the same type the push handler accepts — seed and push
        // converge on one representation and can never drift.
        let snapshot: RoomPayload =
            serde_json::from_str(&raw).context("failed to parse test snapshot JSON")?;
        state.set_snapshot(snapshot);
        tracing::info!("seeded snapshot from {}", test.snapshot_path.display());
    }
    Ok(())
}

// ---------- Handlers ----------

/// Revit posts room data here. Returns 200 with a short summary, or 422 if the
/// schema version is one this server doesn't understand.
async fn ingest_rooms(
    State(state): State<Shared>,
    Json(payload): Json<RoomPayload>,
) -> Result<Json<IngestResponse>, (StatusCode, String)> {
    if payload.schema_version != SUPPORTED_SCHEMA {
        return Err((
            StatusCode::UNPROCESSABLE_ENTITY,
            format!(
                "schema_version {} not supported; this server speaks {}",
                payload.schema_version, SUPPORTED_SCHEMA
            ),
        ));
    }

    let count = payload.rooms.len();
    tracing::info!("received {} room(s)", count);

    state.set_snapshot(payload);

    Ok(Json(IngestResponse {
        accepted: true,
        room_count: count,
    }))
}

#[derive(Serialize)]
struct IngestResponse {
    accepted: bool,
    room_count: usize,
}

/// A room as sent to the viewer: the stored room plus any attached dRofus data
/// and its resolved classification path. Separate response type so the join
/// never mutates the stored snapshot, and so dRofus stays a distinct sub-object
/// (its own lifecycle — it will later refresh on its own trigger, so it must
/// not be fused into the room's own properties).
#[derive(Serialize)]
struct RoomResponse {
    #[serde(flatten)]
    room: Room,

    /// Present only when the room's link value matched a dRofus record.
    /// Absent (skipped) otherwise — an unmatched key is a signal, not an error.
    #[serde(skip_serializing_if = "Option::is_none")]
    drofus: Option<DrofusRecord>,

    /// Full-depth classification path. Empty when no hierarchy is configured.
    classification: Vec<TierValue>,
}

/// The viewer fetches the most recent payload here. Returns 204 if nothing has
/// been posted yet, so the front-end can show an empty state.
/// dRofus join and classification are resolved here at response assembly —
/// the stored snapshot stays raw; derived data is never written back to state.
async fn get_rooms(State(state): State<Shared>) -> Result<Json<serde_json::Value>, StatusCode> {
    let payload = match state.latest.lock().unwrap().clone() {
        Some(p) => p,
        None => return Err(StatusCode::NO_CONTENT),
    };

    let rooms: Vec<RoomResponse> = payload
        .rooms
        .iter()
        .map(|room| {
            // dRofus join: read the link property off the room, look up the record.
            let drofus = state.drofus.as_ref().and_then(|d| {
                lookup_property(room, &d.link_property)
                    .and_then(|key| d.by_id.get(&key).cloned())
            });

            // Classification resolved fresh — see staleness note on classify_room.
            let classification = classify_room(room, &state.hierarchy);

            RoomResponse { room: room.clone(), drofus, classification }
        })
        .collect();

    // Re-emit levels + rooms; keep schema_version so the viewer's check holds.
    Ok(Json(serde_json::json!({
        "schema_version": payload.schema_version,
        "levels": payload.levels,
        "rooms": rooms,
    })))
}

// ---------- Wiring ----------

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::fmt()
        .with_env_filter("revit_viewer=info,tower_http=info")
        .init();

    let args = Args::parse();
    let settings = load_settings(&args.settings)
        .with_context(|| format!("bad settings file: {}", args.settings.display()))?;

    tracing::info!("settings loaded from {}", args.settings.display());

    let Settings { sources, test_data, hierarchy } = settings;
    let drofus = load_drofus(&sources.drofus)?;
    let state: Shared = Arc::new(AppState::new(drofus, hierarchy));

    seed_if_test(&state, test_data.as_ref())?;

    let app = Router::new()
        .route("/rooms", post(ingest_rooms).get(get_rooms))
        // Serves the viewer page at "/" from ./static.
        .fallback_service(ServeDir::new("static"))
        // Lets the browser viewer call /rooms even if served from elsewhere.
        .layer(CorsLayer::permissive())
        .layer(TraceLayer::new_for_http())
        .with_state(state);

    let addr = "127.0.0.1:5151";
    let listener = tokio::net::TcpListener::bind(addr).await?;
    tracing::info!("viewer on http://{addr}  (POST room JSON to http://{addr}/rooms)");
    axum::serve(listener, app).await?;

    Ok(())
}

// ---------- Tests ----------

#[cfg(test)]
mod tests {
    use super::*;

    // Helpers ----------------------------------------------------------------

    fn make_room(id: &str, custom: BTreeMap<&str, (&str, Option<&str>)>) -> Room {
        Room {
            id: id.to_string(),
            name: "Test Room".to_string(),
            level_id: "1".to_string(),
            loops: vec![],
            properties: RoomProperties {
                builtin: BuiltinProperties::default(),
                custom: custom
                    .into_iter()
                    .map(|(k, (val, st))| {
                        (
                            k.to_string(),
                            CustomValue {
                                value: val.to_string(),
                                storage_type: st.map(|s| s.to_string()),
                            },
                        )
                    })
                    .collect(),
            },
        }
    }

    fn make_tier(name: &str, code_prop: Option<&str>, name_prop: Option<&str>) -> HierarchyTier {
        HierarchyTier {
            name: name.to_string(),
            code_property: code_prop.map(|s| s.to_string()),
            name_property: name_prop.map(|s| s.to_string()),
        }
    }

    // Step 1: serde round-trips ----------------------------------------------

    /// A v3 payload with a room carrying builtin + two custom entries
    /// survives a serde round-trip intact.
    #[test]
    fn test_v3_room_properties_round_trip() {
        let json = serde_json::json!({
            "schema_version": 3,
            "levels": [{ "id": "lvl1", "name": "Level 1", "elevation": 0.0 }],
            "rooms": [{
                "id": "r1",
                "name": "Office",
                "level_id": "lvl1",
                "loops": [],
                "properties": {
                    "builtin": { "Number": "101", "Area": 25.5 },
                    "custom": {
                        "Dept": { "value": "Finance", "storage_type": "String" },
                        "CostCode": { "value": "42", "storage_type": "Integer" }
                    }
                }
            }]
        });

        let payload: RoomPayload = serde_json::from_value(json).unwrap();
        let room = &payload.rooms[0];

        assert_eq!(room.properties.builtin.number, "101");
        assert_eq!(room.properties.builtin.area, 25.5);
        assert_eq!(room.properties.custom["Dept"].value, "Finance");
        assert_eq!(
            room.properties.custom["Dept"].storage_type,
            Some("String".to_string())
        );
        assert_eq!(room.properties.custom["CostCode"].value, "42");

        // Confirm round-trip: serialise and re-parse.
        let serialised = serde_json::to_string(&payload).unwrap();
        let reparsed: RoomPayload = serde_json::from_str(&serialised).unwrap();
        assert_eq!(reparsed.rooms[0].properties.builtin.number, "101");
    }

    /// A v2-shaped room JSON (no properties block) deserialises to an empty
    /// block — proves the `#[serde(default)]` wiring is correct.
    #[test]
    fn test_v2_room_deserialises_to_empty_properties() {
        let json = serde_json::json!({
            "id": "r1",
            "name": "Office",
            "level_id": "lvl1",
            "loops": []
            // no "properties" key
        });

        let room: Room = serde_json::from_value(json).unwrap();
        assert!(room.properties.custom.is_empty());
        assert_eq!(room.properties.builtin.number, "");
        assert_eq!(room.properties.builtin.area, 0.0);
    }

    /// CustomValue::as_f64 parses a numeric string regardless of storage_type.
    #[test]
    fn test_custom_value_as_f64() {
        let cv = |val: &str, st: Option<&str>| CustomValue {
            value: val.to_string(),
            storage_type: st.map(|s| s.to_string()),
        };

        assert_eq!(cv("3.14", Some("Double")).as_f64(), Some(3.14));
        assert_eq!(cv("42", Some("Integer")).as_f64(), Some(42.0));
        // Content wins over hint: a String param holding a number still parses.
        assert_eq!(cv("7.5", Some("String")).as_f64(), Some(7.5));
        // Truly non-numeric returns None.
        assert_eq!(cv("Finance", Some("String")).as_f64(), None);
    }

    // Step 3: classification -------------------------------------------------

    /// A fully-classified room produces a full path with no undefined tiers.
    #[test]
    fn test_classify_room_fully_classified() {
        let room = make_room(
            "r1",
            BTreeMap::from([
                ("bldg_code", ("B01", None)),
                ("dept_code", ("D02", None)),
            ]),
        );
        let tiers = vec![
            make_tier("Building", Some("bldg_code"), None),
            make_tier("Department", Some("dept_code"), None),
        ];

        let path = classify_room(&room, &tiers);

        assert_eq!(path.len(), 2);
        assert_eq!(path[0].code.as_deref(), Some("B01"));
        assert!(!path[0].undefined);
        assert_eq!(path[1].code.as_deref(), Some("D02"));
        assert!(!path[1].undefined);
    }

    /// A room missing the sub-department property: Building + Department
    /// resolve, Sub-department and everything below become undefined.
    #[test]
    fn test_classify_room_partial_undefined() {
        let room = make_room(
            "r1",
            BTreeMap::from([
                ("bldg_code", ("B01", None)),
                ("dept_code", ("D02", None)),
                // sub_dept_code absent
            ]),
        );
        let tiers = vec![
            make_tier("Building", Some("bldg_code"), None),
            make_tier("Department", Some("dept_code"), None),
            make_tier("SubDept", Some("sub_dept_code"), None),
        ];

        let path = classify_room(&room, &tiers);

        assert!(!path[0].undefined);
        assert!(!path[1].undefined);
        assert!(path[2].undefined);
    }

    /// A room missing tier 1 is undefined all the way down.
    #[test]
    fn test_classify_room_all_undefined() {
        let room = make_room("r1", BTreeMap::new()); // no custom props
        let tiers = vec![
            make_tier("Building", Some("bldg_code"), None),
            make_tier("Department", Some("dept_code"), None),
        ];

        let path = classify_room(&room, &tiers);

        assert!(path.iter().all(|t| t.undefined));
    }

    /// A HierarchyTier with neither property fails validation.
    #[test]
    fn test_unkeyable_tier_fails_validation() {
        let tier = HierarchyTier {
            name: "Ghost".to_string(),
            code_property: None,
            name_property: None,
        };
        assert!(tier.validate().is_err());
    }
}
