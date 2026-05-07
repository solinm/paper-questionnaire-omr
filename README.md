# Automatic Scoring of Paper-Based Questionnaires

An automated pipeline for processing paper-based questionnaires using SDAPS (Scripts for Data Acquisition with Paper-based Surveys). Scanned questionnaire images are synced from Dropbox via rclone, OCR-sorted into the correct SDAPS project, processed for optical mark recognition, and exported as CSV and JSON.

## Prerequisites

- Python 3
- `sdaps` CLI v1.9.13 — https://sdaps.org/install/
- `tesseract` CLI — https://github.com/tesseract-ocr/tesseract
- LaTeX with the `sdapsclassic` package (required to compile questionnaire sources)
- `rclone` configured with a Dropbox remote — https://rclone.org/dropbox/
- GTK with Broadway backend (for browser-based GUI access on headless servers)

## Directory Structure

All commands are run from the `sdaps_pipeline/` folder. Before first run, create the following directories inside `sdaps_pipeline/`:

```
sdaps_pipeline/
├── newSurveys/                        # Drop rclone-synced scans here
├── sortedSurveys/
│   └── <project_name>/               # Created automatically by sort.py
├── projects/
│   └── <project_name>/               # Created by create_projects.sh
├── csv_outputs/
│   └── <project_name>/
│       └── YYYYMMDD_HHMMSS/          # Timestamped output per run
├── tex_sources/
│   └── <project_name>/
│       └── questionnaire.tex         # LaTeX source for each questionnaire
├── run_all.sh
├── create_projects.sh
├── sort.py
├── extract_sqlite_data.py
└── requirements.txt
```

```bash
mkdir -p newSurveys sortedSurveys projects csv_outputs tex_sources
```

## Setup

1. **Create and activate the virtual environment:**

```bash
python3 -m venv my-env
source my-env/bin/activate
```

2. **Install Python dependencies:**

```bash
pip install -r requirements.txt
```

3. **Make shell scripts executable:**

```bash
chmod +x run_all.sh create_projects.sh
```

4. **Configure rclone for Dropbox** (if not already done):

```bash
rclone config
# Follow prompts to add a remote named "dropbox"
```

## Adding a New Questionnaire

1. Create or edit the LaTeX source file using the `sdapsclassic` document class. The questionnaires in this repo can be edited in [Overleaf](https://www.overleaf.com) — no local LaTeX installation needed. Once done, download the `.tex` file and place it at:

```
tex_sources/<project_name>/questionnaire.tex
```

2. Key requirements in the `.tex` file:
   - Use `sdaps_style=qr` and `checkmode=check` in the document class options
   - The `\title{}` value is used by the OCR sorting script to match scanned images to the correct project — it must be distinct and clearly printed on the form
   - Declare a scale identifier inside the `questionnaire` environment using `\addinfo`
   - Each question's `var=` parameter (e.g., `var=gas01`) maps directly to CSV column headers and JSON keys
   - For questionnaires with accented characters (e.g., French), include the following in the preamble:

```latex
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
```

3. Run `./create_projects.sh` or `./run_all.sh` to initialize the new SDAPS project. LaTeX is required on the server for this step (used by SDAPS to compile the template), but not on your local machine if you're editing in Overleaf. The compiled project will appear in `projects/<project_name>/`.

## Running the Pipeline

### Full pipeline (recommended for routine use)

Syncs from Dropbox, sorts, processes, and exports all questionnaires in one step:

```bash
./run_all.sh
```

This runs the following steps in order:

1. `rclone sync dropbox:<remote_path> newSurveys/` — pulls new scans from Dropbox
2. `create_projects.sh` — initializes any new SDAPS projects from `tex_sources/`
3. `sort.py` — OCR-sorts images from `newSurveys/` into `sortedSurveys/<project_name>/`
4. SDAPS processing — adds images, runs recognition, exports CSV
5. CSV-to-JSON conversion — converts outputs for backend use

Processed images and CSVs are saved to `csv_outputs/<project_name>/YYYYMMDD_HHMMSS/`.

### Individual scripts

Run these manually when needed:

```bash
# Re-sort any unprocessed images in newSurveys/
python3 sort.py

# Initialize new projects from tex_sources/ only
./create_projects.sh

# Extract updated results from a specific project after manual corrections
python3 extract_sqlite_data.py projects/<project_name>
```

## Scanning Guidelines

SDAPS is sensitive to perspective distortion. **Use a mobile scanner app rather than a raw photo.** Recommended options: Adobe Scan, CamScanner, or Apple's built-in document scanner. Flat, well-lit scans produce the most reliable recognition results.

## Manual Error Correction (Broadway GUI)

If recognition results need to be reviewed or corrected:

1. Start the Broadway backend:

```bash
broadwayd :5 &
```

2. Open the SDAPS GUI for the target project (in a separate terminal):

```bash
GDK_BACKEND=broadway BROADWAY_DISPLAY=:5 sdaps gui projects/<project_name>
```

3. Open a browser and navigate to `http://localhost:8085`

4. Inspect and correct responses in the GUI, then save.

5. Re-export the corrected data:

```bash
python3 extract_sqlite_data.py projects/<project_name>
```

## File Structure

| File | Description |
|---|---|
| `run_all.sh` | Runs the full pipeline end-to-end |
| `create_projects.sh` | Initializes SDAPS projects from LaTeX sources in `tex_sources/`; skips projects that already exist |
| `sort.py` | Extracts text from scanned images via Tesseract OCR and routes them to the correct `sortedSurveys/<project_name>/` folder using fuzzy string matching (confidence threshold: 0.6). Images that don't match any project remain in `newSurveys/` for manual review |
| `extract_sqlite_data.py` | Exports the most up-to-date questionnaire results from a project's SDAPS SQLite database to CSV and JSON |

## FAQ

**1. How do I make corrections to a survey?**

Launch the Broadway GUI (see above), adjust responses, and save. Then re-run `extract_sqlite_data.py` on the project to export updated results.

**2. How do I create a new project?**

Add the LaTeX source to `tex_sources/<project_name>/questionnaire.tex`, then run `./create_projects.sh` or `./run_all.sh`. The new project will appear in `projects/`.

**3. How does rclone fit in?**

rclone syncs completed questionnaire images from a shared Dropbox folder to the server's `newSurveys/` directory, replacing the need for manual file transfer.

**4. How does sorting work?**

`sort.py` uses Tesseract to extract text from each image, then compares it against the `\title{}` values from all known `questionnaire.tex` sources using fuzzy string matching. The image is routed to the project with the highest similarity score above 0.6.

**5. What if a scan doesn't match any project?**

The file stays in `newSurveys/` and is not moved or processed. Review it manually and either re-scan with better quality or move it to the correct `sortedSurveys/<project_name>/` folder manually, then re-run the pipeline.

**6. How do I get the most up-to-date results after corrections?**

```bash
python3 extract_sqlite_data.py projects/<project_name>
```

**7. Where is the output?**

Each pipeline run produces a timestamped directory at `csv_outputs/<project_name>/YYYYMMDD_HHMMSS/` containing the exported CSV, its JSON equivalent, and the processed images from that batch.
