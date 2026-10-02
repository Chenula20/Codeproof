import { useState } from 'react'
import CodeView from './CodeView.jsx'

export default function Investigation({ challenge, files, hints, verdict, onHint, onExplain, onReviewPatch, patchUnlocked }) {
  const [explanation, setExplanation] = useState('')
  const [activeFile, setActiveFile] = useState(challenge.investigation_files[0])
  const file = files[activeFile]
  const nextLevel = hints.length + 1

  return (
    <div className="investigation">
      <div className="code-pane">
        <div className="panel-header">
          <span className="title">Investigation</span>
          {challenge.investigation_files.map((f) => (
            <button
              key={f}
              className={`btn sm${activeFile === f ? ' primary' : ' ghost'}`}
              onClick={() => setActiveFile(f)}
            >
              {f}
            </button>
          ))}
          <div className="spacer" />
          {patchUnlocked && <button className="btn primary sm" onClick={onReviewPatch}>Review Patch →</button>}
        </div>
        {file ? <CodeView content={file.content} highlights={file.highlights} /> : <div className="loading">Loading…</div>}
      </div>
      <div className="coach">
        <h3>AI Coach — explain before fix</h3>
        <div className="coach-body">
          {hints.map((h) => (
            <div key={h.level} className="hint-card">
              <div className="hint-title">Hint {h.level}/{h.total} — {h.title}</div>
              <div className="hint-text">{h.hint}</div>
            </div>
          ))}
          {hints.length === 0 && (
            <p style={{ color: 'var(--text-faint)', fontSize: 12 }}>
              Reveal progressive hints if you get stuck, then explain the root cause in your own words.
              A correct explanation unlocks the patch proposal.
            </p>
          )}
          {verdict && (
            <div className={`verdict ${verdict.classification === 'CORRECT' ? 'correct' : verdict.classification === 'PARTIALLY_CORRECT' ? 'partial' : 'incorrect'}`}>
              <b>{verdict.classification.replaceAll('_', ' ')}</b> — {verdict.feedback}
            </div>
          )}
          <textarea
            placeholder="Explain the root cause: what is sent, what is read, and why does it fail?"
            value={explanation}
            onChange={(e) => setExplanation(e.target.value)}
          />
        </div>
        <div className="coach-actions">
          <button className="btn" disabled={nextLevel > 4} onClick={() => onHint(nextLevel)}>
            {nextLevel > 4 ? 'All hints revealed' : `Reveal Hint ${nextLevel}`}
          </button>
          <button
            className="btn primary"
            disabled={!explanation.trim()}
            onClick={() => onExplain(explanation.trim())}
          >
            Evaluate Explanation
          </button>
        </div>
      </div>
    </div>
  )
}
