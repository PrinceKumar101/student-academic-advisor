from datetime import date

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.engines.metrics import to_risk_inputs
from app.engines.risk_config import RiskValidationError
from app.engines.whatif import simulate
from app.models.student import Student
from app.schemas.risk import (
    ChangedFactorOut,
    WhatIfOut,
    WhatIfScoreOut,
)
from app.services.academic_data_loader import load


def run_what_if(
    db: Session,
    student: Student,
    overrides: dict[str, float | int],
    as_of: date,
) -> WhatIfOut:
    data = load(db, [student.id], as_of)[0]
    try:
        result = simulate(to_risk_inputs(data), overrides, as_of=as_of)
    except RiskValidationError as exc:
        raise AppError("VALIDATION_ERROR", str(exc), 422) from exc
    return WhatIfOut(
        current=WhatIfScoreOut(
            score=result.current.score, level=result.current.level
        ),
        simulated=WhatIfScoreOut(
            score=result.simulated.score, level=result.simulated.level
        ),
        difference=result.difference,
        changed_factors=[
            ChangedFactorOut(
                key=item.key,
                from_value=item.from_value,
                to_value=item.to_value,
                risk_from=item.risk_from,
                risk_to=item.risk_to,
                contribution_delta=item.contribution_delta,
                hypothetical=item.hypothetical,
            )
            for item in result.changed_factors
        ],
        persisted=False,
    )
