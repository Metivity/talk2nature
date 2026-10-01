export function contributionDraft({kind, title, url, depth, reason}) {
  if (!['Source suggestion','Correction','Research question','Help with a task'].includes(kind)) throw Error('Choose a contribution type.');
  for (const [label, value, max] of [['title',title,100],['source link',url,350],['review depth',depth,80],['question',reason,600]]) {
    if (typeof value !== 'string' || !value.trim() || value.length > max) throw Error(`Add a ${label} within the stated length limit.`);
  }
  let source;
  try { source=new URL(url.trim()); } catch { throw Error('Use a complete public HTTPS source link.'); }
  if (source.protocol !== 'https:' || source.username || source.password) throw Error('Use a public HTTPS link without credentials.');
  const body = `Contribution: ${kind}\n\nSource / relevant page: ${source.href}\n\nWhat I reviewed: ${depth.trim()}\n\nWhy it matters / my question:\n${reason.trim()}\n\nSuggested for discussion; not independently validated by Talk2Nature.`;
  const link = new URL('https://github.com/Metivity/talk2nature/issues/new');
  link.searchParams.set('title',`[${kind}] ${title.trim()}`); link.searchParams.set('body',body);
  if (link.href.length > 7500) throw Error('Shorten the draft before opening it on GitHub.');
  return {body,url:link.href};
}

export function youtubeEmbed(id) {
  if (!/^[a-zA-Z0-9_-]{11}$/.test(id)) throw Error('Invalid video identity.');
  return `https://www.youtube-nocookie.com/embed/${id}?autoplay=0&rel=0`;
}
