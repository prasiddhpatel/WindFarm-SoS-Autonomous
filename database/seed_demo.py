#!/usr/bin/env python3
"""
Seed script: inserts 2 demo turbines and 6 blade patches.
Run after docker compose up: python3 database/seed_demo.py
"""
import os, uuid
import psycopg

DSN = os.environ.get(
    'DATABASE_URL',
    'postgresql://sos:sos_password@localhost:5432/windfarm_sos'
)

TURBINES = [
    dict(id=str(uuid.uuid4()), turbine_code='WTG-01', name='Turbine 01',
         latitude=54.5260, longitude=3.3228, blade_length_m=63.0, hub_height_m=90.0),
    dict(id=str(uuid.uuid4()), turbine_code='WTG-02', name='Turbine 02',
         latitude=54.5280, longitude=3.3265, blade_length_m=63.0, hub_height_m=90.0),
]

PATCHES = [
    dict(blade_index=0, chord_pos=0.3, span_pos=0.55, defect_class=2,
         severity=0.62, severity_cov=0.04, rul_days=120.0, recommendation='schedule_nde'),
    dict(blade_index=1, chord_pos=0.5, span_pos=0.70, defect_class=1,
         severity=0.31, severity_cov=0.06, rul_days=310.0, recommendation='monitor'),
    dict(blade_index=2, chord_pos=0.6, span_pos=0.40, defect_class=3,
         severity=0.85, severity_cov=0.03, rul_days=45.0,  recommendation='urgent_repair'),
]


def main():
    with psycopg.connect(DSN) as conn:
        for t in TURBINES:
            conn.execute("""
                INSERT INTO turbines
                    (id, turbine_code, name, latitude, longitude, blade_length_m, hub_height_m)
                VALUES
                    (%(id)s, %(turbine_code)s, %(name)s, %(latitude)s, %(longitude)s,
                     %(blade_length_m)s, %(hub_height_m)s)
                ON CONFLICT (turbine_code) DO NOTHING;
            """, t)

        for tcode in [t['turbine_code'] for t in TURBINES]:
            row = conn.execute(
                "SELECT id FROM turbines WHERE turbine_code=%s", (tcode,)
            ).fetchone()
            if not row:
                continue
            tid = str(row[0])
            for p in PATCHES:
                conn.execute("""
                    INSERT INTO blade_patches
                        (turbine_id, blade_index, chord_pos, span_pos,
                         defect_class, severity, severity_cov, rul_days, recommendation)
                    VALUES
                        (%(turbine_id)s, %(blade_index)s, %(chord_pos)s, %(span_pos)s,
                         %(defect_class)s, %(severity)s, %(severity_cov)s,
                         %(rul_days)s, %(recommendation)s)
                    ON CONFLICT (turbine_id, blade_index, chord_pos, span_pos) DO NOTHING;
                """, {**p, 'turbine_id': tid})
        conn.commit()
    print('Seed complete: 2 turbines, 6 patches inserted.')


if __name__ == '__main__':
    main()
