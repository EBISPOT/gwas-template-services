// Function to parse radio buttons:
function parseForm() {
    var parameters = new FormData();

    // Parsing radio buttons
    for(var field of ["curator", "haplotype", "effect", "backgroundTrait"]){
        var radios = document.getElementsByName(field);

        // Looping through all buttons and save the value which is selected:
        for (var radio of radios) {
            if ( radio.checked ) {
                parameters.append(field, radio.value);
                break;
            }
        }
    }

    // Check if user uploads summary stats:
    if (document.getElementById('summaryStats').checked){
        accessionIDs = document.getElementById('accessionIDs').value;
        accessionIDs = accessionIDs.replace(/\s/g, "").split(",");
        console.log(accessionIDs);
        parameters.append('accessionIDs', accessionIDs)
    }
    console.log(parameters)
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

