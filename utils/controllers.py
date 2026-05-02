def status_code_map(outcome_status):
    if outcome_status == "WORKOUT_NOT_FOUND":
        return 404
    elif outcome_status in {
        "WORKOUT_ALREADY_COMPLETED",
        "WORKOUT_NOT_PAUSED",
        "WORKOUT_ALREADY_PAUSED",
    }:
        return 409
    return 200
