let audio = document.getElementById('audio');
let audio_src = document.getElementById('audio_source');
let canvas = document.getElementById('canvas');
let sample_idx = 0;
let responses = [];
let background_color = '#D9EDF7';
let start_time = 0;
let marker_id_counter = 0;
let trial_id = generateID();

function Action(type, id) {
  return {
    'type': type,
    'id': id
  };
}

function Response() {
  return {
    'final_response': [],
    'edit_history': []
  }
}

/////////////////////////////////////////////////////////
// Setup
/////////////////////////////////////////////////////////

window.onload = function() {
  sample_idx = 0;
  audio_src.src = samples[sample_idx]['url'];
  audio.load();
  audio.loop = true;
  $('#interface').css('background', background_color);
  start_time = new Date().getTime();

  responses.push(Response());

  make_interface();
};

/////////////////////////////////////////////////////////
// Keyboard Shortcuts
/////////////////////////////////////////////////////////
Mousetrap.bind('s', scrub_back);
Mousetrap.bind('a', play_pause);

/////////////////////////////////////////////////////////
// Audio Player
/////////////////////////////////////////////////////////

function play_pause() {
  if (audio.paused) {
    audio.play();
  }
  else {
    audio.pause();
  }
}

setInterval(function() {
  // set scrubber position
  if (audio.duration > 0) {
    let x = current_time_to_x();
    Interface.scrubber.x(x);
    Interface.layer.draw();
  }
}, 25);

function current_time_to_x() {
  return Interface.line_begin + audio.currentTime / audio.duration * (Interface.line_end - Interface.line_begin);
}

function x_to_time(x) {
  return (x - Interface.line_begin) / (Interface.line_end - Interface.line_begin) * audio.duration;
}

function timeFmt(t) {
  return (t / 60).toFixed(0).padStart(2, '0') + ':' +
      t.toFixed(0).padStart(2, '0');
}

audio.addEventListener('play', function() {
  let icon = $('#pause_play_button > span');
  icon.removeClass('glyphicon-play');
  icon.addClass('glyphicon-pause');
});

audio.addEventListener('suspend', function() {
  let icon = $('#pause_play_button > span');
  icon.addClass('glyphicon-play');
  icon.removeClass('glyphicon-pause');
});

audio.addEventListener('pause', function() {
  let icon = $('#pause_play_button > span');
  icon.addClass('glyphicon-play');
  icon.removeClass('glyphicon-pause');
});

function scrub_back() {
    audio.currentTime -= 1;
}

function next_submit() {
  // pause the music
  audio.pause()

  // save the current responses for this sample
  for (let i = 0; i < Interface.markers.length; i++) {
    responses[sample_idx]['final_response'].push(x_to_time(Interface.markers[i].x()));
  }

  // clear current markers
  let i = Interface.markers.length - 1;
  for (; i >= 0; i--) {
    Interface.markers[i].destroy();
    Interface.markers.splice(i, 1);
  }
  Interface.layer.draw();

  if (sample_idx === samples.length - 1) {
    $('#next-submit-button').prop('disabled', true);

    // HTTP POST to server
    let request = new XMLHttpRequest();
    let finish_time = new Date().getTime();
    let metadata = {
      // 'trial time': (finish_time - start_time) / 1000.0,
      'tiral-id': trial_id
    };
    let post_data = {
      'metadata': metadata,
      'samples': samples,
      'responses': responses,
    };
    let url = "/responses";
    request.open('POST', url, true);
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.send(JSON.stringify(post_data));

    // FIXME: redirect to debriefing page
    // window.location.href = 'thankyou.html?trial-id=' + trial_id;
  }
  else {
    // load the next sample
    sample_idx += 1;
    audio_src.src = samples[sample_idx]['url'];
    audio.load();

    // create response object for new trial
    responses[sample_idx] = Response();

    // init interface
    init_interface();

    // change next button to submit button if it's the last sample
    if (sample_idx === samples.length - 1) {
      $('#next-submit-button').prop('innerHTML', 'Submit');
    }
  }
}

/////////////////////////////////////////////////////////
// Konva Canvas
/////////////////////////////////////////////////////////
let Interface = {};

