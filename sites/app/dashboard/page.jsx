'use client'
import { useCallback, useEffect, useRef, useState } from 'react'
import { supabase, supabaseReady } from '../../lib/supabase'
import s from './dashboard.module.css'

const API = (process.env.NEXT_PUBLIC_API_BASE || '').replace(/\/$/, '')

const SUGGESTIONS = [
  'Η διεύθυνσή μου είναι Λ. Μαραθώνος 12',
  'Άλλαξε το τηλέφωνο σε 210 1234567',
  'Κάνε το πιο μοντέρνο και σκούρο',
  'Πρόσθεσε υπηρεσία «Δωρεάν εκτίμηση»',
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
  const [tab, setTab] = useState('chat')
  const [form, setForm] = useState(null)      // τα πεδία του site, για χειροκίνητη αλλαγή
  const [saving, setSaving] = useState(false)
  const [posts, setPosts] = useState(null)
  const [copied, setCopied] = useState(-1)
  const [saved, setSaved] = useState(false)
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

  // Χειροκίνητη επεξεργασία — δουλεύει και χωρίς τον βοηθό AI.
  async function openEdit() {
    setTab('edit'); setErr('')
    if (form) return
    try {
      const d = await authFetch(`/clients/${clientId}/content`)
      setForm(d.content)
    } catch (e) {
      setErr('Δεν φόρτωσαν τα στοιχεία σου. ' + e.message)
    }
  }

  async function saveForm(e) {
    e.preventDefault()
    setSaving(true); setErr(''); setSaved(false)
    try {
      await authFetch(`/clients/${clientId}/content`, {
        method: 'PUT', body: JSON.stringify({ content: form }),
      })
      setSaved(true)
      setVer(Date.now())                    // ανανέωσε το preview
      setTimeout(() => setSaved(false), 2500)
    } catch (e) {
      setErr('Δεν αποθηκεύτηκε. ' + e.message)
    }
    setSaving(false)
  }

  const setField = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))

  // Έτοιμα posts για την εβδομάδα — ο πελάτης τα αντιγράφει και τα δημοσιεύει.
  async function openPosts() {
    setTab('posts'); setErr('')
    if (posts) return
    try {
      const d = await authFetch(`/clients/${clientId}/posts`)
      setPosts(d.posts || [])
    } catch (e) {
      setErr('Δεν φόρτωσαν τα posts. ' + e.message)
    }
  }

  function copyPost(i, text) {
    navigator.clipboard?.writeText(text)
    setCopied(i); setTimeout(() => setCopied(-1), 2000)
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
          <a className={s.linkBtn} href="/odigos/google" target="_blank" rel="noreferrer">Οδηγός Google</a>
          <button className={s.linkBtn} onClick={openBilling}>Συνδρομή</button>
          <button className={s.linkBtn} onClick={() => supabase.auth.signOut()}>Έξοδος</button>
        </div>
      </header>

      <div className={s.split}>
        <section className={s.chat}>
          <div className={s.tabs}>
            <button className={tab === 'chat' ? s.tabOn : s.tab} onClick={() => setTab('chat')}>💬 Πες μου τι θες</button>
            <button className={tab === 'edit' ? s.tabOn : s.tab} onClick={openEdit}>✏️ Στοιχεία</button>
            <button className={tab === 'posts' ? s.tabOn : s.tab} onClick={openPosts}>📅 Posts</button>
          </div>

          {tab === 'posts' ? (
            !posts ? (
              <div className={s.formWrap}><p className={s.hint}>Φορτώνει…</p></div>
            ) : (
              <div className={s.formWrap}>
                <p className={s.hint}>Η εβδομάδα σου. Αντίγραψε, βγάλε τη φωτογραφία, δημοσίευσε.</p>
                {posts.map((p, i) => (
                  <div key={i} className={s.post}>
                    <div className={s.postTop}>
                      <strong>{p.day}</strong><span>{p.angle}</span>
                    </div>
                    <p className={s.postIdea}>💡 {p.idea}</p>
                    <p className={s.postHint}>📷 {p.photo_hint}</p>
                    <p className={s.postCaption}>{p.caption}</p>
                    <div className={s.postBar}>
                      <span className={s.tags}>{p.hashtags?.join(' ')}</span>
                      <button onClick={() => copyPost(i, `${p.caption}

${(p.hashtags || []).join(' ')}`)}>
                        {copied === i ? '✓ Αντιγράφηκε' : 'Αντιγραφή'}
                      </button>
                    </div>
                  </div>
                ))}
                {err && <p className={s.err}>{err}</p>}
              </div>
            )
          ) : tab === 'edit' ? (
            !form ? (
              <div className={s.formWrap}><p className={s.hint}>Φορτώνει…</p></div>
            ) : (
              <form className={s.formWrap} onSubmit={saveForm}>
                <label>Όνομα<input value={form.name || ''} onChange={setField('name')} /></label>
                <label>Τι κάνεις<input value={form.trade || ''} onChange={setField('trade')} /></label>
                <label>Τηλέφωνο<input value={form.phone || ''} onChange={setField('phone')} /></label>
                <label>Πόλη<input value={form.city || ''} onChange={setField('city')} /></label>
                <label>Διεύθυνση <span className={s.hint}>(για τον χάρτη)</span>
                  <input value={form.address || ''} onChange={setField('address')} placeholder="π.χ. Λ. Μαραθώνος 12" /></label>
                <label>Ωράριο<input value={form.hours || ''} onChange={setField('hours')} placeholder="Δευτ.–Σάβ. 09:00–19:00" /></label>
                <label>Μία φράση για σένα
                  <textarea rows={2} value={form.tagline || ''} onChange={setField('tagline')} /></label>
                <label>Το προφίλ σου στο Google <span className={s.hint}>(προαιρετικό)</span>
                  <input value={form.gbp_url || ''} onChange={setField('gbp_url')} placeholder="https://maps.app.goo.gl/..." /></label>

                <div className={s.formBar}>
                  <button type="submit" disabled={saving}>{saving ? 'Αποθηκεύω…' : 'Αποθήκευση'}</button>
                  {saved && <span className={s.okTag}>✓ Αποθηκεύτηκε</span>}
                </div>
                {err && <p className={s.err}>{err}</p>}
              </form>
            )
          ) : (
          <>
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
          </>
          )}
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
