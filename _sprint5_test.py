"""
Sprint 5 -- MOM Summarization (FR-05) + Follow-up Email (FR-06) test
MockLLMClient + MockGraphClient only.
"""
import io
import httpx

BASE = "http://localhost:8000"
results = []

TRANSCRIPT_TEXT = b"""
Meeting Transcript - Q3 Partnership Review
Date: 2026-06-15

Alice: Let's start with the pricing proposal. Sales team, any update?
Bob: Yes, we have a revised proposal ready. We agreed on a 15% discount for the first year.
Alice: Great. We also need to schedule a technical integration session.
Bob: Agreed. BrSE team will handle that. Target is before end of June.
Alice: One more thing -- customer requested a pilot environment by June 25.
Bob: Noted. DevOps will provision it.
Alice: Anything else? Ok, let's wrap up.
"""

MEETING_ID = None
MINUTES_ID = None
EMAIL_ID = None
EMAIL_ID2 = None  # for edge cases


def check(name, cond, detail=""):
    results.append((name, cond, detail))
    tag = "PASS" if cond else "FAIL"
    safe_detail = str(detail).encode("ascii", errors="replace").decode("ascii")
    print(f"  [{tag}] {name}" + (f"  -- {safe_detail}" if safe_detail else ""))
    return cond


def section(title):
    print(f"\n{'='*60}\n  {title}\n{'='*60}")


# ── S5-1: POST /meetings/mom ─────────────────────────────────────
section("S5-1  POST /meetings/mom  (mock LLM, transcript upload)")
try:
    r = httpx.post(
        f"{BASE}/meetings/mom",
        files={"file": ("transcript.txt", io.BytesIO(TRANSCRIPT_TEXT), "text/plain")},
        timeout=20,
    )
    b = r.json()
    check("status=201", r.status_code == 201, f"got {r.status_code}")
    if r.status_code == 201:
        MEETING_ID = b["meeting_id"]
        MINUTES_ID = b["id"]
        check("status=draft", b.get("status") == "draft", b.get("status"))
        check("summary not empty", bool(b.get("summary")), repr(b.get("summary"))[:60])
        check("action_items present", len(b.get("action_items", [])) > 0,
              f"count={len(b.get('action_items', []))}")
        check("meeting_id returned", MEETING_ID is not None)
        print(f"\n  Mock MOM summary (first 80 chars):")
        print(f"    {str(b.get('summary', ''))[:80].encode('ascii', errors='replace').decode('ascii')}")
        print(f"\n  Action items ({len(b.get('action_items', []))}):")
        for a in b.get("action_items", []):
            line = f"    [{a.get('owner','?')} / {a.get('deadline','?')}] {a.get('description','')}"
            print(line.encode("ascii", errors="replace").decode("ascii"))
except Exception as e:
    check("request", False, str(e))

# ── S5-2: GET /meetings/{id}/mom ─────────────────────────────────
section("S5-2  GET /meetings/{id}/mom")
if MEETING_ID:
    try:
        r = httpx.get(f"{BASE}/meetings/{MEETING_ID}/mom", timeout=10)
        b = r.json()
        check("status=200", r.status_code == 200, f"got {r.status_code}")
        check("meeting_id matches", b.get("meeting_id") == MEETING_ID)
        check("id matches", b.get("id") == MINUTES_ID)
        check("status=draft", b.get("status") == "draft")
    except Exception as e:
        check("request", False, str(e))

# ── S5-3: PATCH /meetings/{id}/mom ───────────────────────────────
section("S5-3  PATCH /meetings/{id}/mom  (edit summary + action items)")
if MEETING_ID:
    try:
        patch_body = {
            "summary": "Updated: Q3 partnership scope confirmed with phased rollout.",
            "action_items": [
                {"description": "Send revised pricing proposal", "owner": "Sales", "deadline": "2026-06-20"},
                {"description": "Schedule technical integration call", "owner": "BrSE", "deadline": "2026-06-25"},
                {"description": "Provision pilot environment", "owner": "DevOps", "deadline": "2026-06-25"},
            ],
        }
        r = httpx.patch(f"{BASE}/meetings/{MEETING_ID}/mom", json=patch_body, timeout=10)
        b = r.json()
        check("status=200", r.status_code == 200, f"got {r.status_code}")
        if r.status_code == 200:
            check("summary updated", "Updated:" in (b.get("summary") or ""))
            check("action_items=3", len(b.get("action_items", [])) == 3,
                  f"got {len(b.get('action_items', []))}")
    except Exception as e:
        check("request", False, str(e))

