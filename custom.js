let audio = document.getElementById('audio');
let canvas = document.getElementById('canvas');

function set_loop() {
  audio.loop = document.getElementById('loop_check').checked;
}

let width = 700;
let height = 100;

let stage = new Konva.Stage({
  container: 'canvas',
  width: width,
  height: height,
});

let layer = new Konva.Layer();
let radius = stage.getWidth() / 100;
let stroke = 2;
let line_height = 2;

function add_marker(x_pos, y_pos, layer) {
  let marker = new Konva.Circle({
    x: x_pos,
    y: y_pos,
    radius: radius,
    fill: '#00000055',
    stroke: 'black',
    strokeWidth: stroke,
    draggable: true,
    dragBoundFunc: function(pos) {
      return {
        x: Math.max(radius + stroke,
            Math.min(stage.getWidth() - radius - stroke, pos.x)),
        y: this.getAbsolutePosition().y,
      };
    },
  });

  marker.on('mouseover', function() {
    document.body.style.cursor = 'pointer';
  });
  marker.on('mouseout', function() {
    document.body.style.cursor = 'default';
  });

  layer.add(marker);
}

stage.on('contentClick', function(event) {
  if (event.evt.ctrlKey) {
    // insert new marker
    add_marker(event.evt.x, event.evt.y, layer);
  } else if (event.evt.shiftKey) {
    // delete marker
  } else {
    console.log(layer.shapes);
    // do nothing on normal click
  }
});

let line = new Konva.Rect({
  x: 0,
  y: stage.getHeight() / 2 - line_height / 2,
  width: stage.getWidth(),
  height: line_height,
  fill: '#666',
});

layer.add(line);
stage.add(layer);
