# gwas-template-services

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/63c9e20a0f6b428f8cbd8ad294beeb68)](https://app.codacy.com/app/DSuveges/gwas-template-services?utm_source=github.com&utm_medium=referral&utm_content=EBISPOT/gwas-template-services&utm_campaign=Badge_Grade_Dashboard) [![Codacy Badge](https://api.codacy.com/project/badge/Coverage/a5ee270cf0e449be88980397ee49945d)](https://www.codacy.com/app/DSuveges/gwas-template-services?utm_source=github.com&utm_medium=referral&utm_content=EBISPOT/gwas-template-services&utm_campaign=Badge_Coverage)[![Build Status](https://travis-ci.org/EBISPOT/gwas-template-services.svg?branch=Add_testing)](https://travis-ci.org/EBISPOT/gwas-template-services)

Application to provide template related services for the deposition interface

**Requires Python 3.6+**

## Installation - using docker

For information on docker see [Docker documentation](https://docs.docker.com/)

1. Clone repository:
    ```bash
    git clone https://github.com/EBISPOT/gwas-template-services.git
    cd gwas-template-services
    ```

2. Build docker image:
    ```bash
    docker build -t template_services .
    ```
    Buildind an image named `template_services`
    
3. Run docker image:

    ```bash
    mkdir docker_logs
    docker run --detach \
           -p 8649:8000 \
           -v $(pwd)/docker_logs/:/application/logs \
           template_services
    ```
    * Detaching the running container for the shell
    * Mapping the exposed `8000` port to `8649` on the host
    * Mounting the `docker_logs` folder so the containerised app can write logs on the host
    * starting the `template_services` image
     
     When running the image, the application automatically started and is accessible on port `8649`
    
4. Test if application is running:

    ```bash
    curl -X GET "http://localhost:8649/v1/template-schema" -H "accept: application/json"
    ```
    The expected out should be a JSON document listing the available schema versions:
    ```JSON
    {
      "schema_versions": {
        "1.0": {
          "href": "http://localhost:8649//v1/template-schema/1.0"
        }
      }
    }
    ```

## Installation - using conda

1. Clone repository:
    ```bash
    git clone https://github.com/EBISPOT/gwas-template-services.git
    cd gwas-template-services
    ```
    
2. Create conda environment:

    ```bash
    conda env create -f environment.yml
    ```
    
3. Activate environment:

    ```bash
    conda activate template_serv
    ```
4. Install template service packates:

    ```bash
    pip install .
    ```
5. Start the web application:

    ```bash
    gunicorn -b localhost:8080 app:app \
        --log-level=debug \
        --access-logfile=logs/access.log \
        --error-logfile=logs/error.log
    ```

## Endpoints

### `/v1/template-schema` (GET)

Endpoint to expose all available schema versions. Returns a JSON.  

### `/v1/template-schema/{version}` (GET)

Endpoint to expose schema definition for a defined schema version. Returns a JSON.

### `/v1/templates` (POST)

Endpoint to generate a template spreadsheet in excel. Retruns a blob.

**Parameters:**

* `curator` - Describing if a user is member of the curator group or not (type: `boolean`, optional, default: `false`) 
* `summaryStats` - if submitting full metadata (`false`) of summary statistics (`true`). (type: `boolean`, optional, default: `false`)
* `prefillData` - if data sent to the endpoint to prefill certain cells.

**Structure of the pre-fill data:**

```json
{
  "sheetName": [
    {
      "column1": "c1_value1",
      "column2": "c2_value1",
      "column3": "c3_value1"
    },
    {
      "column1": "c1_value2",
      "column2": "c2_value2",
      "column3": "c3_value2"
    }
  ]
}
```

#### examples:

Generate template for curators to deposity full metadata set:

```bash
curl -X POST "http://localhost:9000/v1/templates" \
    -d  '{"curator" : true}' \
    -H "Content-Type: application/json" > template.xlsx
```

Generate template for a non-curator user, where studies don't have mapped traits, and associations are not shown:

```bash
curl -X POST "http://localhost:9000/v1/templates" \
    -d  '{"curator" : false}' \
    -H "Content-Type: application/json" > template.xlsx
```

Generate template for depositing sumamry stats for already published studies.

```bash
curl -X POST "http://localhost:9000/v1/templates" \
    -d  '{"summaryStats" : true}' \
    -H "Content-Type: application/json" > template.xlsx
``` 

Generate template for depositing sumamry stats for already published studies with pre-filled study metadata for an easier identification.

```bash
curl -X POST "http://localhost:9000/v1/templates" \
    -d  '{"summaryStats" : true, "prefillData" : {"study":[{"study_accession":"GCST002728","trait":"Yang-deficiency constitution","sample_description":"30 cases, 30 balanced constitution controls"}]}}' \
    -H "Content-Type: application/json" > template.xlsx
``` 

If pre-filled template is generated, the pre-filled values are password protected and users can only updated cells in columns were input is required.

## Using the stand-alone scripts

Documentation comes later.