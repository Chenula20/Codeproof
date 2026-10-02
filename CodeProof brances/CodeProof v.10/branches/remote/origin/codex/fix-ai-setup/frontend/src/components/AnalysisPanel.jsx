export default function AnalysisPanel({ overview }) {
  if (!overview) return null
  return (
    <div className="content-panel">
      <h2 style={{ marginBottom: 14 }}>Project Analysis</h2>
      <div className="card" style={{ maxWidth: 620 }}>
        <h2>{overview.name}</h2>
        <p className="focus">{overview.description}</p>
        <div className="tech-row">
          {overview.technologies.map((t) => <span key={t} className="chip">{t}</span>)}
        </div>
        <p className="focus">Review focus: <b>{overview.review_focus}</b></p>
      </div>
      <p className="note">Analysis is part of the deterministic demo dataset — no AI calls were made.</p>
    </div>
  )
}
