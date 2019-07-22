// Function to parse radio buttons:
function parseForm() {
    var parameters = new FormData();

    // Parsing radio buttons
    for(var field of ["curator", "haplotype", "effect", "backgroundTrait"]){

        var form = document.getElementById("templateCustomizer")
        parameters.append(field, form.elements[field].value)
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
    }
}

document.getElementById("generate").onclick = function(){ generateTemplate();}

