// Canvas calendar ICS URLs for .env (they are secrets: never print them or save them in the repo). On https://canvas.uw.edu:
//   python scripts/pw_run.py scripts/browser/ics_urls.js state/_ics_urls.tmp --url https://canvas.uw.edu/
// then write .env with the python one-liner in BOOTSTRAP §9 and delete the .tmp. Returns {CANVAS_ICS_GPU, CANVAS_ICS_DSA}.
if (location.origin !== 'https://canvas.uw.edu') throw 'LOGIN_EXPIRED:' + location.origin;
const cs = await (await fetch('/api/v1/courses?enrollment_state=active&per_page=100', {headers: {Accept: 'application/json'}})).json();
const ics = id => ((cs.find(c => c.id === id) || {}).calendar || {}).ics;
const out = {CANVAS_ICS_GPU: ics(1917398), CANVAS_ICS_DSA: ics(1917417)};
if (!out.CANVAS_ICS_GPU || !out.CANVAS_ICS_DSA) throw 'NOT_FOUND: course missing from active enrollments';
out
