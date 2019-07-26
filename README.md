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

### `/template_download_test`

It's a html page to demonstrate the behavior of the customizable template spread sheet generation.

**Parameters:**

* `curator` - Describing if a user is member of the curator group or not (optional, yes/no)
* `haplotype` - If the user is depositing haplotype based associations (optional, yes/no)
* `snpxsnp` - If the user is depositing SNP x SNP interaction based associations (optional, yes/no)
* `effect` - How the effect of the association is expressed (Ooptional, R/beta)
* `backgroundTrait` - If the study applied background traits (optional, yes/no)
* `accessionIDs` - Array of strings optional. If submitted it is assumed that the user is depositing summary 
stats for an existing publication. The provided accession IDs will be pre-filled into the template. 

## Using the stand-alone scripts

Documentation comes later.