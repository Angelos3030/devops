// Brand slot: uploaded logo if present, otherwise the wordmark (business name)
// styled by the template's own class. On dark themes pass `dark` so a dark logo
// stays visible inside a soft light chip. We adapt placement/contrast only —
// never redraw the client's logo.
export default function Brand({ data: d, className, dark = false, prefix = null, suffix = null }) {
  // prefix/suffix (μονόγραμμα, διακοσμητική τελεία) εμφανίζονται μόνο στο wordmark mode
  if (!d.LOGO) return <span className={className}>{prefix}{d.NAME}{suffix}</span>
  return (
    <span className={className} style={{ display: 'inline-flex', alignItems: 'center', lineHeight: 0 }}>
      <img
        src={d.LOGO}
        alt={d.NAME}
        style={{
          height: '2.1em', width: 'auto', maxWidth: '170px', objectFit: 'contain', display: 'block',
          ...(dark ? { background: 'rgba(255,255,255,.92)', borderRadius: '6px', padding: '3px 9px' } : {}),
        }}
      />
    </span>
  )
}
