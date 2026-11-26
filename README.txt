MTH 101 SIMPLIFIED: SETS (narrated whiteboard lessons)

Files
  index.html              the whole module (lessons, Try it, Practice, Quick notes)
  audio/<clip id>.mp3     one narration clip per beat (generated)
  narration-script.txt    every beat's narration with its clip ID (generated)
  gen_voice.py            makes the clips with edge-tts (Nigerian voice)
  tools/export_script.js  rebuilds narration-script.txt from index.html
  render.yaml             Render static-site config

After changing any lesson narration in index.html
  1. node tools/export_script.js
  2. Delete the mp3s of the changed clips. If steps were added or removed,
     delete the whole audio folder, because clip IDs renumber.
  3. py gen_voice.py
     (default voice: en-NG-AbeoNeural, normal speed, pitch -3Hz.
      Only missing clips are made. If some fail, run it again.)

Test locally
  py -m http.server 8000   then open http://localhost:8000

Deploy
  Push to GitHub. Render rebuilds the static site automatically.
