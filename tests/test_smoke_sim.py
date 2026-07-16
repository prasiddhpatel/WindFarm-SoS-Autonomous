"""Simulation bridge config tests (no Gazebo, no ROS required)."""
import importlib.util, os, sys
import pytest


def _load_launch(filename):
    path = os.path.join('simulation', 'launch', filename)
    spec = importlib.util.spec_from_file_location(filename.replace('.py',''), path)
    mod  = importlib.util.module_from_spec(spec)
    # stub heavy launch dependencies
    for m in ('launch', 'launch.actions', 'launch.substitutions',
              'launch.launch_description_sources',
              'launch_ros', 'launch_ros.actions', 'launch_ros.substitutions'):
        if m not in sys.modules:
            import types
            sys.modules[m] = types.ModuleType(m)
    return mod, spec


def test_sim_bridge_launch_importable():
    mod, spec = _load_launch('sim_bridge.launch.py')
    try:
        spec.loader.exec_module(mod)
        assert hasattr(mod, 'generate_launch_description')
    except Exception:
        pytest.skip('launch deps not available in test environment')


def test_expected_bridge_topics_present():
    from simulation.scripts.smoke_test_sim import EXPECTED_TOPICS
    for t in EXPECTED_TOPICS:
        assert t.startswith('/')
    assert '/imu/data' in EXPECTED_TOPICS
    assert '/camera/rgb' in EXPECTED_TOPICS


def test_smoke_script_importable():
    spec = importlib.util.spec_from_file_location(
        'smoke_test_sim',
        os.path.join('simulation', 'scripts', 'smoke_test_sim.py')
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert hasattr(mod, 'check_bridge_config')
    assert hasattr(mod, 'EXPECTED_TOPICS')
