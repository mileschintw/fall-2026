// On https://piazza.com/class/muomkq9jzdj104/post/<cid> (pw_run.py --url): returns the post's text.
// NOTE: opening a post marks it read on Piazza. Never post/reply.
if (location.origin !== 'https://piazza.com' || !location.pathname.startsWith('/class/')) throw 'LOGIN_EXPIRED:' + location.href;
for(let i=0;i<20 && (!document.querySelector('main') || document.querySelector('main').innerText.includes('Rendering markdown'));i++) await new Promise(r=>setTimeout(r,500));
({cid: location.pathname.split('/').pop(), text: document.querySelector('main').innerText})
