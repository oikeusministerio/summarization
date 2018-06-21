
var server_base_path = 'http://localhost:5000'

function sendText(method,summary_length) {
    var content = document.getElementById("content").value
    var xhr = new XMLHttpRequest();
    xhr.open("POST", server_base_path + "/summarize", true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({
        content: content,
        summary_length: summary_length,
        minimum_distance: 0.1,
        method: method
    }));
    xhr.onload = function() {
      document.getElementById("in_progress").innerHTML = ""
      document.getElementById("submit_button").disabled = false;
      var data = JSON.parse(this.responseText);
      if(data.success) {
        showSummary(data.summary, data.positions);
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
    document.getElementById("submit_button").disabled = true;
    document.getElementById("output_div").innerHTML = ""

    var summary_length = document.getElementById("summary_length").value
    document.getElementById("in_progress").innerHTML = "Lähetetty, tässä menee noin 1-2 minuuttia."
    var method = document.querySelector('input[name="method"]:checked').value;

    var textOrFile = document.querySelector('input[name="text_input_mode"]:checked').value;
    if (textOrFile == "file_upload_input") {
        sendFile(method,summary_length)
    } else {
        sendText(method,summary_length)
    }
}

// modify this to more pretty
function showError(text) {
    document.getElementById("error_output").innerHTML = text
    document.getElementById("output_div").innerHTML = ""
}

// modify this to more pretty
function showSummary(text, positions) {
    document.getElementById("error_output").innerHTML = ""
    var output = "VALITTIIN LAUSEET : " + positions + "<br> <br> TIIVISTELMÄ: \n" + text
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
    } else {
        document.getElementById("copy_paste_input").style.display = "block";
        document.getElementById("file_upload_input").style.display = "none";
    }
}