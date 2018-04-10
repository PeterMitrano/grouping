let audio = document.getElementById('audio');
let audio_src = document.getElementById('audio_source');
let canvas = document.getElementById('canvas');
let sample_idx = 0;
let responses = [];
let background_color = '#D9EDF7';
let start_time = 0;
let marker_id_counter = 0;
let trial_start_time;

function Action(type, id) {
  return {
    'type': type,
    'id': id,
  };
}

function Response() {
  return {
    'final_response': [],
    'edit_history': [],
    'duration_seconds': -1,
  };
}

/////////////////////////////////////////////////////////
// Setup
/////////////////////////////////////////////////////////

window.onload = function() {
  sample_idx = 0;
  audio_src.src = samples[sample_idx]['url'];
  audio.load();
  audio.loop = true;
  let iface = $('#interface');
  iface.css('background', background_color);
  start_time = new Date().getTime();

  responses.push(Response());

  make_interface();

  // update progress indicator
  $("#progress_indicator").html("Sample " + (sample_idx+1) + "/" + samples.length);

  iface.hide();
};

function show_interface() {
  $('#confirm').hide();
  $('#interface').show();

  // also start timer for first trial here
  trial_start_time = new Date();
}

/////////////////////////////////////////////////////////
// Keyboard Shortcuts
/////////////////////////////////////////////////////////
Mousetrap.bind('a', play_pause);
Mousetrap.bind('space', play_pause);
Mousetrap.bind('space', squelch, 'keyup');
Mousetrap.bind('s', add_marker_at_scrubber);
Mousetrap.bind('d', scrub_back);

/////////////////////////////////////////////////////////
// Audio Player
/////////////////////////////////////////////////////////

function squelch(e) {
  if (e.preventDefault) {
    e.preventDefault();
  } else {
    // internet explorer
    e.returnValue = false;
  }
}

function play_pause(e) {
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
}, 30);

setInterval(function() {
  check_disable_button();
}, 100);

function current_time_to_x() {
  return Interface.line_begin + audio.currentTime / audio.duration *
      (Interface.line_end - Interface.line_begin);
}

function x_to_time(x) {
  return (x - Interface.line_begin) / (Interface.line_end - Interface.line_begin) * audio.duration;
}

function timeFmt(t) {
  return (t / 60).toFixed(0).padStart(2, '0') + ':' +
      t.toFixed(0).padStart(2, '0');
}

audio.addEventListener('play', function() {
  let icon = $('#pause_play_button').find('> span');
  icon.removeClass('glyphicon-play');
  icon.addClass('glyphicon-pause');
});

audio.addEventListener('pause', function() {
  let icon = $('#pause_play_button').find('> span');
  icon.addClass('glyphicon-play');
  icon.removeClass('glyphicon-pause');
});

function scrub_back() {
  if (audio.currentTime - 1 < 0) {
    audio.currentTime = audio.duration - (1 - audio.currentTime);
  }
  else {
    audio.currentTime -= 1;
  }
}

