
var server_base_path = 'http://localhost:5000'

function sendText(method,returnJustification) {
    var summary_length = document.getElementById("cp_summary_length").value
    var content = document.getElementById("content").value
    var xhr = new XMLHttpRequest();
    xhr.open("POST", server_base_path + "/summarize", true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({
        content: content,
        summary_length: summary_length,
        method: method,
        return_justification:returnJustification,
        return_type: 'json'
    }));
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

function sendFile(files, method,summaryLength, returnJustification) {
    if (files.length < 1) {
        showError("Anna docx tiedosto tai copy-pastea tiivistettävä teksti.");
        document.getElementById("submit_button").disabled = false;
        return;
    }
    var file = files[0]
    var fd = new FormData();
    fd.append("file", file);

    var xhr = new XMLHttpRequest();
    var path =  server_base_path + "/summarize/file?summary_length="+summaryLength
                                    + "&method=" +method + "&return_type=json"
    xhr.open('POST', path, true);

    xhr.upload.onprogress = function(e) {
        if (e.lengthComputable) {
          var percentComplete = (e.loaded / e.total) * 100;
          console.log(percentComplete + '% uploaded');
        }
    };
    xhr.onload = function() {
        document.getElementById("in_progress").innerHTML = ""
        document.getElementById("submit_button").disabled = false;
        var data = JSON.parse(this.responseText);
        if(data.success) {
            showMultiSectionSummary(data);
        } else {
            showError(data.error)
        }
    };
    xhr.send(fd);
}

function sendDirectory(files, method,summaryLength, returnType) {
    if (files.length < 1) {
        showError("Anna docx tiedosto tai copy-pastea tiivistettävä teksti.");
        document.getElementById("submit_button").disabled = false;
        return;
    }
    var fd = new FormData();
    for (var i = 0; i < files.length; i++) {
        var file = files[i]
        fd.append("file-"+i, file);
    }

    var xhr = new XMLHttpRequest();
    var path =  server_base_path + "/summarize/directory?summary_length="+summaryLength
                                    + "&method=" +method + "&return_type="+returnType
    xhr.open('POST', path, true);

    xhr.upload.onprogress = function(e) {
        if (e.lengthComputable) {
          var percentComplete = (e.loaded / e.total) * 100;
          console.log(percentComplete + '% uploaded');
        }
    };
    xhr.onload = function() {
        document.getElementById("in_progress").innerHTML = ""
        document.getElementById("submit_button").disabled = false;
        if (returnType == 'json') {
            var data = JSON.parse(this.responseText);
            if(data.success) {
                showMultiSectionSummary(data);
            } else {
                showError(data.error)
            }
        } else {
            // THIS IS REALLY UGLY WAY TO HANDLE
            // SHOULD BE HANDLED BY
            // Content-Type: Accept: text/plain or json or html
            // INSTEAD OF LOGIC IN CODE
            document.getElementById("error_output").innerHTML = ""
            document.getElementById("output_div").innerHTML = this.responseText
        }
    };
    xhr.send(fd);
}

function send(e) {
    e.preventDefault();
    clearCanvas();
    document.getElementById("submit_button").disabled = true;
    document.getElementById("output_div").innerHTML = ""

    document.getElementById("in_progress").innerHTML = "Lähetetty, tässä menee noin 1-2 minuuttia."
    var method = document.querySelector('input[name="method"]:checked').value;

    var returnJustification = document.querySelector('input[name="return_justification"]:checked').value;

    var textOrFile = document.querySelector('input[name="text_input_mode"]:checked').value;
    if (textOrFile == "copy_paste_input") {
        sendText(method,returnJustification)
    } else if(textOrFile == "directory_input") {
        var summaryLength = document.getElementById("dir_summary_length").value
        var files = document.getElementById("multiple_files").files
        sendDirectory(files, method, summaryLength, "png") //json
    } else {
        var isDocxFile = (textOrFile == "docx_file_upload_input")
        var fileId = isDocxFile ? "docx_file" : "txt_file"
        var lengthId = isDocxFile ? "docx_summary_length" : "txt_summary_length"
        var summaryLength = document.getElementById(lengthId).value
        var files = document.getElementById(fileId).files
        if( document.getElementById(fileId).files.length == 0 ){
            showError("Anna tiedosto tai syötä teksti.");
            document.getElementById("submit_button").disabled = false;
        } else {
            sendFile(files, method,summaryLength,returnJustification)
        }
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

    var textOrFile = document.querySelector('input[name="text_input_mode"]:checked').value;
    toggleTextInputField({value: textOrFile})
}

function toggleTextInputField(e) {
    if(e.value == "docx_file_upload_input") {
        document.getElementById("copy_paste_input").style.display = "none";
        document.getElementById("docx_file_upload_input").style.display = "block";
        document.getElementById("txt_file_upload_input").style.display = "none";
        document.getElementById("directory_input").style.display = "none";
        document.getElementById("return_justification").style.display = "none";
    } else if (e.value == "txt_file_upload_input") {
        document.getElementById("copy_paste_input").style.display = "none";
        document.getElementById("docx_file_upload_input").style.display = "none";
        document.getElementById("txt_file_upload_input").style.display = "block";
        document.getElementById("directory_input").style.display = "none";
        document.getElementById("return_justification").style.display = "none";
    } else if (e.value == "copy_paste_input") {
        document.getElementById("copy_paste_input").style.display = "block";
        document.getElementById("docx_file_upload_input").style.display = "none";
        document.getElementById("txt_file_upload_input").style.display = "none";
        document.getElementById("directory_input").style.display = "none";
        document.getElementById("return_justification").style.display = "block";
    } else {
        document.getElementById("copy_paste_input").style.display = "none";
        document.getElementById("docx_file_upload_input").style.display = "none";
        document.getElementById("txt_file_upload_input").style.display = "none";
        document.getElementById("directory_input").style.display = "block";
        document.getElementById("return_justification").style.display = "none";
    }
}

function enableSubmitting(e) {

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