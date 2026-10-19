// Lightweight change detector: list every file in the GPU team SharePoint (recordings, .loop channel paragraphs, screenshots).
if (location.origin !== 'https://uwnetid.sharepoint.com') throw 'LOGIN_EXPIRED:' + location.origin;
const site='/sites/og_EEP_524_A_B_-_GPU_Computing';
const r=await fetch(site+"/_api/web/GetListUsingPath(DecodedUrl=@a)/items?@a='"+site+"/Shared Documents'&$select=FileRef,Created,Modified&$top=500",{headers:{Accept:'application/json;odata=nometadata'}}).then(r=>r.json());
r.value.map(f=>[f.FileRef.replace(site+'/Shared Documents/',''),f.Created,f.Modified])