function next_submit() {
  // pause the music
  audio.pause();

  // disable the next/submit button
  $('#next-submit-button').prop('disabled', true);

  // save the current responses for this sample
  for (let i = 0; i < Interface.markers.length; i++) {
    let m = Interface.markers[i];
    let timestamp = x_to_time(m.x());
    if (isNaN(timestamp)) {
      timestamp = 9999999; // error handling in case someone places a marker _really_ fast
    }
    let marker_info = {'timestamp': timestamp};
    if (m.radius() === Interface.marker_large) {
      marker_info.size = 'large';
    }
    else if (m.radius() === Interface.marker_small) {
      marker_info.size = 'small';
    }
    responses[sample_idx]['final_response'].push(marker_info);
  }

  // clear current markers
  let i = Interface.markers.length - 1;
  for (; i >= 0; i--) {
    Interface.markers[i].destroy();
    Interface.markers.splice(i, 1);
  }
  Interface.layer.draw();

  // save how long it took to complete this sample
  let now = new Date();
  responses[sample_idx]['duration_seconds'] = (now.getTime() - trial_start_time.getTime()) / 1000.0;
  trial_start_time = now;

  if (sample_idx === samples.length - 1) {
    $('#next-submit-button').prop('disabled', true);

    // HTTP POST to server
    let request = new XMLHttpRequest();
    let finish_time = new Date().getTime();
    let metadata = {
    };
    let post_data = {
      'metadata': metadata,
      'experiment_id': experiment_id,
      'samples': samples,
      'responses': responses,
    };
    let url = '/responses';
    request.open('POST', url, true);
    request.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
    request.send(JSON.stringify(post_data));

    // FIXME: redirect to debriefing page
    window.location.href = next_href;
  }
  else {

    // load the next sample
    sample_idx += 1;
    audio_src.src = samples[sample_idx]['url'];
    audio.load();

    // create response object for new trial
    responses[sample_idx] = Response();

    // update progress indicator
    $("#progress_indicator").html("Sample " + (sample_idx+1) + "/" + samples.length);

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
  let width = $('#interface').width() - 100;
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
      return {
        x: bound(pos.x),
        y: this.getAbsolutePosition().y,
      };
    },
  });

  Interface.marker.marker_id = marker_id_counter++;

  Interface.marker.on('dragend', function() {
    let action = {
      'type': 'drag',
      'id': this.marker_id,
      'to': x_to_time(this.x())
    };
    responses[sample_idx]['edit_history'].push(action);
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
      let action = {
        'type': 'delete',
        'id': this.marker_id,
      };
      responses[sample_idx]['edit_history'].push(action);
      this.destroy();
      Interface.layer.draw();
      let idx = Interface.markers.indexOf(this);
      if (idx > -1) {
        Interface.markers.splice(idx, 1);
      }
    }
    else if (event.evt.altKey) {
      // resize the marker
      let action = {
        'type': 'resize',
        'id': this.marker_id,
      };
      if (this.radius() === Interface.marker_small) {
        this.setRadius(Interface.marker_large);
        Interface.layer.draw();
        action['size'] = Interface.marker_large;
      }
      else {
        this.setRadius(Interface.marker_small);
        action['size'] = Interface.marker_small;
        Interface.layer.draw();
      }
      responses[sample_idx]['edit_history'].push(action);
    }
  });

  Interface.layer.on('click', function(event) {
    insert_key_combo = false;
    if (navigator.appVersion.indexOf("Win") != -1 && event.evt.ctrlKey) {
      insert_key_combo = true;
    }
    else if (event.evt.metaKey) {
      insert_key_combo = true;
    }

    if (insert_key_combo) {
      // insert new marker
      let x = Interface.stage.getPointerPosition().x;
      if ((x > Interface.line_begin) && (x < Interface.line_end)) {
        let new_marker = add_marker(x);
        let action = {
          'type': 'add',
          'id': new_marker.marker_id,
          'at': x_to_time(x)
        };
        responses[sample_idx]['edit_history'].push(action);
      }
    } else {
      // do nothing on normal click
    }
  });

  background.setZIndex(0);
  line.setZIndex(1);
  Interface.markers = [];
  Interface.stage.add(Interface.layer);
  Interface.loaded = true;
}

function bound(x) {
  return Math.max(Interface.line_begin, Math.min(Interface.line_end, x));
}

function add_marker_at_scrubber() {
    let new_marker = add_marker(current_time_to_x());
    let action = {
      'type': 'add',
      'id': new_marker.marker_id,
      'at': x_to_time(new_marker.x())
    };
    responses[sample_idx]['edit_history'].push(action);
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

function check_disable_button() {
  let trial_duration_ms = 0;
  if (trial_start_time) {
      let now = new Date();
      trial_duration_ms = (now.getTime() - trial_start_time.getTime());
  }
  if ((Interface.loaded && Interface.markers.length == 0) || trial_duration_ms < 1000) {
    $('#next-submit-button').prop('disabled', true);
  }
  else {
    $('#next-submit-button').prop('disabled', false);
  }
}
