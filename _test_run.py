import httpx
import json
import sys
import os

BASE = "http://localhost:8000"
PASS_S = "PASS"
FAIL_S = "FAIL"
INFO_S = "INFO"

results = []

def check(name, condition, detail=""):
    results.append((name, condition, detail))
    status = PASS_S if condition else FAIL_S
    print(f"  [{status}] {name}" + (f" -- {detail}" if detail else ""))
    return condition

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

# ─────────────────────────────────────────────────────────────
# SPRINT 2 — Card Upload
# ─────────────────────────────────────────────────────────────
section("SPRINT 2 -- FR-01: Business Card Upload")

def scan_image(path):
    with open(path, "rb") as f:
        data = f.read()
    fname = os.path.basename(path)
    ctype = "image/jpeg" if path.endswith(".jpg") else "image/png"
    r = httpx.post(
        f"{BASE}/cards/scan",
        files={"file": (fname, data, ctype)},
        timeout=90.0,
    )
    return r

GOOD_CARD_ID = None

# S2-1: test-card.png — expected: valid business card
print("\n[S2-1] Happy path -- test-card.png")
try:
    r = scan_image("test-card.png")
    if r.status_code == 201:
        body = r.json()
        check("S2-1 status=201", True, f"id={str(body['id'])[:8]}...")
        check("S2-1 is_valid_card=true", body.get("is_valid_card") is True)
        fields = body.get("fields", {})
        extracted = [k for k, v in fields.items() if v.get("value")]
        check("S2-1 fields extracted", len(extracted) > 0, f"fields: {extracted}")
        GOOD_CARD_ID = body["id"]
    else:
        body = r.json()
        check("S2-1 status=201", False, f"got {r.status_code}: {json.dumps(body)[:120]}")
except Exception as e:
    check("S2-1 request", False, str(e))

# S2-2 to S2-5: scan all other images, report classification
print("\n[S2-2..5] Edge cases -- non-business-card images")
image_files = [
    "Image.jpg",
    "Image (1).jpg",
    "Image (2).jpg",
    "Image (3).jpg",
    "Image (4).jpg",
    "Image (5).jpg",
    "Image (6).jpg",
    "Image (7).jpg",
    "Image (8).jpg",
    "image.png",
    "image (1).png",
]

for fname in image_files:
    if not os.path.exists(fname):
        continue
    try:
        r = scan_image(fname)
        if r.status_code == 201:
            body = r.json()
            print(f"  [INFO] {fname} --> 201 VALID CARD (is_valid={body.get('is_valid_card')})")
        elif r.status_code == 422:
            body = r.json()
            code = body.get("error", {}).get("code", "?")
            msg  = body.get("error", {}).get("message", "?")[:70]
            check(f"{fname} --> 422 {code}", True, msg)
        else:
            body = r.json()
            print(f"  [FAIL] {fname} --> unexpected {r.status_code}: {json.dumps(body)[:80]}")
    except Exception as e:
        print(f"  [FAIL] {fname} --> {e}")

# S2-6: Confirm card with missing required field
print("\n[S2-6] Edge -- confirm card with missing name")
if GOOD_CARD_ID:
    try:
        # Clear name field
        httpx.patch(f"{BASE}/cards/{GOOD_CARD_ID}", json={"name": ""}, timeout=10.0)
        r2 = httpx.post(f"{BASE}/cards/{GOOD_CARD_ID}/confirm", timeout=10.0)
        check("S2-6 confirm rejected (missing name)", r2.status_code in (400, 422),
              f"got {r2.status_code}")
    except Exception as e:
        check("S2-6 request", False, str(e))
else:
    print("  [SKIP] no valid card from S2-1")

# ─────────────────────────────────────────────────────────────
# SPRINT 3 — Email State Machine
# ─────────────────────────────────────────────────────────────
section("SPRINT 3 -- FR-02: Email State Machine")

EMAIL_ID = None
MEETING_ID = None

# Setup: scan + confirm card to get customer_id, then create meeting linked to that customer
print("\n[S3-0] Setup -- scan card + confirm + create linked meeting")
_SAMPLE_TRANSCRIPT = (
    "Meeting: Q3 Partnership Discussion\n"
    "Date: 2026-06-13\n"
    "Participants: Alice (Sales), Bob (BrSE), Customer\n\n"
    "Alice: Thank you for joining. Let's discuss the Q3 scope.\n"
    "Customer: We need a revised proposal by next week.\n"
    "Bob: I can prepare a technical integration doc.\n"
    "Alice: Agreed. Next steps: send revised proposal by June 20, "
    "schedule technical call by June 25.\n"
)
CUSTOMER_ID = None
try:
    # Scan a fresh business card
    with open("test-card.png", "rb") as f:
        card_data = f.read()
    rc = httpx.post(
        f"{BASE}/cards/scan",
        files={"file": ("test-card.png", card_data, "image/png")},
        timeout=90.0,
    )
    if rc.status_code == 201:
        setup_card_id = rc.json()["id"]
        # Confirm the card → creates customer
        rconf = httpx.post(f"{BASE}/cards/{setup_card_id}/confirm", timeout=10.0)
        if rconf.status_code == 201:
            CUSTOMER_ID = str(rconf.json().get("customer_id"))
            print(f"    customer_id={CUSTOMER_ID[:8] if CUSTOMER_ID else None}...")
        else:
            print(f"    confirm failed: {rconf.status_code} {rconf.text[:100]}")
    else:
        print(f"    card scan failed: {rc.status_code} {rc.text[:100]}")
