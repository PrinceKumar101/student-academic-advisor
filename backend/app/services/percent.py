def attendance_percent(classes_held: int, classes_attended: int) -> float | None:
    if classes_held <= 0:
        return None
    return round(classes_attended / classes_held * 100, 1)
