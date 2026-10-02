export default function CodeView({ content, highlights = [] }) {
  const lines = content.split('\n')
  const mark = new Set(highlights)
  return (
    <div className="code-view">
      {lines.map((text, i) => (
        <div key={i} className={`code-line${mark.has(i + 1) ? ' highlight' : ''}`}>
          <span className="ln">{i + 1}</span>
          <span className="lc">{text || ' '}</span>
        </div>
      ))}
    </div>
  )
}
