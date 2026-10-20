// Canvas wiki page -> text (e.g. GPU 'weekly-reading-sets' for textbook chapters). On https://canvas.uw.edu/courses/<COURSE>:
//   python scripts/pw_run.py scripts/browser/canvas_page.js state/_page.tmp --pre "window.COURSE=1917398; window.PAGE='weekly-reading-sets'" --url https://canvas.uw.edu/courses/1917398
if (location.origin !== 'https://canvas.uw.edu') throw 'LOGIN_EXPIRED:' + location.origin;
if (!window.COURSE || !window.PAGE) throw 'USAGE: set window.COURSE and window.PAGE with --pre';
const pg = await (await fetch(`/api/v1/courses/${window.COURSE}/pages/${window.PAGE}`, {headers: {Accept: 'application/json'}})).json();
if (!pg.body) throw 'PAGE_ERROR: ' + JSON.stringify(pg).slice(0, 200);
const d = document.createElement('div'); d.innerHTML = pg.body;
({title: pg.title, updated_at: pg.updated_at, text: d.innerText.replace(/\n{3,}/g, '\n\n').trim()})