# ── S5-4: Approve MOM ────────────────────────────────────────────
section("S5-4  POST /meetings/{id}/mom/approve")
if MEETING_ID:
    try:
        r = httpx.post(f"{BASE}/meetings/{MEETING_ID}/mom/approve", timeout=10)
        b = r.json()
        check("status=200", r.status_code == 200, f"got {r.status_code}")
        if r.status_code == 200:
            check("status=approved", b.get("status") == "approved")
            check("action_items still present", len(b.get("action_items", [])) == 3)
    except Exception as e:
        check("request", False, str(e))

# ── S5-5: Edge — approve MOM with no action items ────────────────
section("S5-5  Edge: approve MOM with no action items  (separate meeting)")
try:
    # Create a bare MOM with minimal transcript
    r2 = httpx.post(
        f"{BASE}/meetings/mom",
        files={"file": ("t.txt", io.BytesIO(b"Short meeting. No actions."), "text/plain")},
        timeout=20,
    )
    if r2.status_code == 201:
        bare_meeting_id = r2.json()["meeting_id"]
        # Clear action items via PATCH
        httpx.patch(
            f"{BASE}/meetings/{bare_meeting_id}/mom",
            json={"summary": "Short.", "action_items": []},
            timeout=10,
        )
        # Now try to approve
        r3 = httpx.post(f"{BASE}/meetings/{bare_meeting_id}/mom/approve", timeout=10)
        check("blocked 400/422", r3.status_code in (400, 422),
              f"got {r3.status_code} {r3.json().get('error', {}).get('code', '')}")
    else:
        check("setup failed", False, f"setup got {r2.status_code}")
except Exception as e:
    check("request", False, str(e))

# ── S5-6: Edge — double approve ──────────────────────────────────
section("S5-6  Edge: double-approve same MOM  (should fail)")
if MEETING_ID:
    try:
        r = httpx.post(f"{BASE}/meetings/{MEETING_ID}/mom/approve", timeout=10)
        b = r.json()
        check("blocked 400/422", r.status_code in (400, 422),
              f"got {r.status_code} {b.get('error', {}).get('code', '')}")
    except Exception as e:
        check("request", False, str(e))

# ── S5-7: Edge — edit after approved ─────────────────────────────
section("S5-7  Edge: PATCH MOM after approved  (should fail)")
if MEETING_ID:
    try:
        r = httpx.patch(
            f"{BASE}/meetings/{MEETING_ID}/mom",
            json={"summary": "Trying to edit after approval"},
            timeout=10,
        )
        b = r.json()
        check("blocked 400/422", r.status_code in (400, 422),
              f"got {r.status_code} {b.get('error', {}).get('code', '')}")
    except Exception as e:
        check("request", False, str(e))

# ── S5-8: POST /emails/follow-up ─────────────────────────────────
section("S5-8  POST /emails/follow-up  (from approved MOM)")
if MEETING_ID:
    try:
        r = httpx.post(
            f"{BASE}/emails/follow-up",
            json={"meeting_id": MEETING_ID},
            timeout=20,
        )
        b = r.json()
        check("status=201", r.status_code == 201, f"got {r.status_code}")
        if r.status_code == 201:
            EMAIL_ID = b["id"]
            check("type=follow_up", b.get("type") == "follow_up")
            check("status=draft", b.get("status") == "draft")
            check("subject not empty", bool(b.get("subject")))
            check("body not empty", bool(b.get("body")))
            subj = str(b.get("subject", "")).encode("ascii", errors="replace").decode("ascii")
            print(f"\n  Mock follow-up subject: {subj}")
            body_preview = str(b.get("body", ""))[:80].encode("ascii", errors="replace").decode("ascii")
            print(f"  Body preview: {body_preview}...")
    except Exception as e:
        check("request", False, str(e))

# ── S5-9: GET /emails/{id} ───────────────────────────────────────
section("S5-9  GET /emails/{id}  (follow-up draft)")
if EMAIL_ID:
    try:
        r = httpx.get(f"{BASE}/emails/{EMAIL_ID}", timeout=10)
        b = r.json()
        check("status=200", r.status_code == 200, f"got {r.status_code}")
        check("id matches", b.get("id") == EMAIL_ID)
        check("meeting_id matches", b.get("meeting_id") == MEETING_ID)
        check("status=draft", b.get("status") == "draft")
    except Exception as e:
        check("request", False, str(e))

