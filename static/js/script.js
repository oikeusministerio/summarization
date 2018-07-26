
var server_base_path = 'http://localhost:5000'

function prepareRequestText(path, method, summaryLength, returnType) {
    var content = document.getElementById("content").value
    var xhr = new XMLHttpRequest();
    xhr.open("POST", server_base_path + path, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    returnJustification = "True"
    xhr.send(JSON.stringify({
        content: content,
        summary_length: summaryLength,
        method: method,
        return_justification: returnJustification,
        return_type: returnType
    }));
    return xhr
}

function sendText(path, method,summaryLength) {
    var xhr = prepareRequestText(path, method, summaryLength, 'json')
    xhr.onload = function() {
      document.getElementById("in_progress").innerHTML = ""
      document.getElementById("submit_button").disabled = false;
      var data = JSON.parse(this.responseText);
      if(data.success) {
        if (method == 'graph' && returnJustification == "True" && 'ranking' in data) {
            showSummary(data.summary, data.positions, true, data.ranking);
        } else {
            showSummary(data.summary, data.positions, false);
        }
        if(method == 'embedding' && returnJustification == "True") {
            fetchVisualisation(data.words,data.neighbors)
        }
      } else {
        showError(data.error)
      }
    }
}

function sendTextNER(path, returnType) {
    var xhr = prepareRequestText(path, null, null, returnType)
    xhr.onload = function() {
        document.getElementById("in_progress").innerHTML = ""
        document.getElementById("submit_button").disabled = false;
        document.getElementById("submit_button_named_entity").disabled = false;
        if(this.status == 200 || this.status == 201) {
            if (returnType == 'json' || returnType == 'html') {
                var data = JSON.parse(this.responseText);
                document.getElementById("error_output").innerHTML = ""
                document.getElementById("output_div").innerHTML = data.names
            } else {
                //debugger;
                document.getElementById("error_output").innerHTML = ""
                document.getElementById("output_div").innerHTML = '<img src="data:image/png;base64,' + this.response + '" data-src="' + this.response + '"/>'
            }
        } else {
            var data = JSON.parse(this.responseText);
            showError(data.error)
        }
    }
}

function handleResponse(response, returnType) {
    document.getElementById("in_progress").innerHTML = ""
    document.getElementById("submit_button").disabled = false;
    document.getElementById("submit_button_named_entity").disabled = false;
    if(response.status == 200 || response.status == 201) {
        if (returnType == 'json') {
        // TODO handle ners also
            var data = JSON.parse(response.responseText);
            showMultiSectionSummary(data);
        } else if (returnType == 'html'){
            document.getElementById("error_output").innerHTML = ""
            document.getElementById("output_div").innerHTML = response.responseText
        } else if (returnType == 'docx') {
            mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document,'
            var fileObj = new File([response.response], 'tiivistelma.docx',  {type: mimetype})
            saveAs(fileObj);
        } else {
            document.getElementById("error_output").innerHTML = ""
            document.getElementById("output_div").innerHTML = '<img src="data:image/png;base64,' + response.response + '" data-src="' + response.response + '"/>'
        }
    } else {
        var data = JSON.parse(response.responseText);
        showError(data.error)
    }
}

function sendFiles(path, files, returnType) {
    if (files.length < 1) {
        showError("Anna tiedosto tai copy-pastea tiivistettävä teksti.");
        document.getElementById("submit_button").disabled = false;
        return;
    }
    var fd = new FormData();
    for (var i = 0; i < files.length; i++) {
        var file = files[i]
        fd.append("file-"+i, file);
    }

    var xhr = new XMLHttpRequest();
    if (returnType == 'docx') {
        xhr.responseType = 'blob';
    }
    xhr.open('POST', path, true);

    xhr.upload.onprogress = function(e) {
        if (e.lengthComputable) {
          var percentComplete = (e.loaded / e.total) * 100;
          console.log(percentComplete + '% uploaded');
        }
    };
    xhr.onload = function() {
        handleResponse(this, returnType)
    };
    xhr.send(fd);
}

function send(e) {
    e.preventDefault();
    clearCanvas();
    document.getElementById("submit_button").disabled = true;
    document.getElementById("output_div").innerHTML = ""
    document.getElementById("error_output").innerHTML = ""


    document.getElementById("in_progress").innerHTML = "Lähetetty, tässä menee noin 1-2 minuuttia."
    var method = document.querySelector('input[name="method"]:checked').value;

    var returnJustification = "True";//document.querySelector('input[name="return_justification"]:checked').value;
    var returnTypeSelector = document.getElementById("returnType")
    var returnType = returnTypeSelector.options[returnTypeSelector.selectedIndex].value

    var textOrFile = document.querySelector('input[name="text_input_mode"]:checked').value;
    if (textOrFile == "copy_paste_input") {
        var summaryLength = document.getElementById("cp_summary_length").value
        sendText('/summarize',method,summaryLength)
    } else if(textOrFile == "directory_input") {
        var summaryLength = document.getElementById("dir_summary_length").value
        var files = document.getElementById("multiple_files").files
        var path =  server_base_path + '/summarize/directory?summary_length='+summaryLength
                                    + "&method=" +method + "&return_type="+returnType
        sendFiles(path,files, returnType) //json
    }
}

function sendForNer(e) {
    e.preventDefault();
    clearCanvas();
    document.getElementById("submit_button_named_entity").disabled = true;
    document.getElementById("output_div").innerHTML = ""
    document.getElementById("error_output").innerHTML = ""
    document.getElementById("in_progress").innerHTML = "Lähetetty, tässä menee noin 1-2 minuuttia."


    var returnTypeSelector = document.getElementById("returnType")
    var returnType = returnTypeSelector.options[returnTypeSelector.selectedIndex].value
    var inputMode = document.querySelector('input[name="text_input_mode"]:checked').value;
    if (inputMode == "copy_paste_input") {
        sendTextNER('/entities', returnType)
    } else {
        var fileId = "multiple_files"
        var files = document.getElementById(fileId).files
        var path =  server_base_path + '/entities/directory?return_type=' + returnType
        sendFiles(path, files, returnType)
    }
}

// modify this to more pretty
function showError(text) {
    console.error(text)
    document.getElementById("in_progress").innerHTML = ""
    document.getElementById("error_output").innerHTML = text
    document.getElementById("output_div").innerHTML = ""
}

// modify this to more pretty
function showSummary(text, positions, hasRanking, ranking) {
    document.getElementById("error_output").innerHTML = ""
    var output = '<table class="summary_table"> <tr>'
    output += "<th>VALITTIIN LAUSEET </th>"
    if (hasRanking) {
        output += "<th> lauseen LEX-RANK pisteet </th>"
    }
    output += "</tr>"
    for(var i = 0; i<positions.length;i++) {
        output += "<tr>"
        output += "<td>" + positions[i] + "</td>"
        if (hasRanking) {
            output += "<td>" + ranking[i] + "</td>"
        }
        output += "</tr>"
    }
    output += "</table> <br><br>"
    output += "TIIVISTELMÄ: \n" + text
    document.getElementById("output_div").innerHTML = output
}

function showMultiSectionSummary(data) {
    document.getElementById("error_output").innerHTML = ""
    htmlOutput = "<div>"
    for (var j in data.filenames) {
        var fn = data.filenames[j]
        htmlOutput += "<h2> Tiedosto : " +fn+ "</h2>"
        var file = data[fn]
        for (var i in file.titles) {
            var title = file.titles[i]
            htmlOutput += "<h3>" + title + "</h3>"
            htmlOutput += "<p>" + file[title].summary + "</p>"
        }
    }
    htmlOutput += "</div>"
    document.getElementById("output_div").innerHTML = htmlOutput
}

function setup() {
    document.getElementById("submit_button").addEventListener("click", send);
    document.getElementById("submit_button_named_entity").addEventListener("click", sendForNer);

    var textOrFile = document.querySelector('input[name="text_input_mode"]:checked').value;
    toggleTextInputField({value: textOrFile})
}

function toggleTextInputField(e) {
    if (e.value == "copy_paste_input") {
        document.getElementById("copy_paste_input").style.display = "block";
        document.getElementById("directory_input").style.display = "none";
    } else {
        document.getElementById("copy_paste_input").style.display = "none";
        document.getElementById("directory_input").style.display = "block";
    }
}

function fetchVisualisation(words, neighbors) {
    var img = new Image();
    img.onload = function () {
        var canvas = document.getElementById('visualisation_canvas');
        var ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, img.width,    img.height,     // source rectangle
                   0, 0, canvas.width, canvas.height);
    };
    img.src = "http://localhost:5000/visualize/embeddings?words=" +
                encodeURIComponent(words) + "&neighbors=" + encodeURIComponent(neighbors);
}

function clearCanvas() {
    var canvas = document.getElementById('visualisation_canvas');
    var context = canvas.getContext('2d');
    context.clearRect(0, 0, canvas.width, canvas.height);
}