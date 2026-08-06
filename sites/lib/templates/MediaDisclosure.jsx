export default function MediaDisclosure({ data }) {
  if (!data?.MEDIA_NOTICE || data.MEDIA_MODE === 'real') return null
  return (
    <aside aria-label="Πληροφορία εικόνων" style={{
      padding: '10px 20px 78px', textAlign: 'center', background: '#f6f4ef',
      color: '#5f5b52', font: '12px/1.5 Inter, system-ui, sans-serif',
    }}>
      {data.MEDIA_NOTICE}
    </aside>
  )
}
