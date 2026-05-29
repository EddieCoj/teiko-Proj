# Teiko Immune Cell Analysis

## Overview
This project analyzes high-dimensional cytometry data from clinical trials to identify immune cell population differences between treatment responders and non-responders. The pipeline processes cell count data, calculates relative frequencies, performs statistical comparisons, and provides an interactive dashboard for data exploration.

## Repository Structure
```text
teiko-proj/
├── load_data.py              # Database creation and data loading (Part 1)
├── analysis.py               # Core analysis: frequencies, statistics, subset queries (Parts 2-4)
├── dashboard/
│   └── app.py                # Streamlit interactive dashboard
├── Makefile                  # Automation targets for setup, pipeline, dashboard
├── requirements.txt          # Python dependencies
├── cell-count.csv            # Input data (immune cell counts per sample)
├── part2_frequencies.csv     # Output: Relative frequencies per cell population
├── part3_statistics.csv      # Output: Statistical test results
├── part4_results.txt         # Output: Subset analysis summary
└── README.md                 # This file
```


## Quick Start

### Prerequisites
- Python 3.10 or higher
- Git (optional, for cloning)

### Setup and Execution

1. **Clone this repository**
   ```bash
   git clone https://github.com/EddieCoj/teiko-Proj
   cd teiko-Proj##

2. **Install dependencies**
   ```bash
   make setup
   ```
   This installs all required Python packages (pandas, sqlite3, plotly, streamlit, scipy, etc.)

3. **Run the complete analysis pipeline**
   ```bash
   make pipeline
   ```

   This executes:

   - Part 1: Creates SQLite database and loads data from `cell-count.csv`
   - Part 2: Calculates relative frequencies for each cell population
   - Part 3: Performs statistical comparison (responders vs non-responders)
   - Part 4: Analyzes baseline melanoma subset and saves results

4. **Launch the interactive dashboard**
   ```bash
   make dashboard
   ```
   Then open your browser to http://localhost:8501

## Database Schema Design

The data is normalized into three tables for scalability and query efficiency.

---

### Table 1: `subjects`

| Column       | Type               | Description                   |
| ------------ | ------------------ | ----------------------------- |
| `subject_id` | TEXT (PRIMARY KEY) | Unique patient identifier     |
| `age`        | INTEGER            | Patient age                   |
| `sex`        | TEXT               | Male (`M`) or Female (`F`)    |
| `condition`  | TEXT               | Disease type (e.g., melanoma) |

**Rationale:** Demographics are stored once per subject, eliminating redundancy when a subject contributes multiple samples.

---

### Table 2: `samples`

| Column                      | Type               | Description                           |
| --------------------------- | ------------------ | ------------------------------------- |
| `sample_id`                 | TEXT (PRIMARY KEY) | Unique sample identifier              |
| `subject_id`                | TEXT (FOREIGN KEY) | Links sample to subject               |
| `response`                  | TEXT               | Treatment response (`yes` / `no`)     |
| `sample_type`               | TEXT               | Biological sample type (e.g., PBMC)   |
| `treatment`                 | TEXT               | Treatment administered                |
| `project`                   | TEXT               | Research project identifier           |
| `time_from_treatment_start` | INTEGER            | Timepoint relative to treatment start |

**Rationale:** Separates sample-specific metadata from subject demographics, allowing longitudinal analysis (multiple samples per subject).

---

### Table 3: `cell_counts`

| Column       | Type               | Description                       |
| ------------ | ------------------ | --------------------------------- |
| `sample_id`  | TEXT (FOREIGN KEY) | Links cell counts to sample       |
| `population` | TEXT               | Immune cell population name       |
| `count`      | INTEGER            | Raw cell count for the population |

**Rationale:** "Tidy data" format with one row per cell population per sample. This vertical structure scales efficiently because adding a new cell type doesn't require schema changes.

### Scalability Considerations
- 100+ projects, 10,000+ samples: Indexes on foreign keys (idx_samples_project, idx_cell_counts_sample) keep JOIN operations fast (O(log n) instead of O(n²))
- New cell types: Simply insert new rows into cell_counts with the new population name - no ALTER TABLE needed
- Additional metadata: Add columns to samples table (e.g., treatment_dose, lab_batch) without affecting existing analysis
- Query performance: Composite primary key on cell_counts enables instant lookups for specific (sample, population) pairs


## Analysis Summary

### Part 2: Relative Frequencies
For each sample, calculates the percentage of each immune cell population relative to the total cell count. Output saved to part2_frequencies.csv.

### Part 3: Responders vs Non-Responders
- Population: Melanoma patients receiving miraclib (PBMC samples only)
- Method: Mann-Whitney U test comparing relative frequencies between responders and non-responders
- Key finding: CD4+ T cells showed a statistically significant difference (p = 0.0133)
- Output: Boxplots (dashboard) and statistical summary (part3_statistics.csv)






