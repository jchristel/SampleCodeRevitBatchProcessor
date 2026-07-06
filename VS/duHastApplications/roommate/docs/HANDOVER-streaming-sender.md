# Handover: sender-side NDJSON streaming (IronPython)

## Format recap

One JSON object per line. Line 1 = envelope (no rooms). Each next line = one room.

```
{"schema_version":5,"project":{...},"model":{...},"snapshot":{...},"levels":[...]}
{"id":"r1",...}
{"id":"r2",...}
```

## Key point: stream, don't build one big string

The whole win is **never holding the full payload in memory** — neither on the
server nor here. So serialize and write each room as it's extracted, straight
into a gzip stream feeding the HTTP request. Don't assemble a giant list first.

## Python (IronPython, .NET streams)

```python
import clr
clr.AddReference("System")
clr.AddReference("System.Net.Http")
from System.IO import MemoryStream
from System.IO.Compression import GZipStream, CompressionMode
from System.Text import Encoding
from System.Net.Http import HttpClient, ByteArrayContent
from System.Net.Http.Headers import MediaTypeHeaderValue
import json

def write_line(gz, obj):
    """Serialize one object to a compact JSON line and write it (UTF-8) into
    the gzip stream, followed by '\n'. One object = one NDJSON line."""
    line = json.dumps(obj, separators=(",", ":")) + "\n"   # compact, no spaces
    data = Encoding.UTF8.GetBytes(line)
    gz.Write(data, 0, data.Length)

def build_ndjson_gzip(envelope, rooms_iter):
    """Return gzip-compressed NDJSON bytes. `rooms_iter` yields one room dict
    at a time — iterate lazily so we never hold all rooms at once."""
    out = MemoryStream()
    # leaveOpen defaults False: closing gz flushes the gzip footer into `out`.
    gz = GZipStream(out, CompressionMode.Compress)
    write_line(gz, envelope)              # line 1: envelope, no rooms
    for room in rooms_iter:               # lazy: extract + write one at a time
        write_line(gz, room)
    gz.Close()                            # MUST close to flush footer
    return out.ToArray()

# --- POST ---
body = build_ndjson_gzip(envelope, extract_rooms())   # extract_rooms() is a generator
content = ByteArrayContent(body)
content.Headers.ContentType = MediaTypeHeaderValue("application/x-ndjson")
content.Headers.Add("Content-Encoding", "gzip")

client = HttpClient()
resp = client.PostAsync("http://127.0.0.1:5151/rooms/stream", content).Result
print(resp.StatusCode, resp.Content.ReadAsStringAsync().Result)
```

## Notes

- `extract_rooms()` should be a **generator** (`yield` one room dict per Revit
  room) so extraction and compression pipeline together — peak memory stays low
  even though `MemoryStream` still holds the *compressed* bytes (small).
- `separators=(",", ":")` gives compact JSON; no newlines *inside* a room, so
  one line = one room holds.
- Envelope must carry `schema_version`, `project`, `model`, `snapshot`,
  `levels` — everything except `rooms`.
- To go fully streaming (not even holding compressed bytes), swap
  `ByteArrayContent`/`MemoryStream` for a `StreamContent` over a pipe — deferred;
  the compressed body is small enough that `ByteArrayContent` is fine first.
```
