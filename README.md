ASAC — Age- and Site-Aware Calibration for Malaria Diagnostic AI

Version: 0.2.0
Author: Thomas Jabiya Oriya
Affiliation: Independent Researcher, Kisumu, Kenya

Purpose

ASAC (Age- and Site-Aware Calibration) is a proposed conceptual and methodological framework for evaluating the reliability of malaria diagnostic artificial intelligence (AI) across patient subgroups, healthcare sites, image-acquisition conditions, and deployment environments.

The framework is designed around the following research pathway:

Audit → Model → Evaluate → Calibrate → Explain → Monitor

ASAC focuses particularly on pediatric subgroup reliability and cross-site generalization, while recognizing that poorer performance in children or at particular sites must be demonstrated empirically rather than assumed.

Current Implementation

This repository contains a minimal Python reference implementation for selected ASAC auditing components:

- Subgroup sensitivity and specificity
- Precision and F1 score
- Expected Calibration Error (ECE)
- Brier score
- Explicit handling of single-class subgroups
- Subgroup-size warnings
- Subgroup temperature scaling
- Global calibration fallback when subgroup data are insufficient
- Synthetic demonstration data

Scientific Scope

The current software is a research and auditing prototype. It does not establish that:

- pediatric malaria AI performs worse than adult malaria AI;
- a particular healthcare site causes poorer model performance;
- ASAC improves diagnostic performance;
- the framework has been clinically validated; or
- the software can safely be used for clinical diagnosis.

These questions require appropriately designed empirical studies.

Limitations

The current implementation does not provide:

- a malaria diagnostic classifier;
- domain-adversarial training;
- held-out-site validation;
- clinical reference-standard adjudication;
- Grad-CAM or other explainability analysis;
- deployment drift monitoring;
- prospective clinical evaluation; or
- health-system implementation.

These components form part of the broader ASAC research agenda and require study-specific data, methods, and validation.

Data

The current example uses synthetic data only.

No patient-level or clinical data are included in this repository.

Clinical Status

Research/audit use only.

This software is not clinically validated and is not intended for clinical diagnosis, treatment decisions, or replacement of qualified healthcare professionals.

Research Status

ASAC is currently a conceptual/methodological framework. Empirical validation is a subsequent research objective.

The immediate research question is whether existing malaria microscopy AI datasets and evaluation practices provide sufficient structure to support defensible claims about pediatric subgroup reliability and cross-site generalization.

Reproducibility

The repository is intended to support transparent methodological development and reproducible research.

Future versions may add:

- public-data audits;
- structured metadata assessment;
- site-aware evaluation;
- calibration experiments;
- explainability and shortcut auditing;
- statistical evaluation procedures; and
- deployment-monitoring methods.

Citation

When using this software, please cite the associated ASAC research paper and the specific software version used.
 Associated Research Manuscript

Age- and Site-Aware Calibration for Reliable Malaria Diagnostic AI in East African Primary Healthcare

Manuscript DOI: 10.5281/zenodo.23082413
Author: Thomas Jabiya Oriya
Independent Researcher, Kisumu, Kenya

ORCID: to be added

Licence

This project is released under the MIT License.

---

Research status: Conceptual framework and methodological prototype
Software version: 0.2.0
Clinical validation: None