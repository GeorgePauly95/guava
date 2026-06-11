from .engine import engine
from sqlalchemy import text, bindparam


def get_metrics(user_ids):
    sql = text("""
    WITH user_ids AS (
    SELECT
        id AS user_id
    FROM
        "user"
    WHERE id in :user_ids
    ),
    user_workouts AS (
    SELECT
        id AS workout_id,
        user_ids.user_id,
        started_at AS START,
        stopped_at AS stop
    FROM
        workout
    INNER JOIN
        user_ids
    ON
        user_ids.user_id = workout.user_id),
    workout_logs AS (
    SELECT
        workout.id AS workout_id,
        started_at,
        stopped_at,
        paused_at,
        resumed_at
    FROM
        workout
    INNER JOIN
        pause_resume_logs
    ON
        workout.id = pause_resume_logs.workout_id),
    workout_intervals AS (
    SELECT
        wlg.workout_id,
        wlg.resumed_at AS START,
        COALESCE(LEAD(wlg.paused_at) OVER (PARTITION BY wlg.workout_id ORDER BY wlg.paused_at), wlg.stopped_at) AS stop
    FROM
        workout_logs wlg
    UNION
    SELECT
        wlg.workout_id,
        min(wlg.started_at) AS START,
        min(wlg.paused_at) AS stop
    FROM
        workout_logs wlg
    GROUP BY
        wlg.workout_id),
    workout_locations AS (
    SELECT
        LOCATION.workout_id,
        LOCATION.id AS location_id,
        latitude,
        longitude,
        time
    FROM
        LOCATION
    INNER JOIN workout_intervals ON
        workout_intervals.workout_id = LOCATION.workout_id
    WHERE
        time BETWEEN START AND stop
    ),
    workout_locations_pairs AS (
    SELECT
        workout_id,
        location_id AS location_id_1,
        LAG(location_id) OVER (PARTITION BY workout_id) AS location_id_2,
        latitude AS latitude_1,
        LAG(latitude) OVER (PARTITION BY workout_id) AS latitude_2, 
        longitude AS longitude_1,
        LAG(longitude) OVER (PARTITION BY workout_id) AS longitude_2,
        time AS time_1,
        LAG(time) OVER (PARTITION BY workout_id) AS time_2
    FROM
        workout_locations
    ),
    workout_metrics AS (
    SELECT
        workout_id,
        haversine_distance(latitude_1, longitude_1, latitude_2, longitude_2) AS distance,
        EXTRACT(EPOCH FROM (time_1 - time_2)) AS time
    FROM
        workout_locations_pairs
    )
    SELECT SUM(distance) AS distance FROM workout_metrics;""")
    sql = sql.bindparams(bindparam("user_ids", expanding=True))
    with engine.begin() as connection:
        metrics = connection.execute(sql, {"user_ids": user_ids})
        metrics = [metric._mapping for metric in metrics]
        return metrics
