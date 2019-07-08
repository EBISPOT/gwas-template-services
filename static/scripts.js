// Generate template:
function generateTemplate(){
    var parameters = getRadio();

    // Submit POST request:
    var xhr = new XMLHttpRequest();
    var hostname=window.location.hostname;
    xhr.open("POST", "templates", true);
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

function saveBlob(blob, fileName) {
    var a = document.createElement("a");
    a.href = window.URL.createObjectURL(blob);
    a.download = fileName;
    a.dispatchEvent(new MouseEvent("click"));
}

// Function to parse radio buttons:
function getRadio() {
    var parameters = new FormData();
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
    return(parameters);
}

document.getElementById("generate").onclick = function(){ generateTemplate()  };

