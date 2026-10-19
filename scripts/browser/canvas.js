// Run in built-in browser on https://canvas.uw.edu/courses/<id> via javascript_tool.
// Returns slim JSON. ICS URLs are secrets: write to .env only, never to repo/log.
if (location.origin !== 'https://canvas.uw.edu') throw 'LOGIN_EXPIRED:' + location.origin;
async function all(url){let out=[];while(url){const r=await fetch(url,{headers:{Accept:'application/json'}});
  if(!r.ok)return {err:r.status,url};out=out.concat(await r.json());
  const m=(r.headers.get('Link')||'').match(/<([^>]+)>;\s*rel="next"/);url=m?m[1]:null;}return out;}
var strip=h=>{const d=document.createElement('div');d.innerHTML=h||'';return d.innerText.replace(/\n{3,}/g,'\n\n').trim();};
var out={};
for (const id of [1917398,1917417]){
  const b='/api/v1/courses/'+id;
  const asg=await all(b+'/assignments?per_page=100&include[]=submission');
  const ann=await all(`/api/v1/announcements?context_codes[]=course_${id}&start_date=2026-09-01&end_date=2027-01-01&per_page=100`);
  const mods=await all(b+'/modules?include[]=items&per_page=100');
  const quiz=await all(b+'/quizzes?per_page=100');
  // GPU has no Modules; materials live in Files (DSA /files is 403 -> use module items)
  const files=id===1917398?await all(b+'/files?per_page=100&sort=created_at'):[];
  const syl=(await (await fetch(b+'?include[]=syllabus_body')).json()).syllabus_body||'';
  out[id]={
    asg: asg.err?asg:asg.map(a=>({id:a.id,name:a.name,due_at:a.due_at,points:a.points_possible,published:a.published,lock_at:a.lock_at,sub:(a.submission||{}).workflow_state})),
    // BOOTSTRAP §3.1: announcements with posted_at null are stale copies -> drop
    ann: ann.err?ann:ann.filter(a=>a.posted_at).map(a=>({id:a.id,title:a.title,posted_at:a.posted_at,author:(a.author||{}).display_name,text:strip(a.message)})),
    mods: mods.err?mods:mods.map(m=>({name:m.name,items:(m.items||[]).map(i=>({item_id:i.id,type:i.type,title:i.title,id:i.content_id,url:i.external_url}))})),
    files: files.err?files:files.map(f=>({id:f.id,name:f.display_name,created_at:f.created_at,updated_at:f.updated_at})),
    syllabus_len: strip(syl).length,
    quiz: quiz.err?quiz:quiz.map(q=>({id:q.id,title:q.title,due_at:q.due_at,unlock_at:q.unlock_at,lock_at:q.lock_at}))};
}
out
