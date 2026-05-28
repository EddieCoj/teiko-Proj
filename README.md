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
      Part 1: Creates SQLite database and loads data from cell-count.csv
      Part 2: Calculates relative frequencies for each cell population
      Part 3: Performs statistical comparison (responders vs non-responders)
      Part 4: Analyzes baseline melanoma subset and saves results

4. **Launch the interactive dashboard**












