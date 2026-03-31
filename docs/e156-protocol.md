# GRADEPro: A Browser-Based GRADE Evidence Profile and Summary of Findings Generator — Protocol

Background: Grading evidence certainty using the GRADE framework is central to guideline development, yet existing tools require institutional subscriptions or server infrastructure. Open-access, offline-capable tools are lacking. Objective: To develop GRADEPro, a browser-based application generating GRADE Evidence Profiles and Summary of Findings tables with zero server dependency. Methods: GRADEPro is a self-contained HTML and JavaScript file. The GRADE engine computes certainty by applying downgrade penalties for risk of bias, inconsistency, indirectness, imprecision, and publication bias (zero to minus-two each) and upgrade bonuses for large effect, dose-response, and opposing confounding (zero or plus-one) to a base of HIGH for RCTs or LOW for observational studies. Auto-suggestions derive from user-supplied I-squared, Egger p-values, and optimal information size. Absolute effects are control rate multiplied by relative risk per one thousand patients. Plain-language summaries are generated deterministically from certainty and effect direction. Three examples cover VTE anticoagulation, COVID-19 corticosteroids, and depression exercise. Exports: HTML, CSV, standalone page, narrative, and print.

**Word count (body):** 156

---

**References**

1. Guyatt GH, Oxman AD, Vist G, et al. GRADE: an emerging consensus on rating quality of evidence and strength of recommendations. *BMJ.* 2008;336:924–926.
2. Guyatt GH, Oxman AD, Kunz R, et al. What is "quality of evidence" and why is it important to clinicians? *BMJ.* 2008;336:995–998.
3. Balshem H, Helfand M, Schünemann HJ, et al. GRADE guidelines: 3. Rating the quality of evidence. *J Clin Epidemiol.* 2011;64:401–406.

---

**AI Disclosure**

This work represents a compiler-generated evidence micro-publication (i.e., a structured, pipeline-based synthesis output). AI is used as a constrained synthesis engine operating on structured inputs and predefined rules, rather than as an autonomous author. Deterministic components of the pipeline, together with versioned, reproducible evidence capsules (TruthCert), are designed to support transparent and auditable outputs. All results and text were reviewed and verified by the author, who takes full responsibility for the content. The workflow operationalises key transparency and reporting principles consistent with CONSORT-AI/SPIRIT-AI, including explicit input specification, predefined schemas, logged human-AI interaction, and reproducible outputs.
