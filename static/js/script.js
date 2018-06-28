
var server_base_path = 'http://localhost:5000'

function sendText(method,summary_length,returnJustification) {
    var content = document.getElementById("content").value
    var xhr = new XMLHttpRequest();
    xhr.open("POST", server_base_path + "/summarize", true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({
        content: content,
        summary_length: summary_length,
        minimum_distance: 0.1,
        method: method,
        return_justification:returnJustification
    }));
    xhr.onload = function() {
      document.getElementById("in_progress").innerHTML = ""
      document.getElementById("submit_button").disabled = false;
      var data = JSON.parse(this.responseText);
      if(data.success) {
        if (method == 'graph' && returnJustification == "True") {
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

function sendFile(method,summary_length) {
    var files = document.getElementById("file").files
    if (files.length < 1) {
        showError("Anna docx tiedosto tai copy-pastea tiivistettävä teksti.");
        document.getElementById("submit_button").disabled = false;
        return;
    }
    var file = files[0]
    var fd = new FormData();
    fd.append("file", file);

    var xhr = new XMLHttpRequest();
    var path =  server_base_path + "/summarize/file?summary_length="+summary_length
                                    + "&method=" +method+ "&minimum_distance=0.1"
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

function send(e) {
    e.preventDefault();
    clearCanvas();
    document.getElementById("submit_button").disabled = true;
    document.getElementById("output_div").innerHTML = ""

    var summary_length = document.getElementById("summary_length").value
    document.getElementById("in_progress").innerHTML = "Lähetetty, tässä menee noin 1-2 minuuttia."
    var method = document.querySelector('input[name="method"]:checked').value;

    var returnJustification = document.querySelector('input[name="return_justification"]:checked').value;

    var textOrFile = document.querySelector('input[name="text_input_mode"]:checked').value;
    if (textOrFile == "file_upload_input") {
        if( document.getElementById("file").files.length == 0 ){
            showError("Anna tiedosto tai syötä teksti.");
        } else {
            sendFile(method,summary_length,returnJustification)
        }
    } else {
        sendText(method,summary_length,returnJustification)
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
    var output = "VALITTIIN LAUSEET : " + positions + "<br> <br> "
    if (hasRanking) {
        output += "LEX-RANK ranking " + ranking + "<br> <br>"
    }
    output += "TIIVISTELMÄ: \n" + text
    document.getElementById("output_div").innerHTML = output
}

function showMultiSectionSummary(data) {
    document.getElementById("error_output").innerHTML = ""
    htmlOutput = "<div>"
    for (var i in data.titles) {
        var title = data.titles[i]
        htmlOutput += "<h3>" + title + "</h3>"
        htmlOutput += "<p>" + data[title].summary + "</p>"
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
    if(e.value == "file_upload_input") {
        document.getElementById("copy_paste_input").style.display = "none";
        document.getElementById("file_upload_input").style.display = "block";
        document.getElementById("return_justification").style.display = "none";
    } else {
        document.getElementById("copy_paste_input").style.display = "block";
        document.getElementById("file_upload_input").style.display = "none";
        document.getElementById("return_justification").style.display = "block";
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