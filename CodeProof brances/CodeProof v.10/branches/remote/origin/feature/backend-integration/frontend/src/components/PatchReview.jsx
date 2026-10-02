function DiffLine({ line }) {
  let cls = 'diff-line'
  if (line.startsWith('+') && !line.startsWith('+++')) cls += ' add'
  else if (line.startsWith('-') && !line.startsWith('---')) cls += ' del'
  else if (line.startsWith('@@')) cls += ' hunk'
  return <div className={cls}>{line}</div>
}

export default function PatchReview({ proposal, applied, applyMessage, onApply, onRunTests, hasValidation }) {
  return (
    <div className="content-panel" style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div>
        <h2>Patch Review</h2>
        <p style={{ color: 'var(--text-dim)', marginTop: 6 }}>{proposal.title}</p>
        <div className="meta" style={{ display: 'flex', gap: 8, marginTop: 10 }}>
          <span className="chip">{proposal.affected_file}</span>
          <span className="chip" style={{ color: 'var(--green)', borderColor: '#1e4629', background: 'var(--green-dim)' }}>
            Risk: {proposal.risk}
          </span>
        </div>
      </div>
      <ul className="patch-notes">
        {proposal.notes.map((n) => <li key={n}>{n}</li>)}
      </ul>
      <div className="diff-view" style={{ maxHeight: 260, border: '1px solid var(--border)', borderRadius: 8 }}>
        {proposal.diff.split('\n').map((line, i) => <DiffLine key={i} line={line} />)}
      </div>
      {applyMessage && <div className="verdict correct">{applyMessage}</div>}
      <div style={{ display: 'flex', gap: 10 }}>
        <button className="btn primary" disabled={applied} onClick={onApply}>
          {applied ? 'Patch Applied' : 'Apply Patch to Challenge Copy'}
        </button>
        {applied && (
          <button className="btn" onClick={onRunTests}>{hasValidation ? 'Re-run Tests' : 'Run Tests in Sandbox'}</button>
        )}
      </div>
    </div>
  )
}
