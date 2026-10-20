// Canvas file PDF -> text. On https://canvas.uw.edu/courses/<COURSE>:
//   python scripts/pw_run.py scripts/browser/pdf_text.js state/_slides.tmp --pre "window.COURSE=1917398; window.FILE_ID=154353784" --url https://canvas.uw.edu/courses/1917398
// Returns {file_id, name, pages, text} (pages separated by "\n\n=== p<N> ===\n"). DSA: get FILE_ID from module items (/files is 403).
if (location.origin !== 'https://canvas.uw.edu') throw 'LOGIN_EXPIRED:' + location.origin;
if (!window.COURSE || !window.FILE_ID) throw 'USAGE: set window.COURSE and window.FILE_ID with --pre';
const pdfjs = await import('https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.0.379/pdf.min.mjs');
pdfjs.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.0.379/pdf.worker.min.mjs';
const meta = await (await fetch(`/api/v1/courses/${window.COURSE}/files/${window.FILE_ID}`)).json();
if (!meta.url) throw 'FILE_ERROR: ' + JSON.stringify(meta).slice(0, 200);
const doc = await pdfjs.getDocument({data: await (await fetch(meta.url)).arrayBuffer()}).promise;
const out = [];
for (let i = 1; i <= doc.numPages; i++) {
  const c = await (await doc.getPage(i)).getTextContent();
  out.push(`=== p${i} ===\n` + c.items.map(t => t.str + (t.hasEOL ? '\n' : ' ')).join('').trim());
}
({file_id: window.FILE_ID, name: meta.display_name, pages: doc.numPages, text: out.join('\n\n')})
