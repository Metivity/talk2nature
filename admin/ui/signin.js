async function start() {
  const status = document.querySelector('#status');
  try {
    const response = await fetch('/auth/config', {credentials: 'same-origin', cache: 'no-store'});
    if (!response.ok) throw new Error('Sign-In is temporarily unavailable. Please try again.');
    const config = await response.json();
    if (!config.ready) {
      status.textContent = 'Google Sign-In is not connected yet. The workspace stays locked until the Google client is configured.';
      return;
    }
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.onload = () => {
      google.accounts.id.initialize({client_id: config.client_id, nonce: config.nonce, auto_select: false, callback: async ({credential}) => {
        status.textContent = 'Verifying your account…';
        try {
          const result = await fetch('/auth/google', {method:'POST', credentials:'same-origin', headers:{'Content-Type':'application/json'}, body:JSON.stringify({credential})});
          if (!result.ok) throw new Error((await result.json()).detail || 'Sign-In was not completed.');
          location.assign('/admin');
        } catch (error) { status.textContent = error.message; document.querySelector('#retry').hidden = false; }
      }});
      google.accounts.id.renderButton(document.querySelector('#google-button'), {type:'standard', theme:'outline', size:'large', text:'signin_with'});
      status.textContent = 'Use your authorized Google account to continue.';
    };
    script.onerror = () => { status.textContent = 'Google Sign-In could not load. Check your connection and try again.'; document.querySelector('#retry').hidden = false; };
    document.head.append(script);
  } catch (error) { status.textContent = error.message; document.querySelector('#retry').hidden = false; }
}
document.querySelector('#retry').addEventListener('click', () => location.reload());
start();
