"""
Integration test suite for Human_inthe_loop and FPT.
"""
import sqlite3
import pytest
import fpt
from fpt.events import ProjectionEvent, EventDispatcher
from fpt.adapters import SovereignLedgerAdapter
from fpt.utils.handshake import generate_handshake_message, handshake_message


def test_fpt_package_availability():
    assert hasattr(fpt, "__version__") or fpt is not None


def test_fpt_handshake_flow(tmp_path):
    log_file = str(tmp_path / "handshake.json")
    txt_file = str(tmp_path / "handshake.txt")

    payload = handshake_message("HITL-Verification", log_file=log_file)
    assert payload["status"] == "success"
    assert payload["message"] == "HITL-Verification"

    msg = generate_handshake_message(target_file=txt_file)
    assert "Proof of Presence" in msg


def test_event_dispatcher_ledger_integration(tmp_path):
    db_path = str(tmp_path / "hitl_ledger.db")
    adapter = SovereignLedgerAdapter(db_path=db_path)
    dispatcher = EventDispatcher()
    dispatcher.register(adapter)

    event = ProjectionEvent(
        timestamp_ns=1000,
        vector_dim=8,
        projection_norm=0.95,
        shadow_energy=0.05,
        action="encode",
        task_id="task_001",
        operator_signature="hitl_test"
    )
    dispatcher.dispatch(event)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    assert len(tables) > 0

    table_name = tables[0]
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    assert len(rows) == 1
    conn.close()


def test_consciousness_referee_anomaly_trap():
    from src.handshake import ConsciousnessReferee
    referee = ConsciousnessReferee(threshold=6.5)
    assert referee.validate_transition({"shadow_energy_this_step": 3.2}) is True
    assert referee.validate_transition({"shadow_energy_this_step": 7.1}) is False
