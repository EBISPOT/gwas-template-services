/*
The parsed study data is a global variable, that might or might not be overwritten later
 */
var parsedStudyData = {};


// Function to parse radio buttons:
function parseForm() {
    var parameters = new FormData();

    // Parsing radio buttons
    for(var field of ["curator", "haplotype", "effect", "backgroundTrait"]){
        var radioValue = $(`input[name=${field}]:checked`).val();
        parameters.append(field, radioValue);
    }

    // Check if the summary stats checkbox is ticked:
    if ($('input[id=summaryStats]').is(':checked')){
        parameters.append('summaryStats', 'true');
    };

    // Check if user uploads summary stats and the parsed study data is filled:
    console.log("** Stuff: " + parsedStudyData);
    if ( Object.keys(parsedStudyData).length > 0 ){
        console.log("** Stuff: " + parsedStudyData);
        parameters.append("prefillData", JSON.stringify(parsedStudyData));
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

/*
A function that retrieves all the study related information based on the PMID of a publication:

Input: PMID
Output: Array of study documents
 */
function getStudies(pmid){
    var REST_URL = `http://${location.host}:8080/gwas/rest/api`;
    var URL = `${REST_URL}/studies/search/findByPublicationIdPubmedId?pubmedId=${pmid}&size=1000`;
    var result = null;
    $.ajax({
        url: URL,
        type: 'get',
        dataType: 'json',
        async: false,
        success: function(data) {
            $( "#publicationRecord" ).append( `<pre>[Info] Retrieving data from the GWAS Catalog REST API was successful.</pre>` );
            result = data;
        },
        error: function(request){
            console.log("[Error] Retrieving data from the REST API failed. URL: " + URL);
            console.log(request.responseText)
            result = [];
        }
    }).fail(function( jqXHR, textStatus ) {
        $( "#publicationRecord" ).append( `<pre>[Error] Retrieving data from the GWAS Catalog REST API failed. Reason: ${textStatus}</pre>` );
        $( "#publicationRecord" ).append( `<pre>[Warning] Reading study data from local file...</pre>` );

        // Load study data from JSON file:
        result = JSON.parse(data);
     });

    return result;
}


/*
A function to parse out study documents to get the relevant fields for generation fot the pre-filled spread sheet:

Input: Array of study documents
Output: Array of parsed study documents:

Each returned study document looks like this:
{
    "accessionID" : "Reticulocyte fraction of red cells",
    "diseaseTrait" : "GCST004619",
    "initialSampleSize" : "170,690 European ancestry individuals"
}
 */
function parseStudyData(studyData){
    var parsedStudyData = {"study" : []};

    // Loop through all studyes:
    for ( var study of studyData ){
        parsedStudyData.study.push({
            "study_accession" : study.accessionId,
            "trait" : study.diseaseTrait.trait,
            "sample_description" : study.initialSampleSize
        });
    };

    return parsedStudyData;
};

// Parse form data
function getFormData(formData){
    var JSON = {}
    for (var pair of formData.entries()) {
        JSON[pair[0]] = pair[1];
    }
    return JSON;
}

// Call API to generate template:
$('button[id=generate]').click(function generateTemplate(){
    parameters = parseForm();

    // Submit POST request:
    var xhr = new XMLHttpRequest();
    var hostname=window.location.hostname;
    xhr.open("POST", "v1/templates", true);
    xhr.responseType = "blob";

    // Printing out request body:
    var requestString = JSON.stringify(getFormData(parameters), undefined, 4);
    requestString = requestString.replace(/\\/g, '');

    $( "#requestBody" ).empty();
    $( "#requestBody" ).append( `<pre>[Info] This is the request body sent to the template generator endpoint:<br>${requestString}</pre>` );

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
});


// If the summary stats checkbox is ticked, we show the pubmed ID form:
$('input[id=summaryStats]').change(function(){
    if($(this).is(':checked')) {
        // Show option add pmid:
        $("#summaryStatsForm").show();
    }
});


// A function to retrieve the pubmed ID from the REST API:
$('button[id=pmidTest]').click(function(){

    // Get pubmedID:
    var pubmedID = document.getElementById("PubmedID").value;
    console.log("** parsed ID: " + pubmedID);

    // Retrieve data from the REST API:
    var studies = getStudies(pubmedID);

    // Filter REST response:
    studies = studies._embedded.studies;
    console.log(studies);

    // Extract meta-data:
    var title = studies[0].publicationInfo.title;
    var studyCount = studies.length;

    // Write report:
    if ( studies.length > 0){
        $( "#publicationRecord" ).append( `<pre>[Info] Publication title: ${title}.</pre>` );
        $( "#publicationRecord" ).append( `<pre>[Info] Number of studies: ${studyCount}</pre>`);

        // Parsing study data:
        parsedStudyData = parseStudyData(studies);
        console.log(parsedStudyData);
    }
    else {
        $( "#publicationRecord" ).append( `[Info] Retrieving data from the GWAS Catalog REST API was successful.` );
        return
    }
});
