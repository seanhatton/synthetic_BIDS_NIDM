# Synthetic BIDS-NIDM Dataset

A synthetic neuroimaging dataset containing 50 subjects structured according to the **Brain Imaging Data Structure (BIDS)** specification. This dataset integrates clinical assessment scores alongside processed structural MRI outputs from **FSL FAST** and **FIRST**.

## 📌 Dataset Overview

* **Subjects:** 50 (`sub-01` to `sub-50`)
* **Sessions:** Single session per subject (`ses-01`)
* **Modality:** Anatomic MRI (T1w)
* **Clinical Assessment Measures:**
  * **IQ:** Intelligence Quotient
  * **HAMD:** Hamilton Depression Rating Scale
* **Derivative Pipelines:**
  * **FSL FAST:** Tissue type segmentation (CSF, Gray Matter, White Matter)
  * **FSL FIRST:** Subcortical brain structure segmentation and volume extraction
* **Semantic Metadata:** Neuroimaging Data Model ([NIDM](https://nidm.nidm-terms.org/)) representation included under `nidm/`

---

## 📁 Repository Structure

```text
synthetic_BIDS_NIDM/
├── README.md
├── LICENSE
├── .bidsignore
├── dataset_description.json   # BIDS dataset metadata
├── participants.json          # Metadata descriptions for demographic and clinical variables
├── participants.tsv           # Subject demographic data (Age, Sex, IQ, HAMD scores)
├── nidm/                      # NIDM-Results RDF files and semantic metadata
├── derivatives/               # Pipeline output derivatives
│   └── fsl/                   # FSL FAST & FIRST segmentation outputs
└── sub-01/                    # BIDS subject raw data directories
    └── ses-01/
        └── anat/
            ├── sub-01_ses-01_T1w.nii.gz
            └── sub-01_ses-01_T1w.json
