let input; // INPUT: This is the entire JSON dict
let sample_url; // INPUT: This is the URL of the sample

let dataset = input['dataset'];

let responses = dataset.map(function(response) {
  if (response['url'] === sample_url) {
    return response['data']['final_response'].map(function(marker) {
      return marker['timestamp'];
    });
  }
});

return responses; // OUTPUT: a list of lists of marker locations (in seconds)
