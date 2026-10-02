const STEPS = [['Understand', 'Analysis and skill map from your project'], ['Investigate', 'Break My App creates a controlled failure'],
  ['Explain', 'Say what caused it before you see a fix'], ['Fix', 'Review the proposed patch and its risk'], ['Validate', 'Sandbox tests and release readiness']]

export default function Welcome({ name, onOpen, loading }) {
  return (
    <div className="welcome" style={{ gridRow: '2 / 5' }}>
      <div>
        <h1>Build with AI.<br />Understand the code.<br />Prove you can fix it.</h1>
        <p className="dim" style={{ fontSize: 19, maxWidth: 640 }}>Explore a project, investigate a controlled failure, explain the cause, and review a proposed fix.</p>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginTop: 28 }}>
          <button className="btn go" style={{ fontSize: 18, padding: '16px 34px', borderRadius: 999 }} onClick={onOpen} disabled={loading}>Open Project</button>
          <span className="dim">Loads {name || 'Student Event Management System'}</span>
        </div>
        <div className="guard"><b>⛨ Workspace Guardian · Original Project: PROTECTED</b>
          <p className="dim" style={{ marginTop: 6 }}>CodeProof works on a temporary copy. Your original files are never modified.</p></div>
      </div>
      <ol className="steps">{STEPS.map(([t, d], i) => <li key={t}><i>{i + 1}</i><div><b>{t}</b><span>{d}</span></div></li>)}</ol>
    </div>
  )
}
