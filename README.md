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