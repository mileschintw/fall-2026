// Run on any https://uw.hosted.panopto.com page (e.g. /Panopto/Pages/Home.aspx).
// If redirected to canvas.uw.edu/login/oauth2/confirm -> STOP, user must authorize.
// Returns {date: {sha,len,src,srt}}:
//   python scripts/pw_run.py scripts/browser/panopto.js state/_dsa.tmp --url <Home.aspx> && python scripts/write_transcripts.py state/_dsa.tmp dsa srt
// NOTE: Panopto StartTime for Class 1 is the upload time (10/02); real date 09/30. Check dates before writing.
if (location.origin !== 'https://uw.hosted.panopto.com') throw 'LOGIN_EXPIRED:' + location.origin;
const FOLDER='9b12e253-ce65-412c-837a-b4d500342d54';
async function h(s){const b=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(s));return [...new Uint8Array(b)].map(x=>x.toString(16).padStart(2,'0')).join('');}
const q={queryParameters:{query:null,sortColumn:1,sortAscending:true,maxResults:100,page:0,startDate:null,endDate:null,folderID:FOLDER,bookmarked:false,getFolderData:true,isSharedWithMe:false,isSubscriptionsPage:false,includeArchived:true,includeArchivedStateCount:true,sessionListOnlyArchived:false,includePlaylists:true}};
const res=(await fetch('/Panopto/Services/Data.svc/GetSessions',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(q)}).then(r=>r.json())).d.Results;
const SKIP = window.SKIP_IDS || [];
if (window.LIST_ONLY) res.map(x=>[x.DeliveryID,x.SessionName,x.StartTime,x.Duration]); else {
const o={};
for (const x of res.filter(x=>x.Duration>60 && !SKIP.includes(x.DeliveryID))){
  const ms=+x.StartTime.match(/\d+/)[0], date=new Date(ms).toLocaleDateString('en-CA',{timeZone:'America/Los_Angeles'});
  const t=await (await fetch('/Panopto/Pages/Transcription/GenerateSRT.ashx?id='+x.DeliveryID+'&language=0')).text();
  o[date]={sha:await h(t),len:t.length,src:x.SessionName+' '+x.DeliveryID,srt:t};
}
o }
