'use client'
import { useCallback, useEffect, useRef, useState } from 'react'
import { supabase, supabaseReady } from '../../lib/supabase'
import s from './dashboard.module.css'

const API = (process.env.NEXT_PUBLIC_API_BASE || '').replace(/\/$/, '')

const SUGGESTIONS = [
  'Άλλαξε το τηλέφωνο σε 210 1234567',
  'Κάνε το πιο μοντέρνο και σκούρο',
  'Πρόσθεσε υπηρεσία «Δωρεάν εκτίμηση»',
  'Γράψε πιο ζεστά την ιστορία μας',
]

export default function Dashboard() {
  const [session, setSession] = useState(undefined)   // undefined = φορτώνει
  const [clients, setClients] = useState(null)
  const [clientId, setClientId] = useState(null)
  const [account, setAccount] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const [ver, setVer] = useState(0)
  const [err, setErr] = useState('')
  const [email, setEmail] = useState('')
  const [sent, setSent] = useState(false)
  const [googleOn, setGoogleOn] = useState(false)
  const chatEnd = useRef(null)

  // Δείξε το κουμπί Google μόνο αν ο provider είναι όντως ενεργός στο Supabase,
  // αλλιώς ο πελάτης θα έπαιρνε σφάλμα «provider is not enabled».
  useEffect(() => {
    const url = process.env.NEXT_PUBLIC_SUPABASE_URL
    const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
    if (!url || !key) return
    fetch(`${url.replace(/\/$/, '')}/auth/v1/settings`, { headers: { apikey: key } })
      .then((r) => r.json())
      .then((d) => setGoogleOn(Boolean(d?.external?.google)))
      .catch(() => {})
  }, [])

  // --- auth ---
  useEffect(() => {
    if (!supabaseReady) { setSession(null); return }
    supabase.auth.getSession().then(({ data }) => setSession(data.session ?? null))
    const { data: sub } = supabase.auth.onAuthStateChange((_e, sess) => setSession(sess ?? null))
    return () => sub.subscription.unsubscribe()
  }, [])

  const authFetch = useCallback(async (path, opts = {}) => {
    const token = session?.access_token
    const res = await fetch(API + path, {
      ...opts,
      headers: { ...(opts.headers || {}), 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    })
    if (!res.ok) throw new Error((await res.text()).slice(0, 200) || `HTTP ${res.status}`)
    return res.json()
  }, [session])

  // --- φόρτωσε τα sites του χρήστη ---
  useEffect(() => {
    if (!session) return
    authFetch('/clients/lookup')
      .then((d) => {
        setClients(d.clients || [])
        const fromUrl = new URLSearchParams(window.location.search).get('client')
        const pick = (d.clients || []).find((c) => c.id === fromUrl) || (d.clients || [])[0]
        if (pick) setClientId(pick.id)
      })
      .catch((e) => setErr('Δεν μπόρεσα να φορτώσω τα site σου. ' + e.message))
  }, [session, authFetch])

  useEffect(() => {
    if (!clientId) return
    authFetch(`/clients/${clientId}/account`).then(setAccount).catch(() => {})
    setMessages([{ role: 'bot', text: 'Γεια σου! Πες μου τι θέλεις να αλλάξω στο site σου — με απλά λόγια.' }])
  }, [clientId, authFetch])

  useEffect(() => { chatEnd.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  async function send(text) {
    const msg = (text ?? input).trim()
    if (!msg || busy) return
    setInput(''); setErr('')
    setMessages((m) => [...m, { role: 'me', text: msg }])
    setBusy(true)
    try {
      const d = await authFetch(`/clients/${clientId}/chat-edit`, {
        method: 'POST', body: JSON.stringify({ message: msg }),
      })
      setMessages((m) => [...m, { role: 'bot', text: d.reply, changed: d.changed }])
      if (d.changed?.length) setVer(Date.now())   // ανανέωσε το preview
    } catch (e) {
      setMessages((m) => [...m, { role: 'bot', text: 'Ουπς, κάτι πήγε στραβά. Δοκίμασε ξανά.' }])
    }
    setBusy(false)
  }

  async function openBilling() {
    try {
      const d = await authFetch(`/clients/${clientId}/billing-portal`, { method: 'POST' })
      window.location.href = d.url
    } catch (e) {
      setErr('Η διαχείριση συνδρομής δεν είναι διαθέσιμη ακόμα.')
    }
  }

  async function signInGoogle() {
    setErr('')
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: { redirectTo: `${window.location.origin}/dashboard` },
    })
    if (error) setErr('Η σύνδεση με Google δεν είναι διαθέσιμη αυτή τη στιγμή — '
                      + 'χρησιμοποίησε το email σου παρακάτω.')
  }

  async function signInEmail(e) {
    e.preventDefault()
    if (!email.trim()) return
    const { error } = await supabase.auth.signInWithOtp({
      email: email.trim(),
      options: { emailRedirectTo: `${window.location.origin}/dashboard` },
    })
    if (error) setErr('Δεν στάλθηκε το email: ' + error.message)
    else setSent(true)
  }

  // ---------- render ----------
  if (session === undefined) {
    return <div className={s.center}><span className={s.spin} />Φορτώνει…</div>
  }

  if (!supabaseReady) {
    return <div className={s.center}>Η σύνδεση δεν έχει ρυθμιστεί ακόμα. Γράψε μας στο hello@getvitrina.gr</div>
  }

  if (!session) {
    return (
      <div className={s.center}>
        <div className={s.loginCard}>
          <h1>Το site σου</h1>
          <p>Συνδέσου για να δεις και να αλλάξεις το site σου.</p>
          {googleOn && (
            <>
              <button className={s.google} onClick={signInGoogle}>
                <span className={s.gIcon}>G</span> Συνέχεια με Google
              </button>
              <div className={s.or}><span>ή</span></div>
            </>
          )}
          {sent ? (
            <p className={s.ok}>✓ Σου στείλαμε σύνδεσμο στο <strong>{email}</strong>. Άνοιξέ τον από το κινητό σου.</p>
          ) : (
            <form onSubmit={signInEmail} className={s.emailForm}>
              <input type="email" required placeholder="το email σου" value={email}
                onChange={(e) => setEmail(e.target.value)} />
              <button type="submit">Στείλε μου σύνδεσμο</button>
            </form>
          )}
          {err && <p className={s.err}>{err}</p>}
        </div>
      </div>
    )
  }

  if (clients && clients.length === 0) {
    return (
      <div className={s.center}>
        <div className={s.loginCard}>
          <h1>Δεν βρήκα site</h1>
          <p>Το email <strong>{session.user.email}</strong> δεν έχει site ακόμα.</p>
          <a className={s.google} href="https://getvitrina.gr/connect.html">Φτιάξε το site μου →</a>
          <button className={s.linkBtn} onClick={() => supabase.auth.signOut()}>Αποσύνδεση</button>
        </div>
      </div>
    )
  }

  return (
    <div className={s.page}>
      <header className={s.top}>
        <span className={s.brand}>Vitrina</span>
        {clients?.length > 1 && (
          <select className={s.picker} value={clientId || ''} onChange={(e) => setClientId(e.target.value)}>
            {clients.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        )}
        <div className={s.topRight}>
          {account?.domain?.domain && (
            <a className={s.live} href={`https://${account.domain.domain}`} target="_blank" rel="noreferrer">
              Δες το ζωντανά ↗
            </a>
          )}
          <button className={s.linkBtn} onClick={openBilling}>Συνδρομή</button>
          <button className={s.linkBtn} onClick={() => supabase.auth.signOut()}>Έξοδος</button>
        </div>
      </header>

      <div className={s.split}>
        <section className={s.chat}>
          <div className={s.msgs}>
            {messages.map((m, i) => (
              <div key={i} className={m.role === 'me' ? s.me : s.bot}>
                <p>{m.text}</p>
                {m.changed?.length > 0 && (
                  <span className={s.tag}>✓ ενημερώθηκε: {m.changed.join(', ')}</span>
                )}
              </div>
            ))}
            {busy && <div className={s.bot}><p className={s.typing}><i /><i /><i /></p></div>}
            <div ref={chatEnd} />
          </div>

          {messages.length <= 1 && (
            <div className={s.chips}>
              {SUGGESTIONS.map((t) => (
                <button key={t} onClick={() => send(t)} className={s.chip}>{t}</button>
              ))}
            </div>
          )}

          <form className={s.composer} onSubmit={(e) => { e.preventDefault(); send() }}>
            <input value={input} onChange={(e) => setInput(e.target.value)} disabled={busy}
              placeholder="Πες μου τι να αλλάξω…" />
            <button type="submit" disabled={busy || !input.trim()}>➤</button>
          </form>
          {err && <p className={s.err}>{err}</p>}
        </section>

        <section className={s.preview}>
          <div className={s.bar}>
            <span className={s.dot} /><span className={s.dot} /><span className={s.dot} />
            <span className={s.url}>{account?.domain?.domain || 'η προεπισκόπησή σου'}</span>
          </div>
          {clientId && (
            <iframe key={ver} src={`/site/${clientId}${ver ? `?v=${ver}` : ''}`} title="Το site σου" />
          )}
        </section>
      </div>
    </div>
  )
}
