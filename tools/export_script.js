// Rebuilds narration-script.txt from the lesson data in index.html.
// Run after ANY change to lesson narration:   node tools/export_script.js
// Then regenerate only the changed clips (delete their mp3s first):   python gen_voice.py

const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const js = html.slice(html.indexOf('<script>') + 8, html.lastIndexOf('</script>'));

const start = js.indexOf('var CH = [');
const end = js.indexOf('/* Voice */');
if (start < 0 || end < 0) {
  console.error('Could not find "var CH = [" and "/* Voice */" in index.html. Keep those markers in place.');
  process.exit(1);
}

// Evaluate only the lesson array; drawing helpers are stubbed because we only need the narration.
const noop = () => {};
const B = new Proxy({}, { get: () => noop });
const body = js.slice(start + 'var CH = '.length, end).trim().replace(/;\s*$/, '');
const CH = new Function('B', 'venn', 'names', 'room', 'result', 'three', 'writeNum', 'calc', 'return ' + body)(
  B, noop, noop, noop, noop, noop, noop, noop
);

const pad = (n) => (n < 10 ? '0' : '') + n;
let out = 'Narration script\nOne line per audio clip. Save each clip as the ID shown, e.g. L1-S01-B1.mp3\n\n';
let clips = 0;
CH.forEach((lesson, i) => {
  out += `==== Lesson ${i + 1}: ${lesson.title} ====\n\n`;
  lesson.steps.forEach((step, j) => {
    step.forEach((beat, k) => {
      clips++;
      out += `L${i + 1}-S${pad(j + 1)}-B${k + 1}\n${beat.say}\n\n`;
    });
  });
});

fs.writeFileSync(path.join(root, 'narration-script.txt'), out);
console.log(`Wrote narration-script.txt: ${CH.length} lessons, ${clips} clips.`);
