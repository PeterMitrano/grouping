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
  fill: '#ff0',
});

let layer = new Konva.Layer();
let radius = stage.getWidth() / 100;
let stroke = 2;
let line_height = 2;

let line = new Konva.Rect({
  x: 0,
  y: stage.getHeight() / 2 - line_height / 2,
  width: stage.getWidth(),
  height: line_height,
  fill: '#666',
});
layer.add(line);

let background = new Konva.Rect({
  x: 0,
  y: 0,
  width: stage.getWidth(),
  height: stage.getHeight(),
  fill: '#fafafa',
});
layer.add(background);

let marker = new Konva.Circle({
  x: stage.getWidth() / 2,
  y: stage.getHeight() / 2,
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
marker.on('click', function(event) {
  if (event.evt.shiftKey) {
    this.destroy();
    layer.draw();
  }
});

layer.on('click', function(event) {
  if (event.evt.ctrlKey) {
    // insert new marker
    add_marker(stage.getPointerPosition().x);
  } else {
    // do nothing on normal click
  }
});

add_marker(10, layer);

background.setZIndex(0);
line.setZIndex(1);
stage.add(layer);

function add_marker(x_pos) {
  let clone = marker.clone({
    x: x_pos,
    y: stage.getHeight() / 2,
  });
  layer.add(clone);
  layer.draw();
}
