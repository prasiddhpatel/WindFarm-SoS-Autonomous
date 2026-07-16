DROP EXTENSION IF EXISTS postgis CASCADE;
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS turbines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    turbine_code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    utm_x DOUBLE PRECISION,
    utm_y DOUBLE PRECISION,
    blade_length_m DOUBLE PRECISION NOT NULL,
    hub_height_m DOUBLE PRECISION NOT NULL,
    geofence GEOMETRY(POLYGON, 4326),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS blade_patches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    turbine_id UUID NOT NULL REFERENCES turbines(id) ON DELETE CASCADE,
    blade_index SMALLINT NOT NULL CHECK (blade_index BETWEEN 0 AND 2),
    chord_pos REAL NOT NULL CHECK (chord_pos >= 0 AND chord_pos <= 1),
    span_pos REAL NOT NULL CHECK (span_pos >= 0 AND span_pos <= 1),
    blade_frame_point GEOMETRY(POINTZ, 4979),
    world_point GEOMETRY(POINTZ, 4326),
    defect_class SMALLINT NOT NULL DEFAULT 0,
    severity REAL NOT NULL DEFAULT 0.0,
    severity_cov REAL NOT NULL DEFAULT 0.0,
    rul_cycles DOUBLE PRECISION,
    rul_days DOUBLE PRECISION,
    recommendation TEXT,
    UNIQUE (turbine_id, blade_index, chord_pos, span_pos)
);

CREATE TABLE IF NOT EXISTS inspections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    turbine_id UUID NOT NULL REFERENCES turbines(id) ON DELETE CASCADE,
    robot_id TEXT NOT NULL,
    inspection_type TEXT NOT NULL CHECK (inspection_type IN ('aerial_triage','contact_nde','manual_validation')),
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'queued',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS patch_observations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    inspection_id UUID NOT NULL REFERENCES inspections(id) ON DELETE CASCADE,
    patch_id UUID REFERENCES blade_patches(id) ON DELETE SET NULL,
    source TEXT NOT NULL CHECK (source IN ('uav_rgb_lwir','uav_lidar','crawler_ut','crawler_ae','human')),
    defect_class SMALLINT,
    severity REAL,
    severity_aleatoric REAL,
    severity_epistemic REAL,
    ut_depth_m REAL,
    ut_extent_m REAL,
    uncertainty REAL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    observed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS fleet_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_type TEXT NOT NULL,
    robot_id TEXT,
    turbine_id UUID REFERENCES turbines(id) ON DELETE SET NULL,
    patch_id UUID REFERENCES blade_patches(id) ON DELETE SET NULL,
    reward DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    execution_cost DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    utility DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    state TEXT NOT NULL DEFAULT 'queued',
    constraints JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_turbines_geofence ON turbines USING GIST (geofence);
CREATE INDEX IF NOT EXISTS idx_blade_patches_world_point ON blade_patches USING GIST (world_point);
CREATE INDEX IF NOT EXISTS idx_patch_observations_observed_at ON patch_observations (observed_at DESC);
CREATE INDEX IF NOT EXISTS idx_fleet_tasks_state ON fleet_tasks (state, created_at DESC);