except Exception as e:
    print(f"    card setup error: {e}")

try:
    form_data = {"file": ("transcript.txt", _SAMPLE_TRANSCRIPT.encode(), "text/plain")}
    extra = {"customer_id": CUSTOMER_ID} if CUSTOMER_ID else {}
    r = httpx.post(
        f"{BASE}/meetings/mom",
        files=form_data,
        data=extra,
        timeout=60.0,
    )
    if r.status_code == 201:
        body = r.json()
        MEETING_ID = str(body.get("meeting_id"))
        check("S3-0 meeting created", bool(MEETING_ID), f"meeting_id={MEETING_ID[:8] if MEETING_ID else None}...")
    else:
        check("S3-0 meeting created", False, f"got {r.status_code}: {r.text[:120]}")
except Exception as e:
    check("S3-0 meeting created", False, str(e))

print("\n[S3-1] POST /emails/thank-you")
try:
    payload = {"meeting_id": MEETING_ID} if MEETING_ID else {}
    r = httpx.post(f"{BASE}/emails/thank-you", json=payload, timeout=15.0)
    check("S3-1 status=201", r.status_code == 201, f"got {r.status_code}")
    if r.status_code == 201:
        body = r.json()
        EMAIL_ID = body["id"]
        check("S3-1 status=draft", body.get("status") == "draft", body.get("status"))
        check("S3-1 has subject", bool(body.get("subject")), repr(body.get("subject")).encode('ascii', errors='replace').decode('ascii'))
        subject_preview = str(body.get('subject', ''))[:70].encode('ascii', errors='replace').decode('ascii')
        print(f"    subject: {subject_preview}")
        body_preview = str(body.get('body', ''))[:100].encode('ascii', errors='replace').decode('ascii')
        print(f"    body preview: {body_preview}")
except Exception as e:
    check("S3-1 request", False, str(e))

print("\n[S3-2] PATCH /emails/{id} -- edit body")
if EMAIL_ID:
    try:
        r = httpx.patch(
            f"{BASE}/emails/{EMAIL_ID}",
            json={"body": "Edited body text for testing."},
            timeout=10.0,
        )
        check("S3-2 status=200", r.status_code == 200, f"got {r.status_code}")
        if r.status_code == 200:
            check("S3-2 body updated", "Edited body" in (r.json().get("body") or ""))
    except Exception as e:
        check("S3-2 request", False, str(e))

print("\n[S3-6] Edge -- send when status=draft (should fail)")
if EMAIL_ID:
    try:
        r = httpx.post(f"{BASE}/emails/{EMAIL_ID}/send", timeout=10.0)
        check("S3-6 send blocked (draft)", r.status_code in (400, 422),
              f"got {r.status_code} {r.json().get('error',{}).get('code','')}")
    except Exception as e:
        check("S3-6 request", False, str(e))

print("\n[S3-3] POST /emails/{id}/submit --> in_review")
if EMAIL_ID:
    try:
        r = httpx.post(f"{BASE}/emails/{EMAIL_ID}/submit", timeout=10.0)
        check("S3-3 status=200", r.status_code == 200, f"got {r.status_code}")
        if r.status_code == 200:
            check("S3-3 status=in_review", r.json().get("status") == "in_review")
    except Exception as e:
        check("S3-3 request", False, str(e))

print("\n[S3-7] Edge -- send when status=in_review (should fail)")
if EMAIL_ID:
    try:
        r = httpx.post(f"{BASE}/emails/{EMAIL_ID}/send", timeout=10.0)
        check("S3-7 send blocked (in_review)", r.status_code in (400, 422),
              f"got {r.status_code} {r.json().get('error',{}).get('code','')}")
    except Exception as e:
        check("S3-7 request", False, str(e))

print("\n[S3-4] POST /emails/{id}/approve --> approved")
if EMAIL_ID:
    try:
        r = httpx.post(f"{BASE}/emails/{EMAIL_ID}/approve", timeout=10.0)
        check("S3-4 status=200", r.status_code == 200, f"got {r.status_code}")
        if r.status_code == 200:
            check("S3-4 status=approved", r.json().get("status") == "approved")
    except Exception as e:
        check("S3-4 request", False, str(e))

