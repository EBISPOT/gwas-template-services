# gwas-template-services

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/63c9e20a0f6b428f8cbd8ad294beeb68)](https://app.codacy.com/app/DSuveges/gwas-template-services?utm_source=github.com&utm_medium=referral&utm_content=EBISPOT/gwas-template-services&utm_campaign=Badge_Grade_Dashboard)

Application to provide template related services for the deposition interface

## Installation

 1. Install miniconda
 2. Clone repo

```bash
cd ${APPROOT}
git clone https://github.com/EBISPOT/gwas-template-services
cd gwas-template-services
```

 2. Create environment based on the environment file

```bash
ENVNAME=template_serv
conda env create -f ${APPROOT}/gwas-template-services/environment.yml \
    --prefix ${MINICONDA}/envs/${ENVNAME}
```

 3. Activate environment and install local packages

```bash
conda activate ${ENVNAME}
pip install .
```

The above command will also install the standalone version of the packages.

 4. Startup web application

```bash
gunicorn -b ${APPHOST}:${PORT} app:app
```

## Using the stand-alone version

```bash
gwas-spreadsheet_builder --output test_output.xlsx \
    --input note:schema_definitions/notes_schema.xlsx \
        study:schema_definitions/study_schema.xlsx \
        association:schema_definitions/association_schema.xlsx \
        samples:schema_definitions/samples.
```

## Endpoints

### Download empty template sheet

`/templates` (GET)

### Get a list of available schemas

`/schemas/` (GET)

### Get JSON schema

`/schemas/{schema_name}` (GET)

### Upload file for a submission

`/upload` (POST)

**Parameters:**

  * `templateFile`: file, required
  * `submissionId`: int, required
  * `fileName`: string, required

### Trigger validation

`/validation?submissionId=<submissionId: int>&fileName=<fileName: str>` (GET)