# ── S5-10: PATCH /emails/{id} ────────────────────────────────────
section("S5-10  PATCH /emails/{id}  (edit draft)")
if EMAIL_ID:
    try:
        r = httpx.patch(
            f"{BASE}/emails/{EMAIL_ID}",
            json={"subject": "Follow-up: Revised Q3 Partnership", "body": "Updated body content."},
            timeout=10,
        )
        b = r.json()
        check("status=200", r.status_code == 200, f"got {r.status_code}")
        if r.status_code == 200:
            check("subject updated", b.get("subject") == "Follow-up: Revised Q3 Partnership")
            check("body updated", b.get("body") == "Updated body content.")
    except Exception as e:
        check("request", False, str(e))

# ── S5-11: Submit → in_review ────────────────────────────────────
section("S5-11  POST /emails/{id}/submit  (draft -> in_review)")
if EMAIL_ID:
    try:
        r = httpx.post(f"{BASE}/emails/{EMAIL_ID}/submit", timeout=10)
        b = r.json()
        check("status=200", r.status_code == 200, f"got {r.status_code}")
        check("status=in_review", b.get("status") == "in_review")
    except Exception as e:
        check("request", False, str(e))

# ── S5-12: Approve → approved ────────────────────────────────────
section("S5-12  POST /emails/{id}/approve  (in_review -> approved)")
if EMAIL_ID:
    try:
        r = httpx.post(f"{BASE}/emails/{EMAIL_ID}/approve", timeout=10)
        b = r.json()
        check("status=200", r.status_code == 200, f"got {r.status_code}")
        check("status=approved", b.get("status") == "approved")
    except Exception as e:
        check("request", False, str(e))

# ── S5-13: Send → sent ───────────────────────────────────────────
section("S5-13  POST /emails/{id}/send  (approved -> sent, no real email)")
if EMAIL_ID:
    try:
        r = httpx.post(f"{BASE}/emails/{EMAIL_ID}/send", timeout=10)
        b = r.json()
        check("status=200", r.status_code == 200, f"got {r.status_code}")
        check("status=sent", b.get("status") == "sent")
        print("  [Security] send only marks status -- no real email dispatched (MockLLMClient)")
    except Exception as e:
        check("request", False, str(e))

# ── S5-14: Edge — follow-up from non-approved MOM ────────────────
section("S5-14  Edge: follow-up from non-approved MOM  (should fail)")
try:
    # Create a fresh meeting/MOM (status=draft)
    r2 = httpx.post(
        f"{BASE}/meetings/mom",
        files={"file": ("t2.txt", io.BytesIO(b"Draft meeting notes."), "text/plain")},
        timeout=20,
    )
    if r2.status_code == 201:
        draft_meeting_id = r2.json()["meeting_id"]
        r3 = httpx.post(
            f"{BASE}/emails/follow-up",
            json={"meeting_id": draft_meeting_id},
            timeout=10,
        )
        b3 = r3.json()
        check("blocked 400/422", r3.status_code in (400, 422),
              f"got {r3.status_code} {b3.get('error', {}).get('code', '')}")
    else:
        check("setup failed", False, f"setup got {r2.status_code}")
except Exception as e:
    check("request", False, str(e))

# ── S5-15: Edge — send twice ─────────────────────────────────────
section("S5-15  Edge: send already-sent email  (should fail)")
if EMAIL_ID:
    try:
        r = httpx.post(f"{BASE}/emails/{EMAIL_ID}/send", timeout=10)
        b = r.json()
        check("blocked 400/422", r.status_code in (400, 422),
              f"got {r.status_code} {b.get('error', {}).get('code', '')}")
    except Exception as e:
        check("request", False, str(e))

# ── S5-16: Edge — edit after approved/sent ───────────────────────
section("S5-16  Edge: PATCH email after sent  (should fail)")
if EMAIL_ID:
    try:
        r = httpx.patch(
            f"{BASE}/emails/{EMAIL_ID}",
            json={"subject": "Trying to edit sent email"},
            timeout=10,
        )
        b = r.json()
        check("blocked 400/422", r.status_code in (400, 422),
              f"got {r.status_code} {b.get('error', {}).get('code', '')}")
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
