let audio = document.getElementById('audio');
let canvas = document.getElementById('canvas');

function set_loop() {
  audio.loop = document.getElementById('loop_checkbox').checked;
}

let width = 800;
let height = 100;

let stage = new Konva.Stage({
  container: 'canvas',
  width: width,
  height: height,
  fill: '#ff0',
});

let layer = new Konva.Layer();
let radius = stage.getWidth() / 80;
let stroke = 2;
let line_height = 2;
let line_begin = 107;
let line_end = width - 157;

let line = new Konva.Rect({
  x: line_begin,
  y: stage.getHeight() / 2 - line_height / 2,
  width: line_end - line_begin,
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
  fill: '#4285F422',
  stroke: '#4285F4',
  strokeWidth: stroke,
  draggable: true,
  dragBoundFunc: function(pos) {
    return {
      x: bound(pos.x),
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
    let x = stage.getPointerPosition().x;
    if ((x > line_begin) &&
        (x < line_end)) {
      add_marker(x);
    }
  } else {
    // do nothing on normal click
  }
});

background.setZIndex(0);
line.setZIndex(1);
add_marker((line_end + line_begin) / 2);
stage.add(layer);

function bound(x) {
  return Math.max(line_begin,
      Math.min(line_end, x));
}

function add_marker(x_pos) {
  let clone = marker.clone({
    x: x_pos,
    y: stage.getHeight() / 2,
  });
  layer.add(clone);
  layer.draw();
}
