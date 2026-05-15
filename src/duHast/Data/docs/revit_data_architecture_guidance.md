# Revit Data Architecture Guidance
## Collector vs Analysis Layer Design

> **Related documents**
> `readme.rst` — technical specification covering what data is exported from Revit, element types, sheet blueprint processing, and the graph database target. That document is the detailed *what*; this document is the architectural *why*.

---

## Background

This guidance captures a design discussion around how to structure Python data classes for Revit room and FFE (Furniture, Fixtures & Equipment) data. The core problem was that a single class (`DataRoom`) was being asked to serve two different purposes — raw data collection and curated analysis — which creates maintenance and design tension over time.

The `readme.rst` independently identifies the same tension: *"Data classes used to export all data are not suitable to represent templates. They also contain a lot of data exported from the Revit model which may not be required."* This guidance formalises that observation into a concrete architectural pattern.

---

## The Core Problem

The existing `DataRoom` collector class captures the full set of Revit room properties faithfully. It also holds an `associated_elements` list which is used to collect FFE items at capture time.

Three opposing concerns emerged:

- **Too much data for analysis** — the full collector output contains many properties that are irrelevant for comparison or downstream use
- **Wrong abstraction for FFE** — retrofitting FFE analysis onto `associated_elements` would force one class to serve conflicting purposes
- **Duplication risk** — embedding full room data inside an FFE-analysis class would duplicate data unnecessarily

---

## The Solution: Two Distinct Layers

### Layer 1 — Collector (existing, no changes required)

| Class | Purpose |
|---|---|
| `DataRoom` | Full faithful capture of Revit room data |
| `associated_elements` | Raw FFE items as collected from Revit |

This layer is **not changed**. Its job is "capture everything from Revit." It is verbose by design.

---

### Layer 2 — Analysis (new)

This is what `readme.rst` refers to as the **blueprint** or **template** layer. The term *analysis layer* is preferred here for consistency, but these are the same concept.

| Class | Purpose |
|---|---|
| `DataRoomAnalysis` | Curated room snapshot with only relevant properties |
| `DataFFEItem` | Single FFE item: curated properties + room-relative location |

This layer is purpose-built for comparison, templating, and downstream storage. It is lean by design.

---

## Workflow

```
Revit
  └── DataRoom (collector JSON)
        └── [processing step]
              └── DataRoomAnalysis (analysis JSON)
                    └── list of DataFFEItem
                          └── Graph Database
```

The processing step is where decisions are made: which room properties matter, how to translate absolute FFE coordinates to room-relative ones, and which FFE properties to carry forward.

The graph database is the ultimate downstream target (see `readme.rst`). The analysis JSON acts as the intermediate persistable form — it can be reloaded and pushed to the graph database without re-running the Revit collection step.

---

## Class Design Principles

### `DataRoomAnalysis`

- References the source room by `room_id` (e.g. `IfcGUID` or Revit element id) — not by embedding the full `DataRoom`
- Contains only the room properties relevant to analysis. Based on `readme.rst`, the confirmed candidates are:
  - Room size (sqm)
  - Room proportion (bounding box length X / length Y)
  - Number of FFE items in room
- Holds a list of `DataFFEItem` instances
- Supports JSON round-trip (persist and reload)
- `__eq__` based on curated properties only

### `DataFFEItem`

Based on the FFE tags TODO in `readme.rst`, the likely properties are:

- Family name and family type name (for linking to FFE tags)
- Insertion point / rotation of the element
- Location stored as relative coordinates within the room bounding box (not absolute model coordinates)
- Supports JSON round-trip
- `__eq__` compares properties only, **ignores location** — enabling "same FFE item, different position" comparisons

---

## Key Design Decisions

### Why not extend `associated_elements`?

`associated_elements` is a raw collector — it captures whatever Revit provides. Adding curated analysis logic into it would conflate two responsibilities and make the class harder to maintain.

### Why not embed `DataRoom` inside `DataRoomAnalysis`?

Embedding the full room object would duplicate data. Instead, `DataRoomAnalysis` holds only a reference (`room_id`) back to the collector. The full collector JSON remains the source of truth if full room context is ever needed.

### Why composition over inheritance?

The `readme.rst` raises the possibility of an inheritance architecture (export class and type class inheriting from a base). For the analysis layer, this is not recommended. `DataRoomAnalysis` and `DataRoom` have different responsibilities and different lifecycles — inheritance would couple them unnecessarily. Referencing by `room_id` keeps them independent.

### Why keep `__eq__` on `DataRoom` unchanged?

Room identity (equality) should not depend on its FFE contents. A separate comparison method (e.g. `has_same_ffe(self, other)`) on `DataRoomAnalysis` keeps the two concerns cleanly separated.

---

## Persistence

Both layers persist independently to JSON:

| File | Contains |
|---|---|
| `rooms.json` | Full collector output (`DataRoom`) |
| `rooms_analysis.json` | Curated analysis output (`DataRoomAnalysis` + `DataFFEItem`) |

The analysis JSON can be reloaded independently without needing to re-run the Revit collection step. From the analysis JSON the data can then be pushed to the graph database.

---

## Relationship to `readme.rst`

| Topic | readme.rst | This document |
|---|---|---|
| What data is exported from Revit | ✅ Detailed | — |
| Element types (doors, ceilings, rooms) | ✅ Detailed | — |
| Sheet blueprint processing logic | ✅ Detailed | — |
| Graph database target | ✅ Referenced | Referenced |
| Why two layers are needed | Noted briefly | ✅ Detailed |
| Class design principles | — | ✅ Detailed |
| Composition vs inheritance decision | Raised as option | ✅ Resolved |
| Terminology alignment (blueprint = analysis layer) | Uses "blueprint" | ✅ Reconciled |

---

## Next Steps

1. Confirm which room properties are needed in `DataRoomAnalysis` (size, proportion, item count confirmed; others TBD)
2. Confirm the FFE properties per item — family name, type name, and insertion point are candidates from `readme.rst`
3. Implement `DataFFEItem` following the existing data class pattern (`data_type`, `__init__(j=None)`, `__eq__`, `__hash__`)
4. Implement `DataRoomAnalysis` following the same pattern
5. Write the processing step that translates `DataRoom` → `DataRoomAnalysis`
6. Define the graph database schema that `DataRoomAnalysis` will map to
