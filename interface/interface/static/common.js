function generateTrialID() {
  let id = getRandomHex();
  for (let i = 0; i < 8; i++) {
    id += '::';
    id += getRandomHex();
  }
  return id;
}

function getRandomHex() {
  let hex = Math.floor(Math.random() * (Math.pow(2, 8) - 1)).toString(16);
  if (hex.length < 2) {
    hex = '0' + hex;
  }
  return hex;
}

function getTrialID() {
  let params = new URLSearchParams(window.location.search);
  if (params.has('trial-id')) {
    return params.get('trial-id');
  }
  return "No Trial ID";
}

function copyToClipboard(element) {
    var $temp = $("<input>");
    $("body").append($temp);
    $temp.val($(element).text()).select();
    document.execCommand("copy");
    $temp.remove();
}
