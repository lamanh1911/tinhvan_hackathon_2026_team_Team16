"""
Sprint 4 — Schedule Proposal test (MockGraphClient)
Tests: create, get, approve, edge cases
"""
import httpx, json

BASE = "http://localhost:8000"
results = []

def check(name, cond, detail=""):
    results.append((name, cond, detail))
    tag = "PASS" if cond else "FAIL"
    print(f"  [{tag}] {name}" + (f"  -- {detail}" if detail else ""))
    return cond

def section(title):
    print(f"\n{'='*58}\n  {title}\n{'='*58}")

PROPOSAL_ID = None
PROPOSAL_ID2 = None

# ── S4-1: Create proposal (no params — uses mock members) ─────
section("S4-1  POST /schedule/online  (mock free-busy)")
try:
    r = httpx.post(f"{BASE}/schedule/online", json={}, timeout=15)
    b = r.json()
    check("status=201", r.status_code == 201, f"got {r.status_code}")
    if r.status_code == 201:
        PROPOSAL_ID = b["id"]
        slot_count = len(b.get("slots", []))
        check("status=draft", b.get("status") == "draft")
        check("returns 4 slots (all free, mock)", slot_count == 4, f"got {slot_count}")
        check("approved_slot_index=null", b.get("approved_slot_index") is None)
        check("customer_id=null (no customer passed)", b.get("customer_id") is None)
        slots = b.get("slots", [])
        if slots:
            s0 = slots[0]
            check("slot[0] has attendees", len(s0.get("attendees", [])) > 0)
            print(f"\n  Mock attendees (from MockGraphClient.get_free_busy → all free):")
            for a in s0.get("attendees", []):
                print(f"    {a['name']} <{a['email']}> : {a['status']}")
            print(f"\n  Slots proposed:")
            for s in slots:
                print(f"    [{s['index']}] {s['start'][:16]}  →  {s['end'][:16]}")
except Exception as e:
    check("request", False, str(e))

# ── S4-2: Create proposal with customer_id ────────────────────
section("S4-2  POST /schedule/online  (with customer_id)")
try:
    import uuid
    fake_customer = str(uuid.uuid4())
    r = httpx.post(
        f"{BASE}/schedule/online",
        json={"customer_id": fake_customer, "start_date": "2026-07-01"},
        timeout=15,
    )
    b = r.json()
    check("status=201", r.status_code == 201, f"got {r.status_code}")
    if r.status_code == 201:
        PROPOSAL_ID2 = b["id"]
        check("customer_id stored", b.get("customer_id") == fake_customer)
        check("start_date respected (slots after 2026-07-01)",
              all(s["start"] >= "2026-07-01" for s in b.get("slots", [])),
              f"first={b['slots'][0]['start'][:10] if b.get('slots') else 'none'}")
except Exception as e:
    check("request", False, str(e))

# ── S4-3: GET /schedule/{id} ──────────────────────────────────
section("S4-3  GET /schedule/{id}")
if PROPOSAL_ID:
    try:
        r = httpx.get(f"{BASE}/schedule/{PROPOSAL_ID}", timeout=10)
        b = r.json()
        check("status=200", r.status_code == 200, f"got {r.status_code}")
        check("correct id returned", b.get("id") == PROPOSAL_ID)
        check("status=draft", b.get("status") == "draft")
    except Exception as e:
        check("request", False, str(e))

# ── S4-4: GET /schedule (list) ────────────────────────────────
section("S4-4  GET /schedule  (list)")
try:
    r = httpx.get(f"{BASE}/schedule", timeout=10)
    b = r.json()
    check("status=200", r.status_code == 200, f"got {r.status_code}")
    ids = [p["id"] for p in b]
    check("proposal_1 in list", PROPOSAL_ID in ids if PROPOSAL_ID else False)
    check("proposal_2 in list", PROPOSAL_ID2 in ids if PROPOSAL_ID2 else False)
    print(f"  Total proposals in DB: {len(b)}")
except Exception as e:
    check("request", False, str(e))

# ── S4-5: Approve slot_index=1 ───────────────────────────────
section("S4-5  POST /schedule/{id}/approve  slot_index=1")
if PROPOSAL_ID:
    try:
        r = httpx.post(
            f"{BASE}/schedule/{PROPOSAL_ID}/approve",
            json={"slot_index": 1},
            timeout=10,
        )
        b = r.json()
        check("status=200", r.status_code == 200, f"got {r.status_code}")
        if r.status_code == 200:
            check("status=approved", b.get("status") == "approved")
            check("approved_slot_index=1", b.get("approved_slot_index") == 1)
            approved = b["slots"][1]
            print(f"  Approved slot: {approved['start'][:16]} → {approved['end'][:16]}")
    except Exception as e:
        check("request", False, str(e))

# ── S4-6: Edge — double approve ──────────────────────────────
section("S4-6  Edge: double-approve (should fail)")
if PROPOSAL_ID:
    try:
        r = httpx.post(
            f"{BASE}/schedule/{PROPOSAL_ID}/approve",
            json={"slot_index": 0},
            timeout=10,
        )
        b = r.json()
        check("blocked 400", r.status_code in (400, 422),
              f"got {r.status_code} {b.get('error',{}).get('code','')}")
    except Exception as e:
        check("request", False, str(e))

# ── S4-7: Edge — slot_index out of range ──────────────────────
section("S4-7  Edge: slot_index=99 out of range")
if PROPOSAL_ID2:
    try:
        r = httpx.post(
            f"{BASE}/schedule/{PROPOSAL_ID2}/approve",
            json={"slot_index": 99},
            timeout=10,
        )
        b = r.json()
        check("blocked 400", r.status_code in (400, 422),
              f"got {r.status_code} {b.get('error',{}).get('code','')}")
    except Exception as e:
        check("request", False, str(e))

# ── S4-8: Edge — non-existent proposal ───────────────────────
section("S4-8  Edge: GET non-existent proposal_id")
try:
    r = httpx.get(f"{BASE}/schedule/00000000-0000-0000-0000-000000000000", timeout=10)
    check("returns 404", r.status_code == 404, f"got {r.status_code}")
except Exception as e:
    check("request", False, str(e))

# ── Summary ──────────────────────────────────────────────────
section("SUMMARY")
passed = sum(1 for _, ok, _ in results if ok)
failed = sum(1 for _, ok, _ in results if not ok)
print(f"\n  Total: {len(results)}  |  Passed: {passed}  |  Failed: {failed}\n")
if failed:
    print("  Failed:")
    for name, ok, detail in results:
        if not ok:
            print(f"    [FAIL] {name} -- {detail}")
