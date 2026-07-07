# Handover: streaming `/rooms` ingest (NDJSON)

## Why

>100 MB FFE exports can't be buffered whole. `Json<RoomPayload>` reads the
entire body into memory before deserializing — that's the ceiling. The fix:
stream the body room-by-room so peak memory is ~one room, not the whole file.

Combine with gzip: sender gzips the NDJSON stream, `RequestDecompressionLayer`
inflates it, we parse the inflated stream line-by-line.

## Wire format: NDJSON

One JSON object per line. First line = envelope (project/model/snapshot/levels,
**no rooms**). Every subsequent line = one `Room`.

```
{"schema_version":5,"project":{...},"model":{...},"snapshot":{...},"levels":[...]}
{"id":"r1","name":"Office","level_id":"311","loops":[...],"properties":{...}}
{"id":"r2",...}
```

Sender emits this to a new endpoint `POST /rooms/stream` (keep the old buffered
`/rooms` for small pushes). Set `Content-Type: application/x-ndjson` and, if
compressing, `Content-Encoding: gzip`.

---

## New handler — fully annotated

```rust
use axum::body::Body;
use axum::extract::State;
use axum::http::StatusCode;
use futures_util::StreamExt;               // for `.next()` on the body stream
use tokio::io::AsyncBufReadExt;            // for `.lines()`
use tokio_util::io::StreamReader;          // Stream<Bytes> -> AsyncRead
use crate::contract::{Room, SUPPORTED_SCHEMA};

/// Streaming ingest for very large models. Reads the request body as a
/// line-delimited stream (NDJSON) instead of buffering it whole, so peak
/// memory is one room, not the entire (possibly >100 MB) payload.
///
/// Line 1 is the envelope (identity + levels, no rooms); each following line
/// is one Room. We accumulate rooms into a RoomPayload and hand the finished
/// payload to the existing store — storage stays a whole-snapshot operation,
/// only *parsing* is streamed.
pub async fn ingest_rooms_stream(
    State(state): State<Shared>,
    body: Body,                            // raw body, NOT Json<_> — we drive parsing ourselves
) -> Result<Json<IngestResponse>, (StatusCode, String)> {
    // 1. Turn the axum Body into an AsyncRead we can read lines from.
    //    `into_data_stream()` yields Result<Bytes, _>; StreamReader wants
    //    io::Error, so map the body error into one. If RequestDecompressionLayer
    //    is in front, this stream is already the INFLATED bytes.
    let stream = body
        .into_data_stream()
        .map(|r| r.map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, e)));
    let reader = StreamReader::new(stream);
    let mut lines = reader.lines();        // yields one line at a time, buffered internally

    // 2. First line = envelope. It carries everything about the payload EXCEPT
    //    rooms, which stream in after it.
    let envelope_line = lines
        .next_line()
        .await
        .map_err(|e| (StatusCode::BAD_REQUEST, format!("read error: {e}")))?
        .ok_or((StatusCode::BAD_REQUEST, "empty body".into()))?;

    // A minimal struct matching the envelope line. Defined inline (or beside
    // RoomPayload in contract.rs) so it deserializes without a `rooms` field.
    let envelope: StreamEnvelope = serde_json::from_str(&envelope_line)
        .map_err(|e| (StatusCode::BAD_REQUEST, format!("bad envelope: {e}")))?;

    // 3. Schema check up front, same contract as the buffered handler — reject
    //    a wrong version before reading a single room.
    if envelope.schema_version != SUPPORTED_SCHEMA {
        return Err((
            StatusCode::UNPROCESSABLE_ENTITY,
            format!(
                "schema_version {} not supported; this server speaks {}",
                envelope.schema_version, SUPPORTED_SCHEMA
            ),
        ));
    }

    // 4. Stream the rooms. Each line is one Room; parse and push. Peak memory
    //    is the growing Vec<Room> plus one line — we don't hold the raw text of
    //    the whole body at once. (If even the assembled Vec is too big to hold,
    //    the next step is a streaming store::put that writes rooms as they
    //    arrive — deferred; see note below.)
    let mut rooms: Vec<Room> = Vec::new();
    while let Some(line) = lines
        .next_line()
        .await
        .map_err(|e| (StatusCode::BAD_REQUEST, format!("read error: {e}")))?
    {
        if line.trim().is_empty() {
            continue;                      // tolerate a trailing blank line
        }
        let room: Room = serde_json::from_str(&line)
            .map_err(|e| (StatusCode::BAD_REQUEST, format!("bad room line: {e}")))?;
        rooms.push(room);
    }

    let count = rooms.len();
    tracing::info!("streamed {} room(s)", count);

    // 5. Reassemble the same RoomPayload the buffered path produces, so storage
    //    and everything downstream is byte-for-byte identical — streaming
    //    changed only how we READ, not what we store.
    let payload = RoomPayload {
        schema_version: envelope.schema_version,
        project: envelope.project,
        model: envelope.model,
        snapshot: envelope.snapshot,
        levels: envelope.levels,
        rooms,
    };

    // 6. Persist via the existing store — a storage failure is a 500, same as
    //    the buffered handler.
    state.set_snapshot(payload).map_err(|e| {
        tracing::error!("failed to store snapshot: {e:#}");
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            format!("could not store snapshot: {e}"),
        )
    })?;

    Ok(Json(IngestResponse { accepted: true, room_count: count }))
}
```

### Envelope struct (add to `contract.rs`)

```rust
/// The first NDJSON line of a streamed push: everything in RoomPayload EXCEPT
/// `rooms`, which arrive as subsequent lines. Kept separate from RoomPayload so
/// the envelope deserializes on its own with no rooms present.
#[derive(Debug, Deserialize)]
pub struct StreamEnvelope {
    pub schema_version: u32,
    pub project: Project,
    pub model: Model,
    pub snapshot: Snapshot,
    pub levels: Vec<Level>,
}
```

### Route (in `main.rs`)

```rust
        // Streaming ingest for large models, alongside the buffered one.
        .route("/rooms/stream", post(ingest_rooms_stream))
```

### `Cargo.toml`

```toml
futures-util = "0.3"
tokio-util = { version = "0.7", features = ["io"] }
# tokio already has "full"; that includes io-util for AsyncBufReadExt.
```

---

## Body-limit interaction

`DefaultBodyLimit` still applies per-request and counts the **inflated** bytes
flowing through. For the streaming route you likely want it **disabled or very
high**, since the whole point is to accept a body too large to buffer:

```rust
use axum::extract::DefaultBodyLimit;
// on the streaming route only:
.route("/rooms/stream", post(ingest_rooms_stream)
    .layer(DefaultBodyLimit::disable()))   // rely on streaming, not a buffer cap
```

Keep the normal cap on the buffered `/rooms`.

---

## Honest limitation (next step if needed)

This streams *parsing* but still assembles all rooms in a `Vec` before storing —
so peak memory is roughly the in-memory room set, not the raw JSON text (a big
win, since the text is ~40% empty-string overhead). If even that Vec is too
large, the follow-on is a `SnapshotStore::put_streaming` that writes rooms to
disk as they arrive. Defer until the Vec itself is the ceiling.

## Scope

- Contract unchanged; new endpoint, buffered `/rooms` stays for small pushes.
- Stacks with gzip: decompression layer inflates, then we stream-parse.
- Empties still exported (QA), just cheap on the wire under gzip.
