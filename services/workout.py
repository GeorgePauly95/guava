from models import PauseAndResumeLogs, Workouts


def check_log_conflict(log, time):
    if log["paused_at"] < time and log["resumed_at"] > time:
        return True
    return False


def pause_workout(workout_id, time):
    logs = PauseAndResumeLogs.get_logs(workout_id)
    active_sessions = [
        log
        for log in logs
        if log["resumed_at"] is None or check_log_conflict(log, time)
    ]
    if len(active_sessions) != 0:
        return {
            "success": False,
            "error_message": f"Workout with id: {workout_id} has already been paused.",
            "outcome_status": "WORKOUT_ALREADY_PAUSED",
        }
    PauseAndResumeLogs.pause_workout(workout_id, time)
    return {"success": True, "outcome_status": "WORKOUT_PAUSED"}


def resume_workout(workout_id, time):
    logs = PauseAndResumeLogs.get_logs(workout_id)
    valid_ids = [
        log["id"]
        for log in logs
        if log["resumed_at"] is None and time > log["paused_at"]
    ]
    if valid_ids == []:
        return {
            "success": False,
            "error_message": f"Workout with id: {workout_id} is not currently paused.",
            "outcome_status": "WORKOUT_NOT_PAUSED",
        }

    for id in valid_ids:
        PauseAndResumeLogs.resume_workout(id, time)
    return {"success": True, "outcome_status": "WORKOUT_RESUMED"}


def stop_workout(workout_id, workout, time):
    if workout["stopped_at"] is not None:
        return {
            "success": False,
            "error_message": f"Workout with id: {workout_id} has already been stopped.",
            "outcome_status": "WORKOUT_ALREADY_COMPLETED",
        }
    logs = PauseAndResumeLogs.get_logs(workout_id)
    for log in logs:
        if log["resumed_at"] is None and log["paused_at"] > time:
            return {
                "success": False,
                "error_message": f"Workout with id: {workout_id} cannot be stopped.",
                "outcome_status": "WORKOUT_NOT_STOPPED",
            }
        elif log["resumed_at"] is not None and log["resumed_at"] > time:
            return {
                "success": False,
                "error_message": f"Workout with id: {workout_id} cannot be stopped.",
                "outcome_status": "WORKOUT_NOT_STOPPED",
            }
    Workouts.stop_workout(workout_id, time)
    return {"success": True, "outcome_status": "WORKOUT_STOPPED"}


def route_modify_workout(workout_id, status, time):
    workout = Workouts.get_workout(workout_id)

    if workout is None or workout["started_at"] > time:
        return {
            "success": False,
            "error_message": f"Workout with id: {workout_id} doesn't exist.",
            "outcome_status": "WORKOUT_NOT_FOUND",
        }
    elif workout["stopped_at"] is not None and workout["stopped_at"] < time:
        return {
            "success": False,
            "error_message": f"Workout with id: {workout_id} is already stopped.",
            "outcome_status": "WORKOUT_ALREADY_COMPLETED",
        }
    elif status == "stop":
        return stop_workout(workout_id, workout, time)
    elif status == "pause":
        return pause_workout(workout_id, time)
    else:
        return resume_workout(workout_id, time)
