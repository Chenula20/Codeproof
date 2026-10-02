import { useState } from 'react'

const dotCls = (n) => (n.endsWith('.js') ? 'js' : n.endsWith('.md') ? 'md' : '')

export function Explorer({ nodes, selected, onSelect }) {
  const files = nodes.filter((n) => n.kind === 'file')
  const top = (p) => (p.includes('/') ? p.split('/')[0] : null)
  const groups = ['src', 'tests'].filter((d) => nodes.some((n) => n.path === d))
  return (
    <div className="col explorer"><h4>Project Explorer</h4>
      {files.filter((f) => !top(f.path)).map((f) => <Item key={f.path} f={f} selected={selected} onSelect={onSelect} />)}
      {groups.map((d) => (<div key={d}><div className="row dir">▭ {d}</div>
        {files.filter((f) => top(f.path) === d).map((f) => <Item key={f.path} f={f} selected={selected} onSelect={onSelect} indent />)}</div>))}
    </div>)
}
const Item = ({ f, selected, onSelect, indent }) => (
  <button className={`row${indent ? ' in' : ''}${selected === f.path ? ' sel' : ''}`} onClick={() => onSelect(f.path)}>
    <span className={`dot ${dotCls(f.name)}`} />{f.name}</button>)

export function Coach({ s, ov, actions }) {
  const [text, setText] = useState('')
  const c = s.challenge
  if (!c) return (
    <div className="col coach"><h5 style={{ display: 'flex', justifyContent: 'space-between' }}><b style={{ color: 'var(--text)', fontWeight: 500 }}>💡 AI Coach</b><span className="tag purple">MOCK</span></h5>
      <h3>Project Analysis</h3><p className="dim">{ov?.description}</p><p className="dim" style={{ marginTop: 14 }}>Build understanding through evidence. Start a controlled challenge when you are ready.</p>
      <button className="btn wide" style={{ margin: '18px 0' }} onClick={actions.showSkills}>View Engineering Skill Map</button>
      <p className="dim" style={{ fontSize: 13.5 }}>All coaching and assessments in this demo are deterministic fixtures, not AI results.</p></div>)
  const status = s.readiness?.status === 'READY_FOR_REVIEW' ? 'READY FOR REVIEW' : s.unlocked ? 'PATCH UNLOCKED' : 'INVESTIGATING'
  return (
    <div className="col coach"><h5 style={{ display: 'flex', justifyContent: 'space-between' }}><b style={{ color: 'var(--text)', fontWeight: 500 }}>💡 AI Coach</b><span className="tag purple">MOCK</span></h5>
      <h3>{c.title}</h3><span className={`tag ${status === 'INVESTIGATING' ? 'cyan' : 'green'}`}>{status}</span><hr />
      <h3>Progressive Hints</h3><p className="dim">Hint {s.hints.length} of 4</p>
      <button className="btn wide" style={{ marginTop: 10 }} disabled={s.hints.length >= 4} onClick={actions.hint}>Get Hint</button>
      {s.hints.map((h) => <div className="hint" key={h.level}><small>Level {h.level} — {h.title}</small>{h.hint}</div>)}<hr />
      <h3>Explain Before You Fix</h3>
      {s.unlocked ? (<>{s.verdict && <div className="verdict">{s.verdict.feedback}</div>}
        <button className="btn go wide" onClick={actions.reviewPatch}>Open Patch Review</button></>) : (<>
        <p className="dim">Explain what you think caused the problem.</p>
        <textarea placeholder="Your explanation" value={text} onChange={(e) => setText(e.target.value)} />
        {s.verdict && <div className="verdict bad"><b>{s.verdict.classification.replace('_', ' ')}.</b> {s.verdict.feedback}</div>}
        <button className="btn go wide" disabled={text.trim().length < 10 || s.busy} onClick={() => actions.explain(text)}>Evaluate Explanation</button></>)}
    </div>)
}

export function Bottom({ s, ov, tab, setTab, actions }) {
  const T = [['problems', 'Problems'], ['tests', 'Tests'], ['sandbox', 'Sandbox'], ['readiness', 'Release Readiness']]
  const v = s.validation, r = s.readiness
  return (
    <div className="bottom"><div className="btabs">{T.map(([k, l]) => <button key={k} className={`btab${tab === k ? ' on' : ''}`} onClick={() => setTab(k)}>{l}</button>)}
      <span className="pill dark">SIMULATED RESULTS</span></div>
      <div className="bbody">
        {tab === 'problems' && (s.challenge ? (<><h6>Challenge error log</h6><div className="box">{s.challenge.error_output.split('\n').slice(0, 3).join('\n')}</div></>)
          : (<><h6>Project review notes · demo</h6><p style={{ fontSize: 16 }}>Demo review focus: {ov?.review_focus?.toLowerCase()}</p></>))}
        {tab === 'tests' && (v ? (<>{v.tests.map((t) => <div className="trow" key={t.name}><span className="ok">✓</span><span className="t"><span className="ok">{t.name}</span> — {t.detail}</span><span className="dim">{t.duration_ms} ms</span></div>)}
          <button className="btn" style={{ marginTop: 14 }} onClick={() => setTab('readiness')}>View Release Readiness</button></>) : <p className="dim">No tests run yet. Apply the patch, then start mock validation.</p>)}
        {tab === 'sandbox' && (s.validating ? <div className="box">Starting sandbox ...{'\n'}Running tests ...</div> : v ? <div className="box">{v.output}</div> : <p className="dim" style={{ fontSize: 16 }}>Sandbox idle.</p>)}
        {tab === 'readiness' && (r ? (<><div className="big">{r.status.replaceAll('_', ' ')}</div><p className="dim">Release Readiness · simulated evidence only</p>
          <div style={{ display: 'flex', gap: 28, flexWrap: 'wrap', margin: '14px 0' }}>{r.checks.map((c) => <span key={c.key} className={c.passed ? 'ok' : ''} style={{ color: c.passed ? undefined : 'var(--red)' }}>{c.passed ? '✓' : '✗'} {c.label}</span>)}</div>
          <p className="dim" style={{ fontSize: 13.5 }}>{r.note}</p></>) : <p className="dim">Run validation to compute release readiness.</p>)}
      </div></div>)
}

export function Modal({ onCancel, onStart, busy }) {
  return (<div className="veil" onClick={onCancel}><div className="modal" onClick={(e) => e.stopPropagation()}>
    <h2>Start a challenge?</h2><p className="dim" style={{ fontSize: 17 }}>CodeProof creates a temporary challenge copy and introduces a controlled failure. Your original project stays protected.</p>
    <div className="acts"><button className="btn" onClick={onCancel}>Cancel</button><button className="btn go" onClick={onStart} disabled={busy}>Start Challenge</button></div></div></div>)
}
