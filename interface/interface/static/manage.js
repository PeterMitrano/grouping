window.onload = function() {
    $('#samples').change(add_samples);
}

let output_samples = [];
let input_samples = [];

function add_samples(e) {
    if (!e.target.files) {
        return;
    }

    let files = e.target.files
    for (let i = 0; i < files.length; i++) {
        let name = files[i].name;

        if (input_samples.indexOf(name) != -1) {
            alert("skipping duplicate file name: " + name);
            continue;
        }

        let new_audio_item = document.createElement("li");
        let new_audio = document.createElement("AUDIO");
        let new_src = document.createElement("source");
        let checkbox = document.createElement("input");
        let text = document.createTextNode(name);
        new_audio.setAttribute("style", "width:90%");
        checkbox.type="checkbox";
        checkbox.setAttribute("style", "margin-left:30px");
        checkbox.onchange = function() {
            if (this.checked) {
                output_samples.push(name);
            }
            else {
                output_samples.pop(name);
            }
        };
        new_src.type = "audio/mpeg";
        new_src.src = "static/all_samples/" + name;
        new_audio.controls = true;
        new_audio.load();
        new_audio.appendChild(new_src);
        new_audio_item.className = "list-group-item";
        new_audio_item.appendChild(text);
        new_audio_item.appendChild(new_audio);
        new_audio_item.appendChild(checkbox);
        $("#input_samples").append(new_audio_item);
        input_samples.push(name);
    }
}

function download() {
    text = output_samples.join("\n");

    let element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    element.setAttribute('download', "filtered_samples.csv");

    element.style.display = 'none';
    document.body.appendChild(element);

    element.click();

    document.body.removeChild(element);
}