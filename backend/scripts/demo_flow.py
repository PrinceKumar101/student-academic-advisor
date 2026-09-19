"""Print the 11-step demo story against a running API server."""

from __future__ import annotations

import argparse
import json
from datetime import date, timedelta
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from scripts.demo_advance import ADVANCE_WEEKS, advance_as_of
from scripts.seed_generator import DEFAULT_AS_OF, DEMO_PASSWORD, RAHUL_EMAIL


def _request(
    base: str,
    method: str,
    path: str,
    *,
    token: str | None = None,
    data: dict | None = None,
    form: dict | None = None,
) -> tuple[int, object]:
    headers = {"Accept": "application/json"}
    body = None
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if form is not None:
        encoded = urlencode(form).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        body = encoded
    elif data is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(data).encode()
    request = Request(base + path, data=body, headers=headers, method=method)
    try:
        with urlopen(request) as response:
            raw = response.read().decode()
            payload = json.loads(raw) if raw else None
            return response.status, payload
    except HTTPError as exc:
        raw = exc.read().decode()
        try:
            payload = json.loads(raw) if raw else {"error": raw}
        except json.JSONDecodeError:
            payload = {"error": raw}
        return exc.code, payload


def _login(base: str, email: str) -> str:
    status, payload = _request(
        base,
        "POST",
        "/api/v1/auth/login",
        form={"username": email, "password": DEMO_PASSWORD},
    )
    if status != 200:
        raise SystemExit(f"Login failed for {email}: {status} {payload}")
    assert isinstance(payload, dict)
    return str(payload["access_token"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the printed demo story.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--as-of", default=DEFAULT_AS_OF.isoformat())
    args = parser.parse_args()
    base = args.base_url.rstrip("/")
    as_of = args.as_of
    later = advance_as_of(date.fromisoformat(as_of), ADVANCE_WEEKS).isoformat()

    print("1. Login as Rahul")
    rahul = _login(base, RAHUL_EMAIL)
    print("   ok")

    print("2. Overview / risk")
    status, overview = _request(
        base, "GET", f"/api/v1/students/me/overview?as_of={as_of}", token=rahul
    )
    risk = overview["risk"] if isinstance(overview, dict) else overview
    print(f"   {status} risk={risk}")

    print("3. Trends")
    status, trends = _request(
        base, "GET", f"/api/v1/trends/me?as_of={as_of}", token=rahul
    )
    if isinstance(trends, dict):
        print(f"   {status} overall={trends['overall']['label']}")
    else:
        print(f"   {status} {trends}")

    print("4. What-if attendance 64→80")
    status, whatif = _request(
        base,
        "POST",
        f"/api/v1/risk/me/what-if?as_of={as_of}",
        token=rahul,
        data={"overrides": {"attendance_percent": 80, "internal_percent": 60}},
    )
    print(f"   {status} {whatif}")

    print("5. AI analysis (fallback if no key)")
    status, analysis = _request(
        base, "POST", "/api/v1/ai/analysis", token=rahul, data={"student_id": "me"}
    )
    if isinstance(analysis, dict):
        print(f"   {status} source={analysis.get('source')}")
    else:
        print(f"   {status} {analysis}")

    print("6. Study plan")
    exam = (date.fromisoformat(as_of) + timedelta(days=21)).isoformat()
    status, plan = _request(
        base,
        "POST",
        "/api/v1/study-plans",
        token=rahul,
        data={"exam_date": exam, "available_hours_per_day": 3, "subject_ids": []},
    )
    if isinstance(plan, dict):
        count = len(plan.get("items", []))
        print(f"   {status} items={count} source={plan.get('source')}")
    else:
        print(f"   {status} {plan}")

    print("7. Teacher login and HIGH filter")
    teacher = _login(base, "teacher1@demo.edu")
    status, listed = _request(
        base,
        "GET",
        f"/api/v1/teacher/students?risk_level=HIGH&as_of={as_of}&search=Rahul",
        token=teacher,
    )
    total = listed.get("total") if isinstance(listed, dict) else listed
    print(f"   {status} total={total}")

    print("8. Create intervention")
    student_id = overview["student_id"] if isinstance(overview, dict) else None
    status, intervention = _request(
        base,
        "POST",
        f"/api/v1/interventions?as_of={as_of}",
        token=teacher,
        data={"student_id": student_id, "title": "Attendance recovery plan"},
    )
    print(f"   {status} {intervention}")

    print("9. Advance records (run scripts.demo_advance separately if needed)")
    print(f"   expected later as_of {later}")

    if isinstance(intervention, dict) and "id" in intervention:
        print("10. Progress after advance (if records already added)")
        status, progress = _request(
            base,
            "GET",
            f"/api/v1/interventions/{intervention['id']}/progress?as_of={later}",
            token=teacher,
        )
        print(f"   {status} {progress}")

    print("11. Done")


if __name__ == "__main__":
    main()
