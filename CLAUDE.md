# MTH 101 Simplified: project brief for Claude Code

Read this whole file before changing anything. It explains what we're building, why, and the rules that keep the lessons good.

## What this is

A study product for Nigerian university students, starting at UNIOSUN (Osun State University). Lecturers share long slide decks and PDFs and read through them without explaining. Students don't understand the material, and they fail.

We turn each course's lecture material into **narrated whiteboard lessons**: the board draws itself step by step while a Nigerian-accented teacher voice explains, uses everyday Nigerian examples, and stops to ask "pause and think" questions. Each module also has an interactive tool, practice questions with worked answers, and one-screen revision notes.

The first module is **MTH 101, Module 1: Set Theory**. Chemistry and physics modules come next.

**Pitch:** "Every course, every past question, already explained, so you just study and pass."

**The edge over ChatGPT:** it's not the AI. It's that the material for *this* school's courses is already explained, in the exam's format, with local examples, and with no prompting needed. Later, past questions per course will be the main reason people pay.

## Who it's for

- 100 and 200 level students first. Large shared courses (MTH, CHM, PHY, GST).
- They use **phones**, often cheap Android phones with limited data. Most open links from **WhatsApp**.
- Their English is Nigerian English. Plain words beat textbook words.

## Hard rules

1. **Stay anonymous.** No real names of the builder anywhere: not in code, comments, commit messages, page text, file names or site names. No lecturer names either.
2. **Never copy lecture slides word for word.** Teach the same topics in our own words and examples. Exercises can be restated and solved.
3. **Cover everything in the source material.** When building a module, list every topic from every slide or page first, then check every item is taught in a lesson. Note anything left out on purpose, and why.
4. **Mobile-first.** It must work at 360px wide on Android Chrome, iPhone Safari and WhatsApp's in-app browser. No sideways scrolling.
5. **One self-contained page per module.** HTML, CSS and JS live in `index.html`. The only external files are Google Fonts and the `audio/` folder. No frameworks, no build step.
6. **Keep it light.** Students have limited data. No images or video files; the board is drawn with SVG. Audio clips are small MP3s.
7. **Don't build general chat.** Every department already has a WhatsApp group.

## Files

```
index.html               the whole module: player, lessons, tabs, quiz, notes
audio/L1-S01-B1.mp3 ...  one narration clip per beat (generated, never hand-edited)
narration-script.txt     every beat's narration with its clip ID (generated from index.html)
gen_voice.py             makes the clips with edge-tts, Nigerian voice
tools/export_script.js   rebuilds narration-script.txt from index.html
render.yaml              Render static-site config (if present)
```

## How the lesson player works (inside index.html)

### Lesson data: `var CH = [ ... ]`

```js
{ title: 'Lesson title', steps: [            // a lesson
    [                                         // a step = one "screen"; the board is cleared between steps
      { say: "What the teacher says.",        // a beat = one sentence or two, plus what is drawn while saying it
        draw: function(){ B.title('...'); B.text(...); },
        hold: 4000 },                         // optional: thinking time in ms after a question, with a countdown on the board
      { say: "Next thing the teacher says." } // draw is optional
    ]
]}
```

- Beats play in order: the board animation and the voice run together, and the next beat starts when both have finished.
- When paused or skipped, all beats in a step are drawn at once and the caption shows the whole step's text.
- If two beats share an element (for example, shade something, then fade it), wrap the step in an IIFE that holds a variable: `(function(){ var s; return [ {...s = B.shade('a')...}, {...B.fade([s])...} ]; })()`
- Keep the markers `var CH = [` and `/* Voice */`. `tools/export_script.js` depends on them.

### Board: 640 × 400 SVG coordinates

The drawing API is `B`. Every call animates during playback and appears instantly when paused.

| Call | Use |
|---|---|
| `B.title(str)` | Blue heading, top-left (36, 58) |
| `B.text(x, y, str, o)` | Handwritten text, typed out letter by letter. `o.size` (default 30), `o.color`, `o.anchor:'middle'`, `o.weight:700`, `o.speed` (ms per character) |
| `B.circle(cx, cy, r, o)` | Marker circle drawn as a stroke |
| `B.line(x1, y1, x2, y2, o)` / `B.arrow(...)` / `B.path(d, o)` / `B.rrect(x, y, w, h, r, o)` | Strokes |
| `B.shade(region, o)` | Highlighter fill on the standard 2-circle Venn. Regions: `a`, `b`, `ab`, `out`. `o.color`, `o.op` (opacity) |
| `B.fade([els], o)` | Fade elements out |
| `B.wait(ms)` | Pause the timeline inside a beat |

Common options: `now:true` (draw instantly, for redrawing the base diagram), `keep:true` (start the next item at the same time), `gap` (ms before the next item), `at` (start time).

Colours: `ink`, `blue`, `red`, `green`, `muted`, `yellow`. Blue = main idea, red = warnings and traps, green = correct and memory lines, muted = side notes.

Helpers: `venn(o)` draws U and circles A and B (`o.la`/`o.lb` for labels, `o.part` to draw one piece, `o.animate`). `names()` places the seven hostel students. `room()` = venn + names, instantly. `result(str)` = the answer line at the bottom. `three(upto, animate)`, `writeNum(step)` and `calc(i, str)` handle the 3-circle word problem.

