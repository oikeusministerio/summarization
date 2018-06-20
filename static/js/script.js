
function send(e) {
    e.preventDefault();
    document.getElementById("submit_button").disabled = true;

    var content = document.getElementById("content").value
    document.getElementById("output_div").innerHTML = ""
    var summary_length = document.getElementById("summary_length").value
    document.getElementById("in_progress").innerHTML = "Lähetetty, tässä menee noin 1-2 minuuttia."

    var method = document.querySelector('input[name="method"]:checked').value;

    var xhr = new XMLHttpRequest();
    xhr.open("POST", "http://localhost:5000/summarize", true);
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

function setup() {
    document.getElementById("submit_button").addEventListener("click", send);

    document.getElementById("copy_paste_input").style.display = "none";
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