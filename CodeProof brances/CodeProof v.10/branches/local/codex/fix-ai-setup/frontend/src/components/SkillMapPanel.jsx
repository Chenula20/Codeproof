export default function SkillMapPanel({ skills }) {
  return (
    <div className="content-panel">
      <h2 style={{ marginBottom: 14 }}>Skill Map</h2>
      <p style={{ color: 'var(--text-dim)', marginBottom: 18, fontSize: 12 }}>
        Estimated from project structure and sources (demo fixtures).
        Bar = relevance, tick = confidence.
      </p>
      {skills.map((s) => (
        <div key={s.key} className="skill-row">
          <div className="label">{s.label}</div>
          <div className="bar-wrap">
            <div className="bar">
              <div className="fill" style={{ width: `${s.relevance}%` }} />
              <div className="confidence" style={{ left: `${s.confidence}%` }} />
            </div>
            <div className="num">{s.relevance}</div>
          </div>
          <div className="evidence">{s.evidence.join(', ')}</div>
        </div>
      ))}
    </div>
  )
}