**Board layout rules:** title at the top-left, content between y = 100 and 380, and nothing past x = 610. Keep board text short: a symbol line or a few words. The full explanation goes in `say`, not on the board.

### Voice

- Each beat's clip ID is `L{lesson}-S{step, 2 digits}-B{beat}`, for example `L4-S03-B2`. The ID comes from the beat's **position**, so inserting or removing a step renumbers every clip after it.
- The player plays `audio/<id>.mp3` if it exists. If it doesn't, it falls back to the phone's speech voice. Captions always show.
- After ANY narration change or reordering:
  1. `node tools/export_script.js`
  2. Delete the affected mp3s. After a reorder, delete everything from the changed point onward, or the whole audio folder.
  3. `python gen_voice.py` (only missing clips are regenerated)
- Voices: `en-NG-AbeoNeural` (male, default) or `en-NG-EzinneNeural` (female). `edge-tts` is unofficial. Before charging money, move generation to Microsoft's official Azure Speech service, which has the same voices.

## How to write lessons (the most important section)

The voice must **teach like a good Nigerian lecturer**, not read text aloud.

- **One idea per beat**, one or two short sentences. The board shows the idea while the voice says it.
- **Talk to the class:** "Look at this." "Now watch." "Who can tell me…?" "Don't be that person."
- **Example before definition when possible**, and use things students know: the class WhatsApp group, the buka (rice with chicken or plantain), the hostel room (amala vs jollof), shirts and trousers, danfo, NEPA, data bundles. Keep the tone respectful and never use stereotypes.
- **Name the trap** students fall into, then show the fix.
- **"Pause and think" questions** every few steps: the question beat has `hold: 3000–4000`, and the next beat gives the answer and the reason.
- **Memory lines** that stick: "Break the bar, flip the sign." "Start from the middle, subtract your way out." "Item versus bag."
- **Write symbols as words in `say`.** The voice can't read ∪ or ⊆. Write "A union B", "is a subset of", "A prime", "the empty set", "two to the power n".
- **Numbers in `say` as words** where a voice might misread them ("twenty-six", "one hundred and six").
- **Avoid double quotes inside `say` strings** (they're delimited by double quotes). Use single quotes or rephrase.
- **End each lesson with a recap**, and point students to Practice.
- **Solve the exam-style exercises** from the source material step by step on the board.

## Page structure and design

- Deep-blue header with a graph-paper grid, then the whiteboard player as the centrepiece. The player has lesson chips, captions, controls, a voice picker and a step progress bar.
- Tabs underneath: **Try it** (interactive tool), **Practice** (10 multiple-choice questions, explanation shown after answering, score bar), **Quick notes** (tables of symbols, rules, laws, formulas and exercise answers).
- White background and blue design, single light theme. Tokens are in `:root`: `--blue #1d4ed8`, `--blue-deep #0a2a8a`, `--red #e0453a`, `--green #0f9d6b`, `--yellow #ffd84d`, `--ink #0b1b3a`.
- Fonts: Plus Jakarta Sans (headings), Inter (body), Kalam (whiteboard handwriting).
- Buttons at least 44px tall. Visible focus states. Respect `prefers-reduced-motion`.

## Building a new module (for example CHM 101)

1. Read the lecturer's PDF or slides completely. Write a **coverage list**: every topic, definition, formula and exercise, slide by slide.
2. Plan the lessons: 5–8 lessons, each with 4–12 steps, ordered from easiest to hardest. The hardest exam-style question gets its own lesson.
3. Copy this module's `index.html` as the template. Replace `CH`, the Try-it tool, the quiz questions and the notes. Keep the player engine untouched unless asked.
4. Check coverage against the list. Every item must be taught.
5. Run `node tools/export_script.js`, then `python gen_voice.py`.
6. Test at 360px wide. Step through every step while paused, check that no board text overlaps or runs past the edge, then play a full lesson.

## Testing checklist before every deploy

- [ ] No JavaScript errors in the console. Every step renders while paused and while playing.
- [ ] No board text overlaps, and nothing passes x = 610 or y = 395.
- [ ] Audio plays in time and the next clip starts without a long gap. With the audio folder removed, the phone-voice fallback works.
- [ ] Works at 360px wide with no horizontal scroll.
- [ ] `narration-script.txt` is up to date and the audio folder has one mp3 per clip ID.
- [ ] No real names anywhere.

## Deploying

Static site on Render from a **private** GitHub repo, with no build step, publishing the repo root, and long caching on `/audio/*`. Use a neutral service name (for example `mth101-simplified`). Commit the `audio/` folder.

## Roadmap (context, don't build unless asked)

1. **Now:** free MTH 101 Sets module, shared in class WhatsApp groups to test demand.
2. **Next:** more MTH 101 topics (quadratics, induction, binomial theorem, complex numbers, trigonometry, sequences), then CHM 101 and PHY 101.
3. **Later:** an app with a course library per school and department, past questions per course and year, CBT-style exam mode, and a Paystack subscription (₦1,500 a month, plus a ₦2,500 exam pass). Course reps get free access and ₦300 per referral.
