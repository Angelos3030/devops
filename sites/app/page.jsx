'use client'
import { useState } from 'react'
import { TEMPLATES, TEMPLATE_KEYS, TEMPLATE_META } from '../lib/templates'
import { demoData } from '../lib/demoData'

export default function DemoPage() {
  const [key, setKey] = useState('editorial')
  const Tpl = TEMPLATES[key]
  return (
    <>
      <div style={bar}>
        <span style={{ fontWeight: 700, letterSpacing: '.02em' }}>Vitrina · React templates (demo)</span>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {TEMPLATE_KEYS.map((k) => (
            <button key={k} onClick={() => setKey(k)} title={TEMPLATE_META[k].desc}
              style={{ ...pill, ...(k === key ? pillActive : {}) }}>
              {TEMPLATE_META[k].label}
            </button>
          ))}
        </div>
      </div>
      <div style={{ paddingTop: 52 }}>
        <Tpl data={demoData} />
      </div>
    </>
  )
}

const bar = { position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100, height: 52,
  display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12,
  padding: '0 16px', background: '#101014', color: '#fff', fontFamily: 'Inter, sans-serif', fontSize: 14 }
const pill = { cursor: 'pointer', border: '1px solid rgba(255,255,255,.25)', background: 'transparent',
  color: '#fff', borderRadius: 999, padding: '6px 14px', fontSize: 13, fontWeight: 600, fontFamily: 'inherit' }
const pillActive = { background: '#ff8a3d', color: '#1a1204', border: '1px solid #ff8a3d' }
