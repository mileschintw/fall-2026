// Assignment specs for both courses (descriptions + the Canvas files they link). Run via scripts/assignment_specs.py:
//   python scripts/pw_run.py scripts/browser/canvas_specs.js state/_specs.tmp --url https://canvas.uw.edu/courses/1917398
// Returns {<course id>: [{id, name, due_at, published, html_url, text, links, files:[{id, name, size, updated_at, content_type}]}]}.
// File download URLs carry a verifier token: only file ids and metadata leave this snippet, `verifier` params are
// stripped from links, and scripts/assignment_specs.py scrubs the text again before writing.
if (location.origin !== 'https://canvas.uw.edu') throw 'LOGIN_EXPIRED:' + location.origin;
async function all(url){let out=[];while(url){const r=await fetch(url,{headers:{Accept:'application/json'}});
  if(!r.ok)throw 'HTTP '+r.status+' '+url;out=out.concat(await r.json());
  const m=(r.headers.get('Link')||'').match(/<([^>]+)>;\s*rel="next"/);url=m?m[1]:null;}return out;}
const noVerifier=h=>h.replace(/([?&])verifier=[^&#]*&?/,'$1').replace(/[?&]$/,'');
var out={};
for (const cid of [1917398,1917417]){
  const asg=await all(`/api/v1/courses/${cid}/assignments?per_page=100`);
  out[cid]=[];
  for (const a of asg){
    // attached off-screen so innerText keeps list/table/paragraph line breaks (a detached node falls back to textContent)
    const d=document.createElement('div');d.style.cssText='position:absolute;left:-99999px;width:800px';
    d.innerHTML=a.description||'';document.body.append(d);
    const links=[], fids=new Set();
    for (const x of d.querySelectorAll('a[href]')){
      const h=noVerifier(x.getAttribute('href')), m=h.match(/\/courses\/\d+\/files\/(\d+)/);
      if (m) fids.add(m[1]); else links.push({text:x.innerText.trim(),href:h});
    }
    const text=d.innerText.replace(/\n{3,}/g,'\n\n').trim();
    d.remove();
    const files=[];
    for (const f of fids){
      const r=await fetch(`/api/v1/courses/${cid}/files/${f}`,{headers:{Accept:'application/json'}});
      const j=r.ok?await r.json():{};
      files.push(r.ok?{id:j.id,name:j.display_name,size:j.size,updated_at:j.updated_at,content_type:j['content-type']}:{id:+f,error:r.status});
    }
    out[cid].push({id:a.id,name:a.name,due_at:a.due_at,published:a.published,html_url:a.html_url,text,links,files});
  }
}
out
