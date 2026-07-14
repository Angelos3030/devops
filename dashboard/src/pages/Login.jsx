import { useState } from 'react'
import { supabase } from '../lib/supabase'

export default function Login() {
  const [err, setErr] = useState('')

  async function signInGoogle() {
    setErr('')
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: { redirectTo: window.location.origin },
    })
    if (error) setErr(error.message)
  }

  return (
    <div className="auth-wrap">
      <div className="auth-card">
        <div className="brand-mark">V</div>
        <h1>Vitrina</h1>
        <p className="muted">Μπες για να δεις και να διαλέξεις το site της επιχείρησής σου.</p>
        <button className="btn-google" onClick={signInGoogle}>
          <svg width="18" height="18" viewBox="0 0 48 48" aria-hidden="true">
            <path fill="#EA4335" d="M24 9.5c3.5 0 6.6 1.2 9 3.6l6.7-6.7C35.6 2.6 30.1 0 24 0 14.6 0 6.4 5.4 2.5 13.2l7.8 6.1C12.2 13.2 17.6 9.5 24 9.5z"/>
            <path fill="#4285F4" d="M46.5 24.5c0-1.6-.1-3.1-.4-4.5H24v9h12.7c-.5 3-2.2 5.5-4.7 7.2l7.3 5.7c4.3-4 6.7-9.9 6.7-17.4z"/>
            <path fill="#FBBC05" d="M10.3 28.3c-.5-1.5-.8-3.1-.8-4.8s.3-3.3.8-4.8l-7.8-6.1C.9 15.9 0 19.8 0 24s.9 8.1 2.5 11.4l7.8-6.1z"/>
            <path fill="#34A853" d="M24 48c6.1 0 11.3-2 15-5.5l-7.3-5.7c-2 1.4-4.7 2.3-7.7 2.3-6.4 0-11.8-3.7-13.7-9l-7.8 6.1C6.4 42.6 14.6 48 24 48z"/>
          </svg>
          Σύνδεση με Google
        </button>
        {err && <p className="err">{err}</p>}
        <p className="fineprint">Με τη σύνδεση αποδέχεσαι τους όρους χρήσης της Vitrina.</p>
      </div>
    </div>
  )
}
