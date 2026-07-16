CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS robot_telemetry (
    ts TIMESTAMPTZ NOT NULL,
    robot_id TEXT NOT NULL,
    topic TEXT NOT NULL,
    payload JSONB NOT NULL,
    level TEXT NOT NULL DEFAULT 'info',
    PRIMARY KEY (ts, robot_id, topic)
);
SELECT create_hypertable('robot_telemetry', by_range('ts'), if_not_exists => TRUE);

CREATE TABLE IF NOT EXISTS health_events (
    ts TIMESTAMPTZ NOT NULL,
    robot_id TEXT NOT NULL,
    component TEXT NOT NULL,
    state TEXT NOT NULL,
    message TEXT,
    PRIMARY KEY (ts, robot_id, component)
);
SELECT create_hypertable('health_events', by_range('ts'), if_not_exists => TRUE);
