# Handover: gzip-compress `/rooms` POST bodies

## Why

FFE exports are already >100 MB uncompressed. The bodies are highly repetitive
JSON (room after room of near-identical property bags), so gzip typically cuts
~85–95%. This keeps JSON everywhere — we only wrap the transport, not the
contract. gzip is platform-independent (RFC 1952): compress in IronPython on
Windows, decompress in Rust on Linux, byte-identical.

Two independent changes: **sender compresses**, **server transparently
decompresses**. Handlers and the JSON contract stay untouched.

---

## 1. Sender (Python / IronPython) — `post_rooms.py`

The extractor runs in-process on .NET, so prefer **.NET's `GZipStream`** over
Python's `gzip` module. Python's stdlib `gzip`/`zlib` is importable in
IronPython but routes through `System.IO.Compression` with occasional
edge-case differences from CPython — using .NET directly avoids that and is
already loaded.

Compress the UTF-8 JSON bytes and set `Content-Encoding: gzip` so the server
knows to inflate.

```python
import clr
clr.AddReference("System")
from System.IO import MemoryStream
from System.IO.Compression import GZipStream, CompressionMode
from System.Text import Encoding

def gzip_bytes(text):
    """UTF-8-encode `text` and return gzip-compressed bytes (RFC 1952)."""
    raw = Encoding.UTF8.GetBytes(text)
    out = MemoryStream()
    # `leaveOpen=False` (3rd arg) lets GZipStream close/flush its footer into
    # `out` when disposed — required, or the gzip trailer is never written.
    gz = GZipStream(out, CompressionMode.Compress)
    gz.Write(raw, 0, raw.Length)
    gz.Close()                 # flushes the gzip footer; do NOT skip
    return out.ToArray()

# --- at the POST site ---
body = gzip_bytes(json_string)          # json_string = the payload you already build
request.Headers["Content-Encoding"] = "gzip"
request.Headers["Content-Type"] = "application/json"
# send `body` (byte[]) as the request content
```

Notes:
- Compress the **final serialized JSON string**, not a dict — encode to bytes
  first, then gzip.
- Do **not** also set `Content-Length` by hand; let `HttpClient` compute it
  from the compressed byte array.
- Keep `Content-Type: application/json` — that describes the *decompressed*
  body, which is what axum's `Json` extractor still sees.

---

## 2. Server (Rust / axum) — decompress transparently

`tower-http` can inflate a gzip request body **before** the `Json` extractor
runs, so `ingest_rooms` needs no change at all.

### 2a. `Cargo.toml` — add the feature

```toml
# add "decompression-gzip" to the existing tower-http features
tower-http = { version = "0.6", features = ["fs", "cors", "trace", "decompression-gzip"] }
```

### 2b. `main.rs` — import + layer

```rust
// add to the tower-http use line:
use tower_http::decompression::RequestDecompressionLayer;
```

Add the layer to the router. **Order matters**: the decompression layer must
sit so it runs *before* the body reaches the handler. With axum/tower, layers
added later wrap earlier ones on the request path, so add
`RequestDecompressionLayer` — it inflates the body, then the request continues
inward to `ingest_rooms` where `Json` deserializes the now-plain bytes.

```rust
    let app = Router::new()
        .route("/rooms", post(ingest_rooms).get(get_rooms))
        .route("/projects", get(get_projects))
        .route("/projects/{id}/buildings", get(get_project_buildings))
        .route("/projects/{id}/validation", get(get_project_validation))
        .fallback_service(ServeDir::new("static"))
        // Inflate gzip request bodies (Content-Encoding: gzip) before the
        // Json extractor sees them. Transparent: a non-gzip body passes
        // through untouched, so old uncompressed senders still work — this is
        // purely additive. FFE exports are >100 MB uncompressed; gzip on the
        // wire keeps them well under the body-size cap below.
        .layer(RequestDecompressionLayer::new())
        // Body-size cap applies to the DECOMPRESSED body. A 100 MB export may
        // gzip to ~5–15 MB on the wire, but this limit governs the inflated
        // size, so it must be large enough for the full uncompressed payload.
        // (If DefaultBodyLimit isn't already added, add it here — see the
        // earlier body-limit change.)
        .layer(CorsLayer::permissive())
        .layer(TraceLayer::new_for_http())
        .with_state(state);
```

### Interaction with the body-size limit (important)

`DefaultBodyLimit` measures the **decompressed** body (it counts bytes as they
come out of the decompression layer). So a 100 MB uncompressed export still
needs the limit set to ≥100 MB even though only ~10 MB crossed the network.
gzip solves *network transfer*, not the in-memory buffered size — set the cap
to whatever the largest inflated payload will be.

If a decompression-bomb ceiling is ever a concern, the body limit is exactly
the guard: an oversized inflated body is rejected once it exceeds the cap.

---

## Verify

```bash
# compress a sample and POST it
gzip -c sample.json > sample.json.gz
curl -v -X POST http://127.0.0.1:5151/rooms \
  -H "Content-Type: application/json" \
  -H "Content-Encoding: gzip" \
  --data-binary @sample.json.gz
# expect 200 + {"accepted":true,...}; a plain (non-gzip) POST must still work too
```

---

## Scope / non-goals

- **Contract unchanged.** v5 JSON shape is identical; only transport is wrapped.
- **Empties still exported.** They're kept deliberately for the QA "param has no
  value" check — gzip makes keeping them cheap on the wire.
- **Response compression** (server → browser) is a separate `CompressionLayer`,
  not covered here — the `/rooms` GET payload is small by comparison.
