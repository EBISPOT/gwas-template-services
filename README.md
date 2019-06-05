# gwas-template-services

Application to provide template related services for the deposition interface

## Installation

1. Install miniconda
2. Clone repo

```bash
cd ${APPROOT}
git clone https://github.com/EBISPOT/gwas-template-services
cd gwas-template-services
```

2. Create environment based on the environment file.

```bash
ENVNAME=template_serv
conda env create -f ${APPROOT}/gwas-template-services/environment.yml --prefix ${MINICONDA}/envs/${ENVNAME}
```

3. Activate environment and run app with gunicorn

```bash
conda activate ${ENVNAME}
gunicorn -b ${APPHOST}:${PORT} app:app
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


