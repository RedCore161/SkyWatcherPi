==============
Sky-Watcher Pi
==============


Description
===========
This project let's you control your Canon-Camera over a web-interface
(build with django). It's designed to run on a Raspberry Pi 4 but
can also run on a PC without further changes.

The main purpose of this project is to give you an esay-to-use-tool
for astrophotography.

Note: This code is explorative, meaning i learned it by doing and have
no professional background in python or html/js/css. Security was no goal,
so please run it only on your local machine!


Features
========
* control your Canon-Camera over USB using gphoto2
* change all relevant settings of the camera and save them for later use
* create flows of CameraConfigs for automated capturing
* live-preview and full-video-capturing using ffmpeg
* only use selected area of the video to minimize filesize


TODOs
=====
* autoguider for telescope-mount using OpenCV


Hardware-Setup
==============
Content will follow soon!


Short instructions
==================
Better content will follow soon!

Install script 'init_project.sh' is not ready yet,
but it contains most of the important steps...


Steps for a fresh raspi
=======================
Better content will follow soon!

1.)	change keyboard layout if needed

2.)	setup network & connect with internet

3.)	activate ssh-server

4.)	login from your pc via ssh

5.)	copy files to raspi

6.)	take a look at 'init_project.sh' and modify variables in the header

7.)	run 'init_project.sh' as sudo

8.)	fill the gaps in the script...

9.)	start django server

10.) Profit!