"""
ASAC subgroup and calibration auditing workbench.

Version: 0.2.0
Author: Thomas Jabiya Oriya

Purpose
-------
Minimal research reference implementation for subgroup performance
and probability-calibration auditing within the proposed Age- and
Site-Aware Calibration (ASAC) framework.

Scope
-----
This module does NOT implement the complete ASAC framework.
It provides selected auditing components only:

- subgroup classification metrics
- expected calibration error (ECE)
- Brier score
- subgroup temperature scaling
- explicit fallback handling for small subgroups
- a synthetic demonstration

Research status
---------------
Research/audit use only.
Not clinically validated.
Not intended for clinical diagnosis or clinical decision-making.

The minimum subgroup size used by default is an engineering safeguard,
not a universal statistical threshold.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

import numpy as np
from scipy.special import expit
from scipy.optimize import minimize_scalar


VERSION = "0.2.0"


def _safe_divide(
    numerator: float,
    denominator: float,
) -> float:
    """Return zero when the denominator is zero."""
    if denominator == 0:
        return 0.0
    return float(numerator / denominator)


def _validate_binary_inputs(
    y_true: np.ndarray,
    y_prob: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """Validate and normalize binary outcomes and probabilities."""
    y_true = np.asarray(y_true, dtype=int)
    y_prob = np.asarray(y_prob, dtype=float)

    if y_true.ndim != 1 or y_prob.ndim != 1:
        raise ValueError("y_true and y_prob must be one-dimensional.")

    if len(y_true) != len(y_prob):
        raise ValueError("y_true and y_prob must have equal length.")

    if len(y_true) == 0:
        raise ValueError("Inputs must contain at least one observation.")

    if not np.all(np.isin(y_true, [0, 1])):
        raise ValueError("y_true must contain only 0 and 1.")

    if not np.all(np.isfinite(y_prob)):
        raise ValueError("y_prob must contain only finite values.")

    if np.any((y_prob < 0) | (y_prob > 1)):
        raise ValueError("y_prob must lie between 0 and 1.")

    return y_true, y_prob


def expected_calibration_error(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    n_bins: int = 10,
) -> float:
    """
    Calculate expected calibration error (ECE).

    The final bin includes probability 1.0.

    Parameters
    ----------
    y_true:
        Binary observed outcomes.
    y_prob:
        Predicted probabilities.
    n_bins:
        Number of equal-width probability bins.

    Returns
    -------
    float
        Expected calibration error.
    """
    y_true, y_prob = _validate_binary_inputs(y_true, y_prob)

    if n_bins < 1:
        raise ValueError("n_bins must be at least 1.")

    edges = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    n = len(y_true)

    for i in range(n_bins):
        lower = edges[i]
        upper = edges[i + 1]

        if i == n_bins - 1:
            mask = (y_prob >= lower) & (y_prob <= upper)
        else:
            mask = (y_prob >= lower) & (y_prob < upper)

        if not np.any(mask):
            continue

        observed = np.mean(y_true[mask])
        predicted = np.mean(y_prob[mask])

        ece += np.sum(mask) / n * abs(observed - predicted)

    return float(ece)


def brier_score(
    y_true: np.ndarray,
    y_prob: np.ndarray,
) -> float:
    """Calculate the binary Brier score."""
    y_true, y_prob = _validate_binary_inputs(y_true, y_prob)
    return float(np.mean((y_prob - y_true) ** 2))


def classification_metrics(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    threshold: float = 0.5,
) -> Dict[str, float]:
    """
    Calculate binary classification and calibration metrics.

    Returns sensitivity, specificity, precision, F1, ECE and Brier score.
    Metrics involving an absent class are reported as 0 rather than
    silently omitted.
    """
    y_true, y_prob = _validate_binary_inputs(y_true, y_prob)

    if not 0 < threshold < 1:
        raise ValueError("threshold must be between 0 and 1.")

    y_pred = (y_prob >= threshold).astype(int)

    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))

    sensitivity = _safe_divide(tp, tp + fn)
    specificity = _safe_divide(tn, tn + fp)
    precision = _safe_divide(tp, tp + fp)

    f1 = _safe_divide(
        2 * precision * sensitivity,
        precision + sensitivity,
    )

    return {
        "n": float(len(y_true)),
        "positives": float(np.sum(y_true == 1)),
        "negatives": float(np.sum(y_true == 0)),
        "sensitivity": sensitivity,
        "specificity": specificity,
        "precision": precision,
        "f1": f1,
        "ece": expected_calibration_error(y_true, y_prob),
        "brier": brier_score(y_true, y_prob),
    }


def audit_fairness(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    subgroup: np.ndarray,
    threshold: float = 0.5,
    n_bins: int = 10,
    min_group_n: int = 30,
) -> Dict[str, Dict[str, float]]:
    """
    Audit performance and calibration across subgroups.

    Parameters
    ----------
    y_true:
        Binary outcomes.
    y_prob:
        Predicted probabilities.
    subgroup:
        Subgroup label for each observation.
    threshold:
        Classification threshold.
    n_bins:
        Number of ECE bins.
    min_group_n:
        Engineering safeguard for reporting subgroup results.

    Notes
    -----
    Groups below min_group_n are still reported. They are flagged as
    small rather than silently excluded.
    """
    y_true, y_prob = _validate_binary_inputs(y_true, y_prob)
    subgroup = np.asarray(subgroup)

    if subgroup.ndim != 1 or len(subgroup) != len(y_true):
        raise ValueError("subgroup must match y_true in length and be 1-D.")

    results: Dict[str, Dict[str, float]] = {}

    for group in np.unique(subgroup):
        mask = subgroup == group

        metrics = classification_metrics(
            y_true[mask],
            y_prob[mask],
            threshold=threshold,
        )

        metrics["ece"] = expected_calibration_error(
            y_true[mask],
            y_prob[mask],
            n_bins=n_bins,
        )

        metrics["small_group_warning"] = float(
            len(y_true[mask]) < min_group_n
        )

        results[str(group)] = metrics

    return results


@dataclass
class TemperatureScaler:
    """Temperature-scaling parameters for one calibration group."""

    temperature: float
    n_observations: int
    fallback_used: bool
    fallback_reason: Optional[str] = None


def subgroup_temperature_scale(
    logits: np.ndarray,
    y_true: np.ndarray,
    subgroup: np.ndarray,
    min_group_n: int = 30,
    global_temperature: Optional[float] = None,
) -> Tuple[np.ndarray, Dict[str, TemperatureScaler]]:
    """
    Apply subgroup temperature scaling with global fallback.

    A separate temperature is estimated only when a subgroup contains
    at least min_group_n observations and both outcome classes are present.

    Temperatures are bounded to avoid extreme numerical solutions.

    Returns
    -------
    calibrated_probabilities:
        Calibrated probabilities.
    metadata:
        Temperature and fallback information for each subgroup.
    """
    logits = np.asarray(logits, dtype=float)
    y_true = np.asarray(y_true, dtype=int)
    subgroup = np.asarray(subgroup)

    if not (len(logits) == len(y_true) == len(subgroup)):
        raise ValueError("All inputs must have equal length.")

    if len(logits) == 0:
        raise ValueError("Inputs must contain at least one observation.")

    if not np.all(np.isfinite(logits)):
        raise ValueError("logits must contain only finite values.")

    if not np.all(np.isin(y_true, [0, 1])):
        raise ValueError("y_true must contain only 0 and 1.")

    if min_group_n < 1:
        raise ValueError("min_group_n must be at least 1.")

    def fit_temperature(
        group_logits: np.ndarray,
        group_y: np.ndarray,
    ) -> float:
        """Fit temperature by minimizing binary log loss."""

        def objective(log_temperature: float) -> float:
            temperature = np.exp(log_temperature)
            probabilities = expit(group_logits / temperature)

            eps = 1e-12
            probabilities = np.clip(probabilities, eps, 1 - eps)

            loss = -np.mean(
                group_y * np.log(probabilities)
                + (1 - group_y) * np.log(1 - probabilities)
            )
            return float(loss)

        result = minimize_scalar(
            objective,
            bounds=(-2.0, 2.0),
            method="bounded",
        )

        return float(np.exp(result.x))

    if global_temperature is None:
        global_temperature = fit_temperature(logits, y_true)

    if global_temperature <= 0 or not np.isfinite(global_temperature):
        raise ValueError("global_temperature must be positive and finite.")

    calibrated = np.empty(len(logits), dtype=float)
    metadata: Dict[str, TemperatureScaler] = {}

    for group in np.unique(subgroup):
        mask = subgroup == group
        group_logits = logits[mask]
        group_y = y_true[mask]
        n_group = len(group_y)

        if n_group < min_group_n:
            temperature = global_temperature
            fallback = True
            reason = "subgroup_below_min_group_n"

        elif len(np.unique(group_y)) < 2:
            temperature = global_temperature
            fallback = True
            reason = "subgroup_contains_one_outcome_class"

        else:
            temperature = fit_temperature(group_logits, group_y)
            fallback = False
            reason = None

        calibrated[mask] = expit(group_logits / temperature)

        metadata[str(group)] = TemperatureScaler(
            temperature=temperature,
            n_observations=n_group,
            fallback_used=fallback,
            fallback_reason=reason,
        )

    return calibrated, metadata


def synthetic_example(seed: int = 42):
    """
    Generate a small synthetic example for demonstration.

    The data are entirely simulated and contain no patient information.
    """
    rng = np.random.default_rng(seed)

    n = 240

    y_true = rng.binomial(1, 0.35, n)

    age_group = rng.choice(
        ["adult", "pediatric"],
        size=n,
        p=[0.55, 0.45],
    )

    site = rng.choice(
        ["site_A", "site_B"],
        size=n,
        p=[0.5, 0.5],
    )

    logits = (
        -0.5
        + 1.6 * y_true
        + rng.normal(0, 1.0, n)
    )

    probabilities = expit(logits)

    return y_true, probabilities, age_group, site


if __name__ == "__main__":
    y_true, y_prob, age_group, site = synthetic_example()

    print(f"ASAC workbench version: {VERSION}")
    print("\nAge-group audit:")

    results = audit_fairness(
        y_true=y_true,
        y_prob=y_prob,
        subgroup=age_group,
        min_group_n=30,
    )

    for group, metrics in results.items():
        print(f"\n{group}")
        for name, value in metrics.items():
            print(f"  {name}: {value}")

    print("\nNote:")
    print("Synthetic demonstration only.")
    print("Not clinically validated.")
    print("Not intended for clinical diagnosis.")