print("\n[S3-8] Edge -- PATCH after approved (should be blocked)")
if EMAIL_ID:
    try:
        r = httpx.patch(
            f"{BASE}/emails/{EMAIL_ID}",
            json={"body": "try to edit after approve"},
            timeout=10.0,
        )
        check("S3-8 PATCH blocked after approved", r.status_code in (400, 422),
              f"got {r.status_code}")
    except Exception as e:
        check("S3-8 request", False, str(e))

print("\n[S3-5] POST /emails/{id}/send --> sent (mark only, no real email)")
if EMAIL_ID:
    try:
        r = httpx.post(f"{BASE}/emails/{EMAIL_ID}/send", timeout=10.0)
        check("S3-5 status=200", r.status_code == 200, f"got {r.status_code}")
        if r.status_code == 200:
            check("S3-5 status=sent", r.json().get("status") == "sent")
    except Exception as e:
        check("S3-5 request", False, str(e))

# ─────────────────────────────────────────────────────────────
# SPRINT 4 — Schedule Proposal
# ─────────────────────────────────────────────────────────────
section("SPRINT 4 -- FR-03: Online Schedule Proposal")

PROPOSAL_ID = None

print("\n[S4-1] POST /schedule/online")
try:
    r = httpx.post(f"{BASE}/schedule/online", json={}, timeout=10.0)
    check("S4-1 status=201", r.status_code == 201, f"got {r.status_code}")
    if r.status_code == 201:
        body = r.json()
        PROPOSAL_ID = body["id"]
        slot_count = len(body.get("slots", []))
        check("S4-1 status=draft", body.get("status") == "draft")
        check("S4-1 returns 3-4 slots", 3 <= slot_count <= 4, f"got {slot_count} slots")
        check("S4-1 approved_slot_index=null", body.get("approved_slot_index") is None)
        if body.get("slots"):
            s = body["slots"][0]
            check("S4-1 slot has attendees", len(s.get("attendees", [])) > 0)
            print(f"    Slot[0]: {s['start'][:16]} -- {s['end'][:16]}")
            for a in s.get("attendees", []):
                print(f"      {a['name']} <{a['email']}> : {a['status']}")
except Exception as e:
    check("S4-1 request", False, str(e))

print("\n[S4-2] GET /schedule/{id}")
if PROPOSAL_ID:
    try:
        r = httpx.get(f"{BASE}/schedule/{PROPOSAL_ID}", timeout=10.0)
        check("S4-2 status=200", r.status_code == 200, f"got {r.status_code}")
        if r.status_code == 200:
            check("S4-2 correct id", r.json().get("id") == PROPOSAL_ID)
    except Exception as e:
        check("S4-2 request", False, str(e))

print("\n[S4-3] POST /schedule/{id}/approve slot_index=0")
if PROPOSAL_ID:
    try:
        r = httpx.post(
            f"{BASE}/schedule/{PROPOSAL_ID}/approve",
            json={"slot_index": 0},
            timeout=10.0,
        )
        check("S4-3 status=200", r.status_code == 200, f"got {r.status_code}")
        if r.status_code == 200:
            body = r.json()
            check("S4-3 status=approved", body.get("status") == "approved")
            check("S4-3 approved_slot_index=0", body.get("approved_slot_index") == 0)
    except Exception as e:
        check("S4-3 request", False, str(e))

print("\n[S4-4] Edge -- double-approve same proposal")
if PROPOSAL_ID:
    try:
        r = httpx.post(
            f"{BASE}/schedule/{PROPOSAL_ID}/approve",
            json={"slot_index": 1},
            timeout=10.0,
        )
        check("S4-4 double-approve blocked", r.status_code in (400, 422),
              f"got {r.status_code} {r.json().get('error',{}).get('code','')}")
    except Exception as e:
        check("S4-4 request", False, str(e))

print("\n[S4-5] Edge -- approve with slot_index=99")
try:
    r2 = httpx.post(f"{BASE}/schedule/online", json={}, timeout=10.0)
    if r2.status_code == 201:
        new_id = r2.json()["id"]
        r = httpx.post(
            f"{BASE}/schedule/{new_id}/approve",
            json={"slot_index": 99},
            timeout=10.0,
        )
        check("S4-5 out-of-range blocked", r.status_code in (400, 422),
              f"got {r.status_code} {r.json().get('error',{}).get('code','')}")
except Exception as e:
    check("S4-5 request", False, str(e))

# ─────────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────────
section("SUMMARY")
passed = sum(1 for _, ok, _ in results if ok)
failed = sum(1 for _, ok, _ in results if not ok)
total  = len(results)
print(f"\n  Total: {total}  |  Passed: {passed}  |  Failed: {failed}\n")
if failed:
    print("  Failed tests:")
    for name, ok, detail in results:
        if not ok:
            print(f"    [FAIL] {name}" + (f" -- {detail}" if detail else ""))
