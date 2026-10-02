function ProblemsTab({ challenge }) {
  if (!challenge) return <div className="empty-state">No active challenge. Use “Break My App” to start one.</div>
  return (
    <div>
      <div className="test-row" style={{ borderBottom: 'none' }}>
        <span className="status failed">ERROR</span>
        <span className="detail">{challenge.title} — see error output below</span>
      </div>
      <div className="pre-wrap mono" style={{ color: 'var(--red)', marginTop: 8 }}>{challenge.error_output}</div>
    </div>
  )
}

function TestsTab({ validation, onRun, running }) {
  if (!validation) {
    return (
      <div className="empty-state">
        <span>No validation run yet.</span>
        <button className="btn primary" onClick={onRun} disabled={running}>
          {running ? 'Running sandbox…' : 'Run Tests in Sandbox'}
        </button>
      </div>
    )
  }
  return (
    <div>
      {validation.tests.map((t, i) => (
        <div key={i} className="test-row">
          <span className={`status ${t.status}`}>{t.status.toUpperCase()}</span>
          <span style={{ width: 200 }}>{t.name}</span>
          <span className="detail">{t.detail}</span>
          <span className="dur">{t.duration_ms} ms</span>
        </div>
      ))}
      <div className="pre-wrap mono" style={{ color: 'var(--text-faint)', marginTop: 10, fontSize: 11 }}>
        {validation.output}
      </div>
      <div style={{ marginTop: 10, display: 'flex', gap: 10, alignItems: 'center' }}>
        <span className={`status ${validation.status}`} style={{ fontWeight: 700 }}>
          {validation.status.toUpperCase()}
        </span>
        <span style={{ color: 'var(--text-faint)' }}>duration {validation.duration_ms} ms</span>
        <button className="btn sm" onClick={onRun} disabled={running}>
          {running ? 'Running…' : 'Re-run'}
        </button>
      </div>
    </div>
  )
}

function ReadinessTab({ readiness }) {
  if (!readiness) return <div className="empty-state">Run validation to compute release readiness.</div>
  return (
    <div>
      <div className={`readiness-banner ${readiness.status === 'READY_FOR_REVIEW' ? 'ready' : 'progress'}`}>
        {readiness.status === 'READY_FOR_REVIEW' ? '✓ READY FOR REVIEW' : '◌ IN PROGRESS'}
      </div>
      {readiness.checks.map((c) => (
        <div key={c.key} className="check-row">
          <span className={`mark ${c.passed ? 'pass' : 'fail'}`}>{c.passed ? '✓' : '✗'}</span>
          {c.label}
        </div>
      ))}
      <p className="note">{readiness.note}</p>
    </div>
  )
}

export default function BottomPanel({ tab, setTab, challenge, validation, readiness, onRunTests, running }) {
  const tabs = [
    { key: 'problems', label: 'Problems', badge: challenge ? '1' : null, badgeCls: 'red' },
    { key: 'tests', label: 'Tests', badge: validation ? (validation.status === 'passed' ? '✓' : '✗') : null, badgeCls: validation?.status === 'passed' ? 'green' : 'red' },
    { key: 'readiness', label: 'Release Readiness', badge: readiness?.status === 'READY_FOR_REVIEW' ? '✓' : null, badgeCls: 'green' },
  ]
  return (
    <div className="bottom-panel">
      <div className="tabs">
        {tabs.map((t) => (
          <button key={t.key} className={`tab${tab === t.key ? ' active' : ''}`} onClick={() => setTab(t.key)}>
            {t.label}
            {t.badge && <span className={`badge ${t.badgeCls}`}>{t.badge}</span>}
          </button>
        ))}
        <div style={{ flex: 1 }} />
        {tab === 'tests' && (!validation || validation.status !== 'passed') && (
          <button className="btn primary sm" style={{ margin: '5px 10px' }} onClick={onRunTests} disabled={running}>
            {running ? 'Running sandbox…' : 'Run Tests'}
          </button>
        )}
      </div>
      <div className="bottom-body">
        {tab === 'problems' && <ProblemsTab challenge={challenge} />}
        {tab === 'tests' && <TestsTab validation={validation} onRun={onRunTests} running={running} />}
        {tab === 'readiness' && <ReadinessTab readiness={readiness} />}
      </div>
    </div>
  )
}
