// Run on https://uwnetid.sharepoint.com/sites/og_EEP_524_A_B_-_GPU_Computing/Shared%20Documents/Forms/AllItems.aspx
// Returns {date: {sha,len,src,vtt}} for every recording that has a transcript. The result is large:
// the harness saves it to tool-results/*.txt; then run
//   python scripts/save_browser_result.py <that file> state/_gpu.tmp && python scripts/write_transcripts.py state/_gpu.tmp gpu vtt
// Never persist temporaryDownloadUrl (tempauth). Do NOT add ?format= to streamContent (400).
if (location.origin !== 'https://uwnetid.sharepoint.com') throw 'LOGIN_EXPIRED:' + location.origin;
const site='/sites/og_EEP_524_A_B_-_GPU_Computing', H={Accept:'application/json;odata=nometadata'}, J={Accept:'application/json'};
async function h(s){const b=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(s));return [...new Uint8Array(b)].map(x=>x.toString(16).padStart(2,'0')).join('');}
const files=(await fetch(site+"/_api/web/GetListUsingPath(DecodedUrl=@a)/items?@a='"+site+"/Shared Documents'&$select=FileRef,Created,UniqueId&$top=500",{headers:H}).then(r=>r.json())).value;
const drv=(await fetch(site+'/_api/v2.1/drives',{headers:J}).then(r=>r.json())).value[0].id;
const SKIP = window.SKIP_DATES || [];   // e.g. ['2026-10-06'] to skip already-saved lectures
const o={};
for (const f of files.filter(f=>/Recordings\/.*\.mp4$/.test(f.FileRef))){
  const name=f.FileRef.split('/').pop(), m=name.match(/-(\d{4})(\d{2})(\d{2})_/), date=m?`${m[1]}-${m[2]}-${m[3]}`:name;
  if (SKIP.includes(date)) continue;
  const item=await fetch(site+`/_api/v2.1/drives/${drv}/root:/General/Recordings/${encodeURIComponent(name)}`,{headers:J}).then(r=>r.json());
  const tr=await fetch(site+`/_api/v2.1/drives/${drv}/items/${item.id}/media/transcripts`,{headers:J}).then(r=>r.json());
  if(!(tr.value||[]).length){o[date]={missing:true,src:name};continue;}
  const v=await fetch(site+`/_api/v2.1/drives/${drv}/items/${item.id}/media/transcripts/${tr.value[0].id}/streamContent`).then(r=>r.text());
  o[date]={sha:await h(v),len:v.length,src:name,vtt:v};
}
o
