# SDAPS Pipeline

  

## Prerequisites

- Python 3

-  `sdaps` CLI installed on your system (v.1.9.13) https://sdaps.org/install/


## Setup

  Ensure commands are run in the *sdaps_pipeline* folder.

1.  **Create the Virtual Environment:**

```bash

python3 -m venv my-env

```

2.  **Activate the Virtual Environment:**

```bash

source my-env/bin/activate

```

3.  **Install Requirements:**

Ensure `requirements.txt` is installed:

```bash

pip install -r requirements.txt

```

4. **Deactivate the Virtual Environment:**
```bash
deactivate
```


## Running the Pipeline

  

To run the pipeline, you can use:
  

```bash

./run_all.sh

```

## File Structure
- sort.py: Sorts new and incoming questionnaires into their appropriate "sorted" project folders
- run_all.sh: Runs all the scripts from the pipeline at once
- extract_sqlite_data.py: Exports project information (information from each individual filled out survey) from the database that SDAPS creates
- create_projects.sh: Creates SDAPS projects from all LaTeX survey sources in tex_sources and its dependencies (If the SDAPS project is already created, it is skipped)

## FAQ

1. How do I make corrections to a survey?
Open the SDAPS GUI (sdaps gui <project/<project_name>>) and manually adjust the answers and fields and save.  Running extract_sqlite_data.py at a project directory will extract the most up-to-date information on filled questionnaires.

2. How do I create a new project?
Create the LaTeX source file needed for the surveym and put it into the tex_sources folder.  You can then run ./create_projects.sh or run the entire pipeline with ./run_all.sh to create the new project.  The new projects will be available in the projects/ directory.

3. Why do we need RClone?
RClone is the method used to move surveys from a device to the server where this application is available.

4. How does sorting work?
Each unsorted PDF has the text extracted from the image.  The first few lines (which contain the project name) are scanned and compared against all existing project names.  The survey is then matched to the project with the highest similarity.

5. While sorting, what if the PDF does not actually match any of the projects?
The PDF stays in the newSurveys/ folder and is not moved.

6. How do I get the most up-to-date results of an SDAPS project?
Run extract_sqlite_data.py on the project.

