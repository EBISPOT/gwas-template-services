// Function to parse radio buttons:
function parseForm() {
    var parameters = new FormData();

    // Parsing radio buttons
    for(var field of ["curator", "haplotype", "effect", "backgroundTrait"]){
        var radioValue = $(`input[name=${field}]:checked`).val();
        parameters.append(field, radioValue);
    }

    // Check if user uploads summary stats:
    if (document.getElementById("summaryStats").checked){
        var accessionIDs = document.getElementById("accessionIDs").value;
        accessionIDs = accessionIDs.replace(/\s/g, "").split(",");
        parameters.append("accessionIDs", accessionIDs);
    }
    return(parameters);
}

// Function to save retrieved template file:
function saveBlob(blob, fileName) {
    var a = document.createElement("a");
    a.href = window.URL.createObjectURL(blob);
    a.download = fileName;
    a.dispatchEvent(new MouseEvent("click"));
}

// Function to retrieve study data from the GWAS Catalog REST API:
function getStudies(pmid){


    // Submit get request:
    var xhr = new XMLHttpRequest();
    var hostname=window.location.hostname;
    xhr.open("POST", "v1/templates", true);
    xhr.responseType = "blob";

}


function getStudies(pmid){
    var URL = `https://www.ebi.ac.uk/gwas/rest/api/studies/search/findByPublicationIdPubmedId?pubmedId=${pmid}&size=1000`;
    var result = null;
    $.ajax({
        url: URL,
        type: 'get',
        dataType: 'json',
        async: false,
        success: function(data) {
            result = data;
        },
        error: function(request){
            console.log("[Error] Retrieving data from the REST API failed. URL: " + URL);
            console.log(request.responseText)
            result = [];
        }
    });
    return result;
}



// Call API to generate template:
function generateTemplate(){
    var parameters = parseForm();

    // Submit POST request:
    var xhr = new XMLHttpRequest();
    var hostname=window.location.hostname;
    xhr.open("POST", "v1/templates", true);
    xhr.responseType = "blob";

    xhr.send(parameters);
    xhr.onload = function() {
        if ( this.status !== 200 ){
            alert("Request failed. Error code: " + this.status);
        }
        else {
            var blob = this.response;
            var fileName = "template.xlsx";
            saveBlob(blob, fileName);
        }
    };
}

document.getElementById("generate").onclick = function(){ generateTemplate();};

