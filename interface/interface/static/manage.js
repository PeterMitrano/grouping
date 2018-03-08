let sample_map = {};

window.onload = function() {
    for (let i=0; i < samples.length; ++i) {
        let sample = samples[i];
        add_sample(sample['url'], sample['name']);
    }

    // check all the samples that are already in the database
    for (let i=0; i < db_samples.length; ++i) {
        let db_sample = db_samples[i];
        let list_element = sample_map[db_sample['url']];
        let checkbox = $(list_element.getElementsByTagName("input"));
        checkbox.prop("checked", true);
    }
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
    new_src.type = "audio/mpeg";
    new_src.src = url;
    new_audio.controls = true;
    new_audio.load();
    new_audio.appendChild(new_src);
    new_audio_item.className = "list-group-item";
    new_audio_item.appendChild(text);
    new_audio_item.appendChild(checkbox);
    new_audio_item.appendChild(new_audio);
    $("#input_samples").append(new_audio_item);
    sample_map[url] = new_audio_item
}

function update() {
    // send a request to the app asking to add or remove various files
    let selected_samples = [];
    let unselected_samples = [];

    for (let i=0; i < samples.length; ++i) {
        let sample = samples[i];
        let list_element = sample_map[sample['url']];
        let checkbox = $(list_element.getElementsByTagName("input"));
        if (checkbox.prop("checked")) {
            selected_samples.push(sample['url']);
        } else {
            unselected_samples.push(sample['url']);
        }
    }

    let post_data = {
        'selected_samples': selected_samples,
        'unselected_samples': unselected_samples
    };
    let url = '/manage';
    let request = new XMLHttpRequest();
    request.open('POST', url, true);
    request.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
    request.send(JSON.stringify(post_data));

    // refresh the page once the request has finished
    request.onreadystatechange = function() {
        location.reload();
    }
}

function download() {
    let text = "";

    for (let i=0; i < samples.length; ++i) {
        let sample = samples[i];
        let list_element = sample_map[sample['url']];
        let checkbox = $(list_element.getElementsByTagName("input"));
        if (checkbox.prop("checked")) {
            text += sample['name'] + "\n";
        }
    }

    let element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    element.setAttribute('download', "index.txt");

    element.style.display = 'none';
    document.body.appendChild(element);

    element.click();

    document.body.removeChild(element);
}
