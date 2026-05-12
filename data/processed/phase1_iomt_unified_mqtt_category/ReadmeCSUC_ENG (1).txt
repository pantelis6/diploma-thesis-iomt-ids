This file has been created on 11-05-2026 by Pantelis Petrakis.


GENERAL INFORMATION
------------------

1. Dataset title:
Unified IoMT Window-Traffic Table (CICIoMT2024 + IoMT-TrafficData): MIOTTA-NPT Features with Harmonized 2-, 6-, and 26-Class Labels


2. Authorship:

	Name: Pantelis Petrakis
	Institution: Universitat Politècnica de Catalunya (UPC) -- BarcelonaTech
	Email: pantelis.petrakis@estudiantat.upc.edu
	ORCID: 0009-0008-0339-4590

	Name: Jordi Domènech Fons
	Institution: Universitat Politècnica de Catalunya (UPC) -- BarcelonaTech
	Email: jordi.domenech.fons@upc.edu
	ORCID: 0000-0002-2977-7265

	Name: Olga León
	Institution: Universitat Politècnica de Catalunya (UPC) -- BarcelonaTech
	Email: olga.leon@upc.edu
	ORCID: 0000-0003-2869-051X

	Name: Isabel V. Martin-Faus
	Institution: Universitat Politècnica de Catalunya (UPC) -- BarcelonaTech
	Email: isabel.martin-faus@upc.edu
	ORCID: 0000-0001-9975-8791

	Name: Josep Pegueroles
	Institution: Universitat Politècnica de Catalunya (UPC) -- BarcelonaTech
	Email: josep.pegueroles@upc.edu
	ORCID: 0000-0002-5194-4883



DESCRIPTION
----------

1. Dataset language:
English (column names and string labels).


2. Abstract:
This dataset is a machine-learning-ready, tabular export of unified Internet of Medical Things (IoMT) network traffic. It merges two public PCAP-derived sources---CICIoMT2024 and IoMT-TrafficData---into a single aligned feature space produced by the MIOTTA-NPT preprocessing tool using a fixed packet window (W = 100 packets per record). Each row represents one traffic window described by 58 numeric window statistics and seven accompanying metadata/label fields. Labels are harmonized at three granularities: binary (Benign vs. Attack), categorical (six classes: Benign, DDoS, DoS, MQTT, Reconnaissance, Spoofing), and fine-grained (26 distinct attack sub-types preserved from the sources). Records retain provenance (source dataset, source file, original attack type/group). The release is split into stratified training, validation, and test partitions (approximately 70% / 15% / 15%) at the six-class level, totalling 8,011,534 rows across the three files. The numeric feature columns are standardized using scikit-learn's StandardScaler fitted on the training partition only and then applied to validation and test to prevent data leakage. Together with the CSV splits, this deposit includes metadata.joblib (Python/joblib dictionary: feature column order, split row counts, harmonisation scheme tag, and near-zero-variance feature audit list from QA) and scaler.joblib (the exact fitted StandardScaler from the same export run). The scaler is required to reproduce the identical transform on newly extracted MIOTTA-NPT feature matrices (e.g., external evaluation traffic); it cannot be faithfully reconstructed by refitting on the published CSVs because those files already store post-transform values.


3. Keywords:
IoMT; intrusion detection; network traffic; dataset unification; MIOTTA-NPT


4. Date of data collection (single date or date range):
Original PCAP captures follow the timelines documented by the respective source releases (CICIoMT2024; IoMT-TrafficData). The unified tabular export and train/validation/test split were generated during the UPC MIOTTA integration study in 2025--2026 (exact PCAP capture dates should be taken from the original dataset papers).


5. Publication Date:
Not yet published (pending deposition in Dataverse).


6. Grant information:

	Grant Agency: INCIBE CARISMATICA Chair of Cybersecurity (partial support)
	Grant Number: (chair programme; no project number supplied)

	Grant Agency: Generalitat de Catalunya
	Grant Number: 2024 FI-1 00643


7. Geographical location/s of data collection:
Original laboratory PCAP collections: locations and topologies are defined by the CICIoMT2024 and IoMT-TrafficData releases (see their documentation). Dataset integration, feature extraction, harmonization, quality assurance, scaling, and splitting were performed at UPC, Barcelona, Catalonia, Spain.



ACCESS INFORMATION
------------------------

