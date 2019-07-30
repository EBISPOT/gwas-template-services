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
    if ($("input[id=summaryStats]").is(":checked")){
        parameters.append("summaryStats", "true");
    };

    // Check if user uploads summary stats and the parsed study data is filled:
    if ( Object.keys(parsedStudyData).length > 0 ){
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
    var REST_URL = `http://${location.hostname}:8080/gwas/rest/api`;
    var URL = `${REST_URL}/studies/search/findByPublicationIdPubmedId?pubmedId=${pmid}&size=1000`;
    var result = null;
    $.ajax({
        url: URL,
        type: "get",
        dataType: "json",
        async: false,
    })
    .done(function(data) {
            $( "#publicationRecord" ).append( `<p>[Info] Retrieving data from the GWAS Catalog REST API was successful.</p>` );
            result = data;})
    .fail(function( jqXHR, textStatus ) {
        $( "#publicationRecord" ).append( `<p>[Error] Retrieving data from the GWAS Catalog REST API failed. Reason: ${textStatus}</p>` );
        $( "#publicationRecord" ).append( `<p>[Warning] Reading study data from local file...</p>` );

        // Load study data from JSON file:
        var data = getStaticData();
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
    }
    return parsedStudyData;
}

// Parse form data
function generateCurlCommand(formData){
    var curlCommand = `curl -X POST \"${location.origin}/v1/templates\"`;

    for (var pair of formData.entries()) {
        curlCommand += ` \\&#10;    -d ${pair[0]}='${pair[1]}'`;
    }
    //curlCommand.replace(/\\/g, "");
    curlCommand += " > template.xlsx";
    return curlCommand;
}

// Call API to generate template:
$("button[id=generate]").click(function generateTemplate(){
    var parameters = parseForm();

    // Show report box:
    $("#requestBody").show();

    // Submit POST request:
    var xhr = new XMLHttpRequest();
    var hostname=window.location.hostname;
    xhr.open("POST", "v1/templates", true);
    xhr.responseType = "blob";

    // Printing out request body:
    var curlString = generateCurlCommand(parameters);

    $( "#requestBody" ).empty();
    $( "#requestBody" ).append( `<p>[Info] This is the equivalent curl command:<br>${curlString}</p>` );

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
$("input[id=summaryStats]").change(function(){
    if($(this).is(":checked")) {
        // Show option add pmid:
        $("#summaryStatsForm").show();
    }
});


// A function to retrieve the pubmed ID from the REST API:
$("button[id=pmidTest]").click(function(){

    // Show report box:
    $("#publicationRecord").show();

    // Get pubmedID:
    var pubmedID = document.getElementById("PubmedID").value;

    // Retrieve data from the REST API:
    var studies = getStudies(pubmedID);

    // Filter REST response:
    studies = studies._embedded.studies;

    // Extract meta-data:
    var title = studies[0].publicationInfo.title;
    var studyCount = studies.length;

    // Write report:
    if ( studies.length > 0){
        $( "#publicationRecord" ).append( `<p>[Info] Publication title: ${title}.</p>` );
        $( "#publicationRecord" ).append( `<p>[Info] Number of studies: ${studyCount}</p>`);

        // Parsing study data:
        parsedStudyData = parseStudyData(studies);
    }
    else {
        $( "#publicationRecord" ).append( `[Info] Retrieving data from the GWAS Catalog REST API was successful.` );
        return;
    }
});
