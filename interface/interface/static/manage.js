window.onload = function() {
    for (let i=0; i < samples.length; ++i) {
        sample = samples[i]
        add_sample(sample['url'], sample['name']);
    }

    for (let i=0; i < db_samples.length; ++i) {
        db_sample = db_samples[i]
        add_db_sample(db_sample['url'], db_sample['count']);
    }
}

let output_samples = [];

function add_db_sample(url, count) {
    let new_db_sample_item = document.createElement("li");
    new_db_sample_item.className = "list-group-item";
    let text = document.createTextNode(url + "......." + count);
    new_db_sample_item.appendChild(text);
    $("#db_samples").append(new_db_sample_item);
}

function add_sample(url, name) {
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
    new_src.src = url;
    new_audio.controls = true;
    new_audio.load();
    new_audio.appendChild(new_src);
    new_audio_item.className = "list-group-item";
    new_audio_item.appendChild(text);
    new_audio_item.appendChild(new_audio);
    new_audio_item.appendChild(checkbox);
    $("#input_samples").append(new_audio_item);
}

function download() {
    text = output_samples.join("\n") + "\n";

    let element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    element.setAttribute('download', "index.txt");

    element.style.display = 'none';
    document.body.appendChild(element);

    element.click();

    document.body.removeChild(element);
}