function make_interface() {
    let width =  $('#interface').width() - 100;
    let height = 50;

    Interface.stage = new Konva.Stage({
      container: 'canvas',
      width: width,
      height: height,
      fill: '#ff0',
    });

    Interface.layer = new Konva.Layer();
    let radius = 9;
    let stroke = 2;
    Interface.marker_small = 6;
    Interface.marker_large = 9;
    Interface.line_height = 2;
    Interface.line_begin = 10;
    Interface.line_end = width - 10;

    let line = new Konva.Rect({
      x: Interface.line_begin,
      y: Interface.stage.getHeight() / 2 - Interface.line_height / 2,
      width: Interface.line_end - Interface.line_begin,
      height: Interface.line_height,
      fill: '#666',
    });
    Interface.layer.add(line);

    let background = new Konva.Rect({
      x: 0,
      y: 0,
      width: Interface.stage.getWidth(),
      height: Interface.stage.getHeight(),
      fill: background_color,
    });
    Interface.layer.add(background);

    let scrubber_radius = 8;
    Interface.scrubber = new Konva.Rect({
      x: Interface.line_begin,
      y: Interface.stage.getHeight() / 2 - 15,
      width: 3,
      height: 30,
      fill: '#222',
    });

    Interface.layer.add(Interface.scrubber);

    Interface.marker = new Konva.Circle({
      x: Interface.stage.getWidth() / 2,
      y: Interface.stage.getHeight() / 2,
      radius: radius,
      fill: '#4285F422',
      stroke: '#4285F4',
      strokeWidth: stroke,
      draggable: true,
      dragBoundFunc: function(pos) {
        // called every time the object is dragged
        this.was_dragging = true;
        return {
          x: bound(pos.x),
          y: this.getAbsolutePosition().y,
        };
      },
    });

    Interface.marker.marker_id = marker_id_counter++;

    Interface.marker.on('mousedown', function() {
    });

    Interface.marker.on('mouseup', function() {
        // end of drag
        if (this.was_dragging) {
          responses[sample_idx]['edit_history'].push(Action("drag", this.marker_id));
        }
        this.was_dragging = false;
    });

    Interface.marker.on('mouseover', function() {
      document.body.style.cursor = 'pointer';
    });

    Interface.marker.on('mouseout', function() {
      document.body.style.cursor = 'default';
    });

    Interface.marker.on('click', function(event) {
      if (event.evt.shiftKey) {
        // delete the marker
        responses[sample_idx]['edit_history'].push(Action("delete", this.marker_id));
        this.destroy();
        Interface.layer.draw();
        let idx = Interface.markers.indexOf(this);
        if (idx > -1) {
          Interface.markers.splice(idx, 1);
        }
      }
      else if (event.evt.altKey) {
        // resize the marker
        responses[sample_idx]['edit_history'].push(Action("resize", this.marker_id));
        if (this.radius() === Interface.marker_small) {
          this.setRadius(Interface.marker_large);
          Interface.layer.draw();
        }
        else {
          this.setRadius(Interface.marker_small);
          Interface.layer.draw();
        }
      }
    });

    Interface.layer.on('click', function(event) {
      if (event.evt.metaKey) {
        // insert new marker
        let x = Interface.stage.getPointerPosition().x;
        if ((x > Interface.line_begin) && (x < Interface.line_end)) {
          let new_marker = add_marker(x);
          responses[sample_idx]['edit_history'].push(Action("add", new_marker.marker_id));
        }
      } else {
        // do nothing on normal click
      }
    });

    background.setZIndex(0);
    line.setZIndex(1);
    Interface.markers = [];
    init_interface();
    Interface.stage.add(Interface.layer);
}

function init_interface() {
// Optional: uncomment to add an initial marker in the center
//  add_marker((Interface.line_end + Interface.line_begin) / 2);
}

function bound(x) {
  return Math.max(Interface.line_begin, Math.min(Interface.line_end, x));
}

function add_marker(x_pos) {
  let clone = Interface.marker.clone({
    x: x_pos,
    y: Interface.stage.getHeight() / 2,
  });
  clone.marker_id = marker_id_counter++;
  Interface.layer.add(clone);
  Interface.layer.draw();
  Interface.markers.push(clone);
  return clone;
}

function generateID() {
  let id = getRandomHex();
  for (let i =0; i < 8; i++) {
    id += "::";
    id += getRandomHex();
  }
  return id;
}

function getRandomHex() {
  hex = Math.floor(Math.random() * (Math.pow(2, 8) + 1)).toString(16);
  if (hex.length < 2) {
    hex = "0" + hex;
  }
  return hex;
}
