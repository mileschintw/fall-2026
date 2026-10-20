// GPU Teams General channel: python scripts/pw_run.py scripts/browser/teams_general.js state/_teams.tmp --url https://teams.cloud.microsoft/
// (Not teams.microsoft.com/v2/: it redirects again after load and kills the evaluation.)
// Returns {channel, now, threads:[{id, created, author, subject, body, replies:[{id, at, author, body}]}]}.
// Every message id is its creation epoch ms (`message-body-<ms>`), so times never depend on the UI language
// (Teams switches between English and 中文) or on relative labels like "昨天". Times are Pacific "YYYY-MM-DD HH:MM".
// Only loaded threads are returned (Teams virtual-scrolls; recently active threads load first) and each thread
// shows only its last few replies. Never post or reply.
if (!/teams\.(cloud\.)?microsoft(\.com)?$/.test(location.hostname)) throw 'LOGIN_EXPIRED:' + location.href;
const GENERAL = 'channel-list-item-text-19:oUPz16fUrA61KIpX_G-ZACdmP8c5jnz0ZTq_ZSVaed41@thread.tacv2';
const sleep = ms => new Promise(r => setTimeout(r, ms));
for (let i = 0; i < 60 && !document.querySelector(`[data-tid="${GENERAL}"]`); i++) await sleep(500);
const ch = document.querySelector(`[data-tid="${GENERAL}"]`);
if (!ch) throw 'NOT_LOADED: GPU General channel not in the team list (Teams did not load, or login expired)';
ch.click();
for (let i = 0; i < 60 && !(document.title.includes('GPU Computing') && document.querySelector('[data-tid="channel-pane-message"]')); i++) await sleep(500);
await sleep(2000);
const posts = [...document.querySelectorAll('[data-tid="channel-pane-message"]')];
if (!posts.length) throw 'EMPTY_FEED: no posts rendered; not saving an empty list';

const pad = n => String(n).padStart(2, '0');
const at = ms => { const d = new Date(+ms); return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`; };
const text = (root, sel) => ((root.querySelector(sel) || {}).innerText || '').trim();
const msg = (root, id) => ({id, at: at(id), author: text(root, `#author-${id}`), body: text(root, `#content-${id}`) || text(root, `#message-body-${id}`)});
({
  channel: document.title,
  now: at(Date.now()),
  threads: posts.map(p => {
    const id = p.id.replace('reply-chain-summary-', '');
    const ids = [...new Set([...p.querySelectorAll('[id^="message-body-"]')].map(e => e.id.slice(13)))];
    const head = msg(p, id);
    return {id, created: head.at, author: head.author, subject: text(p, `#subject-line-${id}`), body: head.body,
            replies: ids.filter(x => x !== id).sort().map(x => msg(p, x))};
  }),
})
