//! Transport-agnostic domain layer: the derive/assemble logic that used to
//! live inside the `/rooms` and validation handlers.
//!
//! Domain logic never imports a transport crate -- no `axum`, no `rmcp`, no
//! `StatusCode` in here. `ServiceError` is the seam: each transport (the Axum
//! `handlers`, the MCP server in `src/bin/mcp.rs`) maps it to its own
//! convention. That mapping is deliberately kept *out* of this module -- it
//! belongs in the adapter, not the domain. See HANDOVER-service-layer.md.

pub mod areas;
pub mod comparison;
pub mod drofus;
pub mod milestones;
pub mod projects;
pub mod rooms;
pub mod snapshots;
pub mod validation;

/// Domain-level failure, independent of how a caller reports it.
///
/// A single variant today, deliberately: every current failure path is an
/// unexpected internal error (a storage read). Caller-fault variants
/// (not-found, bad-input) used to exist here but no service function ever
/// produced them — the read endpoints answer an unknown project with a soft
/// "not configured" success by design (see `list_buildings` /
/// `compute_project_validation`), not an error. A new variant joins together
/// with its first producer, not ahead of it.
#[derive(Debug)]
pub enum ServiceError {
    /// An unexpected internal failure (e.g. a storage read error).
    Internal(anyhow::Error),
}

impl std::fmt::Display for ServiceError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ServiceError::Internal(e) => write!(f, "internal error: {e}"),
        }
    }
}

impl std::error::Error for ServiceError {}
