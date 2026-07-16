"""Standalone severity temporal fusion — no ROS dependency."""
from __future__ import annotations


class SeverityTemporalFusion:
    """Exponential moving average fusion of repeated patch severity estimates.

    Parameters
    ----------
    alpha : float
        Blend weight for the new observation (0 < alpha < 1).
        Smaller = smoother / slower to react.
    """

    def __init__(self, alpha: float = 0.3):
        if not 0.0 < alpha < 1.0:
            raise ValueError(f'alpha must be in (0,1), got {alpha}')
        self._alpha = alpha
        self._state: dict[str, dict] = {}

    # ------------------------------------------------------------------
    def update(self, patch_id: str, observation: dict) -> dict:
        """Incorporate a new observation and return the fused state."""
        if patch_id not in self._state:
            self._state[patch_id] = dict(observation)
            return dict(observation)
        s = self._state[patch_id]
        a = self._alpha
        s['severity'] = (1 - a) * s['severity'] + a * observation['severity']
        s['uncertainty_aleatoric'] = (
            (1 - a) * s.get('uncertainty_aleatoric', 0.0)
            + a * observation.get('uncertainty_aleatoric', 0.0)
        )
        if s['severity'] > 0.55:
            s['defect_class'] = max(
                s.get('defect_class', 0), observation.get('defect_class', 0)
            )
        return dict(s)

    def get(self, patch_id: str) -> dict | None:
        return dict(self._state[patch_id]) if patch_id in self._state else None

    def all_patches(self) -> dict:
        return {k: dict(v) for k, v in self._state.items()}

    def reset(self, patch_id: str | None = None) -> None:
        if patch_id is None:
            self._state.clear()
        else:
            self._state.pop(patch_id, None)
