"""
One-shot script to create minimal test data for smoke testing.
Creates: 1 client, 1 signed contract, 1 event.

Uses raw SQL to bypass permission checks (this is a setup script,
not production code).

Run once: python setup_smoke_data.py
Exit codes: 0 = success, 1 = failure
"""

import sys
from utils.open_db_connection import get_db_connection

def step_ok(msg):
    print(f"  ✅ {msg}")

def step_fail(msg):
    print(f"  ❌ {msg}")
    print("\n" + "=" * 50)
    print("🔴 SETUP FAILED — DO NOT PROCEED TO SMOKE TEST")
    print("=" * 50)
    sys.exit(1)

def section(title):
    print(f"\n── {title} ──")

def fetch_one(sql, params=None):
    """Execute a SELECT and return one row, or None."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.fetchone()
    finally:
        conn.close()

def execute_insert(sql, params):
    """Execute an INSERT and return the lastrowid."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            conn.commit()
            return cur.lastrowid
    finally:
        conn.close()

def main():
    print("=" * 50)
    print("  SMOKE TEST DATA SETUP")
    print("=" * 50)

    # ----------------------------------------------------------
    # STEP 0: Verify collaborators exist
    # ----------------------------------------------------------
    section("Step 0/4: Verifying collaborators")

    try:
        rows = []
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT id, username FROM collaborators")
                rows = cur.fetchall()
        finally:
            conn.close()
        step_ok(f"Found {len(rows)} collaborator(s) in DB")
    except Exception as e:
        step_fail(f"Cannot read collaborators from DB: {e}")
        return

    hubert_id = None
    jobert_id = None

    for r in rows:
        if r[1] == "hubert":
            hubert_id = r[0]
        elif r[1] == "jobhert":
            jobert_id = r[0]

    if not jobert_id:
        step_fail("'jobhert' (Commercial) not found in DB — cannot proceed")
        return
    step_ok(f"jobhert found: ID {jobert_id}")

    if not hubert_id:
        step_fail("'hubert' (Gestion) not found in DB — cannot proceed")
        return
    step_ok(f"hubert found: ID {hubert_id}")

    # ----------------------------------------------------------
    # STEP 1: Create 1 client
    # ----------------------------------------------------------
    section("Step 1/4: Creating client")

    try:
        client_id = execute_insert(
            """INSERT INTO clients (full_name, email, phone, company_name, creation_date, last_update_date, commercial_contact)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            ("Jean Demo", "jean.demo@test.com", "+33600000001",
             "Demo SAS", "2025-01-15", "2025-01-15", jobert_id),
        )
        step_ok(f"Client created: ID {client_id}")
    except Exception as e:
        step_fail(f"INSERT client failed: {e}")
        return

    # Read back to verify
    row = fetch_one("SELECT full_name, last_update_date FROM clients WHERE id = %s", (client_id,))
    if not row:
        step_fail(f"Client ID {client_id} not found after insertion")
        return
    step_ok(f"Client verified in DB: {row[0]} (last_update: {row[1]})")
    
    # ----------------------------------------------------------
    # STEP 2: Create 1 signed contract
    # ----------------------------------------------------------
    section("Step 2/4: Creating contract")

    try:
        contract_id = execute_insert(
            """INSERT INTO contracts (total_amount, remaining_amount, creation_date, is_signed, client_id, commercial_contact_id)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (10000.0, 5000.0, "2025-01-20", True, client_id, jobert_id),
        )
        step_ok(f"Contract created: ID {contract_id}")
    except Exception as e:
        step_fail(f"INSERT contract failed: {e}")
        return

    # Read back and verify is_signed=True
    row = fetch_one("SELECT is_signed FROM contracts WHERE id = %s", (contract_id,))
    if not row:
        step_fail(f"Contract ID {contract_id} not found after insertion")
        return
    if not row[0]:
        step_fail(f"Contract ID {contract_id} exists but is_signed=False")
        return
    step_ok("Contract verified in DB (signed=True)")

    # ----------------------------------------------------------
    # STEP 3: Create 1 event
    # ----------------------------------------------------------
    section("Step 3/4: Creating event")

    try:
        event_id = execute_insert(
            """INSERT INTO events (name, client_name, client_contact, date_start, date_end,
                                   location, attendees, notes, contract_id, support_contact)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            ("Product Launch Party", "Jean Demo", "jean.demo@test.com | +33600000001",
             "2025-06-15", "2025-06-15", "Paris Convention Center", 200,
             "Annual product launch", contract_id, hubert_id),
        )
        step_ok(f"Event created: ID {event_id}")
    except Exception as e:
        step_fail(f"INSERT event failed: {e}")
        return

    # Read back to verify
    row = fetch_one("SELECT name FROM events WHERE id = %s", (event_id,))
    if not row:
        step_fail(f"Event ID {event_id} not found after insertion")
        return
    step_ok(f"Event verified in DB: {row[0]}")

    # ----------------------------------------------------------
    # STEP 4: Final summary
    # ----------------------------------------------------------
    section("Step 4/4: Summary")

    print(f"""
  Collaborators (pre-existing):
    • hubert (Gestion)     → ID {hubert_id}
    • jobhert (Commercial) → ID {jobert_id}

  Created data:
    • Client   → ID {client_id}  (Jean Demo / Demo SAS)
    • Contract → ID {contract_id}  (10 000€, signed, 5 000€ remaining)
    • Event    → ID {event_id}  (Product Launch Party)
""")

    print("=" * 50)
    print("🟢 SETUP COMPLETE — READY FOR SMOKE TEST")
    print("=" * 50)
    print("Next: python -m app.cli.cli start")
    sys.exit(0)

if __name__ == "__main__":
    main()