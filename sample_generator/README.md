# Sample Generator

This directory contains a script to generate a folder full of samples given a bunch of MP3 files. First, put your MP3 files in a folder somewhere convenient. Next, run the following command.

    python sample_generator.py folder_of_mp3/*.mp3 output_samples_folder

You can then go to the webserver and go to the `manage` page, load all those samples, and filter them. To filter, check the ones you want to keep, then hit download. This will download a simple CSV file listing all the samples you checked off. You can use this file to copy samples from your output folder to a seperate folder with this command:

    cd output_samples_folder
    mkdir filtered_samples
    cat ~/Downloads/filtered_samples.csv | xargs cp -t filtered_samples

