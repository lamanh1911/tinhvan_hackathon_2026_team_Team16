"""
Sprint 6 -- FR-04 Offline Schedule + Travel Buffer test
MockMapsClient (30 min fixed) + MockGraphClient (all free)
"""
import httpx

BASE = "http://localhost:8000"
results = []

PROPOSAL_ID = None
PROPOSAL_ID2 = None


def check(name, cond, detail=""):
    results.append((name, cond, detail))
    tag = "PASS" if cond else "FAIL"
    safe = str(detail).encode("ascii", errors="replace").decode("ascii")
    print(f"  [{tag}] {name}" + (f"  -- {safe}" if safe else ""))
    return cond


def section(title):
    print(f"\n{'='*60}\n  {title}\n{'='*60}")


# ── S6-1: POST /schedule/offline ─────────────────────────────────
section("S6-1  POST /schedule/offline  (MockMapsClient 30 min buffer)")
try:
    r = httpx.post(
        f"{BASE}/schedule/offline",
        json={"location": "123 Nguyen Hue, Ho Chi Minh City"},
        timeout=15,
    )
    b = r.json()
    check("status=201", r.status_code == 201, f"got {r.status_code}")
    if r.status_code == 201:
        PROPOSAL_ID = b["id"]
        check("mode=offline", b.get("mode") == "offline", b.get("mode"))
        check("location stored", b.get("location") == "123 Nguyen Hue, Ho Chi Minh City")
        check("status=draft", b.get("status") == "draft")
        slot_count = len(b.get("slots", []))
        check("returns 4 slots (all free mock)", slot_count == 4, f"got {slot_count}")
        check("approved_slot_index=null", b.get("approved_slot_index") is None)
        slots = b.get("slots", [])
        if slots:
            s0 = slots[0]
            buf = s0.get("travel_buffer_minutes")
            check("travel_buffer_minutes=30 in slot[0]", buf == 30, f"got {buf}")
            check("all slots have buffer=30",
                  all(s.get("travel_buffer_minutes") == 30 for s in slots),
                  str([s.get("travel_buffer_minutes") for s in slots]))
            print(f"\n  Slots with travel buffer:")
            for s in slots:
                print(f"    [{s['index']}] {s['start'][:16]}  +{s.get('travel_buffer_minutes')}min buffer")
except Exception as e:
    check("request", False, str(e))

# ── S6-2: GET /schedule/{id} ─────────────────────────────────────
section("S6-2  GET /schedule/{id}  (verify stored mode + location + buffer)")
if PROPOSAL_ID:
    try:
        r = httpx.get(f"{BASE}/schedule/{PROPOSAL_ID}", timeout=10)
        b = r.json()
        check("status=200", r.status_code == 200, f"got {r.status_code}")
        check("mode=offline", b.get("mode") == "offline")
        check("location persisted", b.get("location") == "123 Nguyen Hue, Ho Chi Minh City")
        slots = b.get("slots", [])
        check("travel_buffer_minutes in every slot",
              all(s.get("travel_buffer_minutes") == 30 for s in slots),
              str([s.get("travel_buffer_minutes") for s in slots]))
    except Exception as e:
        check("request", False, str(e))

# ── S6-3: POST offline with customer_id ──────────────────────────
section("S6-3  POST /schedule/offline  (with customer_id)")
try:
    import uuid
    fake_cid = str(uuid.uuid4())
    r = httpx.post(
        f"{BASE}/schedule/offline",
        json={
            "location": "45 Le Loi, District 1",
            "customer_id": fake_cid,
            "start_date": "2026-07-01",
        },
        timeout=15,
    )
    b = r.json()
    check("status=201", r.status_code == 201, f"got {r.status_code}")
    if r.status_code == 201:
        PROPOSAL_ID2 = b["id"]
        check("customer_id stored", b.get("customer_id") == fake_cid)
        check("location stored", b.get("location") == "45 Le Loi, District 1")
        check("start_date respected",
              all(s["start"] >= "2026-07-01" for s in b.get("slots", [])),
              f"first={b['slots'][0]['start'][:10] if b.get('slots') else 'none'}")
        check("buffer in all slots",
              all(s.get("travel_buffer_minutes") == 30 for s in b.get("slots", [])))