1. Creative Commons License of the dataset:
CC0 1.0 Universal (CC0 1.0) Public Domain Dedication --- recommended for maximising reuse of tabular benchmark data. If the repository policy requires attribution instead, use CC BY 4.0; confirm with your Dataverse curators.


2. Dataset DOI:
Not assigned at the time of this README. A persistent identifier (typically a DOI) will be minted by the Dataverse installation upon successful publication of the dataset record.


3. Related publication:
Petrakis, P., Domènech, J., León, O., Martin-Faus, I. V., Pegueroles, J. (forthcoming). Unifying Heterogeneous IoMT Datasets for Intrusion Detection: From Laboratory Testbeds to Real Hospital Network Evaluation. (Manuscript associated with this release; no DOI yet.)


4. Link to related datasets:

	DOI/URL: CICIoMT2024 --- https://doi.org/10.1016/j.iot.2024.101375 (dataset distribution per paper and Canadian Institute for Cybersecurity resources)

	DOI/URL: IoMT-TrafficData --- https://doi.org/10.1109/ACCESS.2024.3445614

	DOI/URL: MIOTTA-NPT tool --- https://github.com/MIOTTA-UPC/Network-Preprocessing-Tool (public repository; version used at export time should be pinned in code release notes)



VERSIONING AND PROVENANCE
---------------

1. Last modification date:
11-05-2026


2. Were data derived from another source?:
Yes. Raw PCAPs and official dataset distributions from CICIoMT2024 (Dadkhah et al., 2024, Internet of Things, doi:10.1016/j.iot.2024.101375) and IoMT-TrafficData (Areia et al., 2024, IEEE Access, doi:10.1109/ACCESS.2024.3445614) were reprocessed with MIOTTA-NPT (León et al., JITEL 2025; public GitHub implementation) to obtain this unified tabular release.


3. Additional related data not included in this dataset:
Raw PCAP archives, intermediate Parquet shards, and non-window feature modes from MIOTTA-NPT are not bundled here. The tabular release folder includes metadata.joblib and scaler.joblib from the same export run as the CSVs (see FILE OVERVIEW).



METHODOLOGICAL INFORMATION
-----------------------

1. Description of the methods used to collect and generate the data:
Network packets were collected in controlled IoMT/healthcare-oriented testbeds according to the experimental designs of CICIoMT2024 and IoMT-TrafficData (see their articles for topology, attack injection, and benign baseline generation). This release does not contain new packet captures; it reproduces a harmonized window-level representation from the public PCAP corpora of those studies.


2. Data processing methods:
PCAPs were ingested by MIOTTA-NPT in combined window mode (W = 100 packets). Near-constant columns were removed after merging, leaving 58 aligned numeric descriptors per window. Labels were harmonized to binary, six-class categorical (with MQTT-related variants collapsed into a single MQTT category), and 26-class fine labels. Structural QA removed NaN/Inf values. A StandardScaler was fit on the training partition only and applied to train, validation, and test feature columns. Stratified 70/15/15 splitting used the six-class label to preserve class proportions across partitions.


3. Software or instruments needed to interpret the data:
Any CSV-capable tool (Python >= 3.10 with pandas >= 2.0 recommended; R readr/data.table; spreadsheet software for exploratory viewing). metadata.joblib and scaler.joblib are Python joblib-serialized objects; load with joblib.load in a trusted environment only (standard pickle-security caveats). metadata.joblib is a plain dict once loaded (feature_cols, split_sizes, category_scheme, near_zero_variance_features). For reproducibility of upstream extraction, MIOTTA-NPT (see GitHub) and the exact commit hash recorded in the project repository should be cited.


4. Information about instruments, calibration and standards:
Not applicable (derived statistical features from packet traces; no physical sensor calibration).


5. Environmental or experimental conditions:
Laboratory testbed conditions as reported in the source dataset publications; this tabular export inherits their limitations (controlled device populations, synthetic benign baselines, etc.).


6. Quality-assurance procedures performed on the data:
Per-record checks for finite numeric features; verification of presence of provenance fields; stratified split validation against expected class histograms; removal of invalid rows prior to export.



FILE OVERVIEW
----------------------

1. Explain the file naming conversion, if applicable:
Standard machine-learning partition names: train.csv (model fitting), val.csv (model selection / early stopping), test.csv (held-out evaluation).


