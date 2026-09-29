# Changelog

All notable changes to the ASAC software repository are documented in this file.

## [0.2.0] — 2026-09-29

### Added

- Subgroup performance auditing.
- Sensitivity, specificity, precision, and F1 score.
- Expected Calibration Error (ECE).
- Brier score.
- Explicit handling of single-class subgroups.
- Subgroup-size warnings for small groups.
- Subgroup temperature scaling.
- Global calibration fallback when subgroup data are insufficient.
- Synthetic demonstration data for reproducibility.

### Scientific Scope

This release provides a minimal Python reference implementation for selected
ASAC auditing and calibration components.

It does not constitute a complete implementation of the ASAC framework and has
not been clinically validated.

### Limitations

This release does not include:

- malaria diagnostic model training;
- domain-adversarial training;
- held-out-site validation;
- clinical reference-standard adjudication;
- Grad-CAM or other explainability analysis;
- deployment drift monitoring; or
- prospective clinical evaluation.

### Status

**Research/audit use only.**

This software is not intended for clinical diagnosis, treatment decisions, or
replacement of qualified healthcare professionals.

[0.2.0]: https://github.com/oriyalthomas-design/asac-malaria-ai
