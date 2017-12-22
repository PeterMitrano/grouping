from IPython.display import display,Audio,HTML

# for having playable audio
def show_playable_audio(path):
	html = "<audio controls><source src={} type='audio/mp3'></audio>".format(path)
	display(HTML(html))

def playable_audio(path):
	html = "<audio controls><source src={} type='audio/mp3'></audio>".format(path)
	return html