2. File list:

	File name: train.csv
	Description: Training split; 5,608,073 data rows plus header; 65 columns (58 features + 7 metadata/label fields).

	File name: val.csv
	Description: Validation split; 1,201,730 data rows plus header; same schema as train.csv.

	File name: test.csv
	Description: Test split; 1,201,731 data rows plus header; same schema as train.csv.

	File name: metadata.joblib
	Description: Export-side dictionary (load with joblib): keys feature_cols (58 names, in transform order), split_sizes ({train,val,test} row counts matching the CSVs), category_scheme (string tag for the harmonisation variant, e.g. mqtt), near_zero_variance_features (QA list from the integration pipeline).

	File name: scaler.joblib
	Description: scikit-learn StandardScaler fitted on the training-split raw (pre-scale) MIOTTA-NPT features for the 58 columns listed in metadata.joblib under feature_cols, saved with joblib. Bundled with the same export run as the CSVs. Refitting a scaler on the published CSVs is statistically invalid for reproducing the transform on new raw feature matrices.


3. Relationship between files:
Mutually exclusive partitions of one unified table; together they contain all 8,011,534 labelled window records with no row overlap across files. metadata.joblib documents the ordered feature column list, split sizes, and harmonisation scheme tag. scaler.joblib is the preprocessing object that maps freshly extracted MIOTTA-NPT feature matrices (same 58 columns, pre-scale) to the same representation used in the CSVs.


4. File format:
Comma-separated values (CSV); UTF-8 encoding expected.


5. If the dataset includes multiple files, specify the directory structure and relationships between the files:
Flat directory: train.csv, val.csv, test.csv, metadata.joblib, scaler.joblib, reside in the same folder. No nested subfolders.



SPECIFIC INFORMATION FOR TABULAR DATA
-------------------------------------------

1. Name file:
train.csv, val.csv, test.csv (identical column layout).


2. Number of rows and columns:
8,011,534 rows in total (5,608,073 + 1,201,730 + 1,201,731); 65 columns. Row counts per file exclude the one-line CSV header.


3. Variables list:

The first 58 columns (Window ... Flow_IAT) are MIOTTA-NPT window statistics after per-feature standardisation (zero mean, unit variance parameters estimated on train.csv only). They are dimensionless z-scores, not raw packet counts.

Variable name: Window through Flow_IAT (58 columns total)
         Description: MIOTTA-NPT window statistics for W = 100 packets (protocol indicators, TCP flag statistics, rates, payload and header aggregates, inter-arrival statistics, moments, etc.) aligned across both sources. Column order is fixed; names appear in the CSV header.
	 Units of measure or value labels: Standardised numeric (z-score; StandardScaler parameters fitted on train.csv only).

Variable name: attack_type
         Description: Original attack label string from the source PCAP labelling scheme prior to harmonisation.
	 Units of measure or value labels: Free-text categorical string.

Variable name: source_file
         Description: Originating PCAP or trace identifier within the source distribution.
	 Units of measure or value labels: String path or filename token.

Variable name: source_dataset
         Description: Provenance tag indicating whether the row originated from CICIoMT2024 or IoMT-TrafficData.
	 Units of measure or value labels: Categorical string (e.g., CICIoMT2024, IoMT-TrafficData).

Variable name: attack_group
         Description: Source-specific attack grouping metadata preserved for traceability.
	 Units of measure or value labels: String categorical.

Variable name: label_category
         Description: Harmonised six-class target: Benign, DDoS, DoS, MQTT, Reconnaissance, Spoofing.
	 Units of measure or value labels: String categorical.

Variable name: label_binary
         Description: Harmonised binary target: Benign vs. Attack.
	 Units of measure or value labels: String categorical.

Variable name: label_fine
         Description: Harmonised 26-class fine-grained attack identifier (union of sub-types across sources).
	 Units of measure or value labels: String categorical.


4. Codes or symbols for missing data:
No missing-value tokens are used; rows with invalid numeric entries were removed during QA.


5. Special formats or abbreviations used:
MQTT-related attack variants are grouped under the single six-class label "MQTT" (reflected in the repository folder name). "MIOTTA-NPT" denotes the MIOTTA Network Preprocessing Tool.


MORE INFORMATION
--------------
Folder suffix "mqtt_category" aligns with metadata.joblib's category_scheme for the six-class harmonisation of MQTT-related attacks. Depositing metadata.joblib and scaler.joblib alongside the three CSVs is required for exact replication of the scaling protocol on new MIOTTA-NPT windows (e.g., external evaluation). For questions about this README template, contact the CSUC Research Support Working Group / UAB Libraries (original template authors). For dataset content questions, contact the authors listed above.

