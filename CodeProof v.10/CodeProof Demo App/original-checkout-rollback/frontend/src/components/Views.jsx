export function Analysis({ ov }) {
  if (!ov) return null
  return (<>
    <div className="chips"><span className="tag cyan">Analysis</span></div>
    <h1>{ov.name}</h1><p className="dim">{ov.description}</p>
    <h2>Technologies</h2><div className="chips">{ov.technologies.map((t) => <span className="tag" key={t}>{t}</span>)}</div>
    <h2>Review focus</h2><div className="box" style={{ font: '16px var(--sans)' }}>{ov.review_focus}</div>
  </>)
}

export function SkillMap({ skills }) {
  return (<>
    <h1>Engineering Skill Map</h1><p className="dim">Estimates from project evidence, not measurements of intelligence or ability.</p>
    <div className="cards">{skills.map((s) => (
      <div className="card" key={s.key}><h3>{s.label}</h3>
        {[['Relevance', s.relevance, ''], ['Confidence', s.confidence, 'p']].map(([l, v, c]) => (
          <div className="meter" key={l}>{l}<div className={`bar ${c}`}><i style={{ width: `${v}%` }} /></div><b>{v}%</b></div>))}
        {s.evidence.map((f) => <span className="file" key={f}>{f}</span>)}
      </div>))}</div>
  </>)
}

export function Code({ file, source }) {
  if (!file) return <p className="dim">Select a file from the Project Explorer.</p>
  const hl = new Set(file.highlights || [])
  return (<>
    <div className="chips"><span className="tag">Read-only</span>
      {source === 'challenge' ? <span className="tag purple">Challenge copy</span> : <span className="tag green">Original project</span>}</div>
    <h1 style={{ fontFamily: 'var(--mono)', fontSize: 26 }}>{file.path}</h1>
    <div className="code">{file.content.split('\n').map((t, i) => (
      <div key={i} className={`ln${hl.has(i + 1) ? ' hl' : ''}`}><i>{i + 1}</i><span>{t}</span></div>))}</div>
  </>)
}

export function Investigation({ c, onOpenFile }) {
  return (<>
    <div className="chips"><span className="tag cyan">INVESTIGATING</span><span className="tag">{c.difficulty}</span><span className="tag">{c.skill}</span></div>
    <h1>{c.title}</h1><p className="dim">{c.description}</p>
    <h2>Investigation files</h2>
    {c.investigation_files.map((f) => <button key={f} className="flink" onClick={() => onOpenFile(f)}>{f}<span>→</span></button>)}
    <h2>Error output</h2><div className="box">{c.error_output}</div>
    <p className="dim" style={{ marginTop: 18 }}>Inspect the evidence, reveal hints as needed, then explain your reasoning to unlock a proposed patch.</p>
  </>)
}

export function Patch({ p, applied, applying, onApply, onValidate, validating, validated }) {
  const cls = (l) => (l.startsWith('+++') || l.startsWith('---') || l.startsWith('@@') ? 'meta' : l.startsWith('+') ? 'add' : l.startsWith('-') ? 'del' : '')
  return (<>
    <div className="chips"><span className="tag cyan">PROPOSED PATCH</span><span className="tag green">Risk: {p.risk}</span></div>
    <h1>{p.title}</h1><p className="dim">Affected file: {p.affected_file}</p>
    <ul className="dim" style={{ margin: '10px 0 0 22px' }}>{p.notes.map((n) => <li key={n}>{n}</li>)}</ul>
    <div className="code diff">{p.diff.split('\n').map((l, i) => <div key={i} className={cls(l)}>{l || ' '}</div>)}</div>
    <div style={{ display: 'flex', gap: 14 }}>
      <button className="btn go" onClick={onApply} disabled={applied || applying}>{applied ? 'Applied to challenge copy' : 'Apply to Challenge Copy'}</button>
      <button className="btn" onClick={onValidate} disabled={!applied || validating}>{validating ? 'Running…' : validated ? 'Re-run Mock Validation' : 'Start Mock Validation'}</button>
    </div>
  </>)
}
