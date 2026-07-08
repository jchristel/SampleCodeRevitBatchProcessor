//! Transport-agnostic domain layer: the derive/assemble logic that used to
//! live inside the `/rooms` and validation handlers.
//!
//! Domain logic never imports a transport crate -- no `axum`, no `rmcp`, no
//! `StatusCode` in here. `ServiceError` is the seam: each transport (today's
//! Axum `handlers`, a future MCP server) maps it to its own convention. That
//! mapping is deliberately kept *out* of this module -- it belongs in the
//! adapter, not the domain. See HANDOVER-service-layer.md.

pub mod projects;
pub mod rooms;
pub mod validation;

/// Domain-level failure, independent of how a caller reports it.
#[derive(Debug)]
pub enum ServiceError {
    /// A referenced id (e.g. an unknown project) doesn't exist.
    NotFound(String),
    /// The caller's input was malformed.
    BadInput(String),
    /// An unexpected internal failure (e.g. a storage read error).
    Internal(anyhow::Error),
}

impl std::fmt::Display for ServiceError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ServiceError::NotFound(msg) => write!(f, "not found: {msg}"),
            ServiceError::BadInput(msg) => write!(f, "bad input: {msg}"),
            ServiceError::Internal(e) => write!(f, "internal error: {e}"),
        }
    }
}

impl std::error::Error for ServiceError {}
