# NFC Project — Quick README

> Lightweight asset-tracking for venue carts (chairs, stanchions, signs, tables, stages) using NFC tags (with optional barcode fallback).

## 1) What this is

A simple system to **identify carts**, **log usage**, and **find where they’re parked**. Each cart has a unique tag. Staff scan the tag with a phone to view/update status and location.

## 2) Core goals

* **Fast ID**: Tap once → see cart contents & status.
* **Where is it?**: Record last-known location and timestamp.
* **Who used it?**: Optional user check‑in / check‑out.
* **Offline-friendly**: Queue scans if there’s no service; sync later.
* **Barcode fallback**: If NFC fails, scan a printed code with the same ID.

## 3) Components

* **Tags**: NTAG213/215/216 NFC stickers (ISO 14443A). Printed QR/Code128 with same UID.
* **Mobile**: PWA or native (Android first, iOS via web NFC or camera QR).
* **API**: Minimal REST (Node/Express or FastAPI) + SQLite/Postgres.
* **Dashboard**: Web UI for search, filters, and history.

## 4) ID & tag schema

**Tag payload (NDEF URL):** `https://<host>/c/<cart_id>`
**cart_id format:** `CART-XXXX` (e.g., `CART-0137`)
**Human label:** Big text `CART-0137`, small text with contents, barcode/QR of the same URL.

**Recommended fields per cart**

* `cart_id` (string, PK)
* `label` (human name, optional)
* `contents` (enum/tags: chairs, stanchions, signs, tables, stages, misc)
* `status` (enum: available, in_use, staged, maintenance, missing)
* `location_zone` (enum: dock, lobby A, lobby B, storage west, storage east, stage L/R)
* `location_note` (free text)
* `last_seen_at` (timestamp)

**Event log fields**

* `event_id` (uuid)
* `cart_id`
* `type` (check_in, check_out, move, audit, maintenance)
* `by_user` (email or staff id)
* `zone` / `note`
* `ts` (timestamp)

## 5) Minimal database sketch (SQL)

```sql
-- carts
CREATE TABLE carts (
  cart_id TEXT PRIMARY KEY,
  label TEXT,
  contents TEXT,
  status TEXT CHECK (status IN ('available','in_use','staged','maintenance','missing')) DEFAULT 'available',
  location_zone TEXT,
  location_note TEXT,
  last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- events (append-only)
CREATE TABLE cart_events (
  event_id TEXT PRIMARY KEY,
  cart_id TEXT REFERENCES carts(cart_id),
  type TEXT CHECK (type IN ('check_in','check_out','move','audit','maintenance')),
  by_user TEXT,
  zone TEXT,
  note TEXT,
  ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_events_cart_ts ON cart_events(cart_id, ts DESC);
```

## 6) API (suggested)

**`GET /api/carts/:cart_id`** → cart details + last 10 events
**`POST /api/carts/:cart_id/event`** → body `{ type, zone?, note?, by_user? }`
**`PATCH /api/carts/:cart_id`** → update `status`, `contents`, `location_zone`, `location_note`

**Auth:** simple token in header (bearer) or staff PIN per device.

## 7) Mobile workflow (staff)

1. **Tap NFC** or **scan QR**.
2. App opens `…/c/CART-0137` → shows status, zone, contents.
3. One‑tap actions: **Check out**, **Move to zone**, **Check in**, **Audit**.
4. If offline → events stored locally; badge shows **Sync** when online.

## 8) Dashboard workflow (lead)

* Search by `cart_id`, contents, status, or zone.
* Filter: **missing**, **in use > 8h**, **maintenance**.
* Click cart → timeline of events.
* Bulk actions: re‑zone multiple carts, mark as staged for event.

## 9) NFC writing checklist

* Encode NDEF URL to each tag: `https://<host>/c/<cart_id>`.
* Lock tag **after** verifying scan.
* Place sticker where phones can tap easily (edge/corner of cart).
* Add printed label + QR.

## 10) Environment & config

Create `.env` for server:

```
PORT=8080
DATABASE_URL=sqlite:./data.db  # or postgres://user:pass@host/db
JWT_SECRET=change_me
BASE_URL=https://example.org
```

## 11) Security & privacy

* Only store staff identifiers required for audits (email or employee ID).
* No personal phones? Use shared devices with app PIN.
* Rate‑limit event posts; validate `cart_id` exists.
* Sign out lost devices from admin panel.

## 12) Rollout plan (practical)

1. **Pilot (5–10 carts)**: tag, encode, test zones, train 2–3 staff.
2. **Tune zones**: ensure names match how staff talk (“north dock”, “west storage”).
3. **Expand**: tag remaining carts; print a quick‑ref card at each dock.
4. **Monthly audit**: export events CSV; check “missing/inactive” carts.

## 13) Troubleshooting quickies

* **Scan opens wrong cart** → check printed/encoded IDs match; re‑encode and relabel.
* **No NFC on iPhone** → use QR; ensure camera opens the same URL.
* **Location stale** → confirm staff are using **Move** action when repositioning.
* **Offline devices** → verify sync banner; check Wi‑Fi/permissions.

## 14) Roadmap (nice‑to‑have)

* Zone heatmap, usage duration KPIs.
* Geo‑fence via BLE beacons for auto‑zone.
* Bulk import/export; Google Sheets bridge.
* Push alert: cart marked **missing** for >24h.

---

**Maintainer:** Anthony
**Project:** `nfc_project`
**License:** MIT (change if needed)
