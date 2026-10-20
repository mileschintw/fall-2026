// 1) On https://piazza.com/class/muomkq9jzdj104 : list feed (compare with state/piazza_seen.json)
// Logged out, Piazza redirects to the home page (https://piazza.com/) with a login modal.
if (location.origin !== 'https://piazza.com' || !location.pathname.startsWith('/class/')) throw 'LOGIN_EXPIRED:' + location.href;
for(let i=0;i<20 && !document.querySelector('li[data-id="post_group_item"]');i++) await new Promise(r=>setTimeout(r,500));
if (!document.querySelector('li[data-id="post_group_item"]')) throw 'EMPTY_FEED: feed did not render; not saving an empty list';
[...document.querySelectorAll('li[data-id="post_group_item"]')].map(e=>({cid:e.id.replace('_item',''),unread:e.className.includes('unread'),
  label:(e.querySelector('[role=link]')||e).getAttribute('aria-label')}))
// 2) For one post: scripts/browser/piazza_post.js with --url .../post/<cid>
