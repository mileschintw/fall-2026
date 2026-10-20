// One Canvas file as base64 (the original PDF for an assignment spec). On https://canvas.uw.edu/courses/<COURSE>:
//   python scripts/pw_run.py scripts/browser/canvas_file.js state/_file.tmp --pre "window.COURSE=1917398; window.FILE_ID=154350654" --url https://canvas.uw.edu/courses/1917398
// Returns {file_id, name, size, updated_at, b64}. The download URL (it carries a verifier token) stays in the page.
if (location.origin !== 'https://canvas.uw.edu') throw 'LOGIN_EXPIRED:' + location.origin;
if (!window.COURSE || !window.FILE_ID) throw 'USAGE: set window.COURSE and window.FILE_ID with --pre';
const meta = await (await fetch(`/api/v1/courses/${window.COURSE}/files/${window.FILE_ID}`)).json();
if (!meta.url) throw 'FILE_ERROR: ' + JSON.stringify(meta).slice(0, 200);
const b = new Uint8Array(await (await fetch(meta.url)).arrayBuffer());
let s = '';
for (let i = 0; i < b.length; i += 8192) s += String.fromCharCode(...b.subarray(i, i + 8192));
({file_id: window.FILE_ID, name: meta.display_name, size: meta.size, updated_at: meta.updated_at, b64: btoa(s)})