except Exception as e:
    check("request", False, str(e))

# ── S6-4: Approve slot_index=0 ───────────────────────────────────
section("S6-4  POST /schedule/{id}/approve  slot_index=0")
if PROPOSAL_ID:
    try:
        r = httpx.post(
            f"{BASE}/schedule/{PROPOSAL_ID}/approve",
            json={"slot_index": 0},
            timeout=10,
        )
        b = r.json()
        check("status=200", r.status_code == 200, f"got {r.status_code}")
        if r.status_code == 200:
            check("status=approved", b.get("status") == "approved")
            check("approved_slot_index=0", b.get("approved_slot_index") == 0)
            check("mode still offline", b.get("mode") == "offline")
            approved = b["slots"][0]
            print(f"  Approved: {approved['start'][:16]} +{approved.get('travel_buffer_minutes')}min buffer")
    except Exception as e:
        check("request", False, str(e))

# ── S6-5: Edge — missing location ────────────────────────────────
section("S6-5  Edge: POST /schedule/offline without location  (should fail)")
try:
    r = httpx.post(f"{BASE}/schedule/offline", json={}, timeout=10)
    check("blocked 422", r.status_code == 422, f"got {r.status_code}")
except Exception as e:
    check("request", False, str(e))

# ── S6-5b: Edge — empty location string ──────────────────────────
section("S6-5b  Edge: POST /schedule/offline with empty location  (should fail)")
try:
    r = httpx.post(f"{BASE}/schedule/offline", json={"location": ""}, timeout=10)
    check("blocked 422", r.status_code == 422, f"got {r.status_code}")
except Exception as e:
    check("request", False, str(e))

# ── S6-6: Edge — double approve ──────────────────────────────────
section("S6-6  Edge: double-approve offline proposal  (should fail)")
if PROPOSAL_ID:
    try:
        r = httpx.post(
            f"{BASE}/schedule/{PROPOSAL_ID}/approve",
            json={"slot_index": 1},
            timeout=10,
        )
        b = r.json()
        check("blocked 400/422", r.status_code in (400, 422),
              f"got {r.status_code} {b.get('error', {}).get('code', '')}")
    except Exception as e:
        check("request", False, str(e))

# ── S6-7: Regression — online proposal still works ───────────────
section("S6-7  Regression: POST /schedule/online  (mode=online, no buffer)")
try:
    r = httpx.post(f"{BASE}/schedule/online", json={}, timeout=15)
    b = r.json()
    check("status=201", r.status_code == 201, f"got {r.status_code}")
    if r.status_code == 201:
        check("mode=online", b.get("mode") == "online", b.get("mode"))
        check("location=null", b.get("location") is None)
        slots = b.get("slots", [])
        check("4 slots", len(slots) == 4, f"got {len(slots)}")
        check("no travel_buffer in online slots",
              all(s.get("travel_buffer_minutes") is None for s in slots),
              str([s.get("travel_buffer_minutes") for s in slots]))
except Exception as e:
    check("request", False, str(e))

# ── Summary ──────────────────────────────────────────────────────
section("SUMMARY")
passed = sum(1 for _, ok, _ in results if ok)
failed = sum(1 for _, ok, _ in results if not ok)
print(f"\n  Total: {len(results)}  |  Passed: {passed}  |  Failed: {failed}\n")
if failed:
    print("  Failed:")
    for name, ok, detail in results:
        if not ok:
            safe = str(detail).encode("ascii", errors="replace").decode("ascii")
            print(f"    [FAIL] {name} -- {safe}")
else:
    print("  All checks passed.")
