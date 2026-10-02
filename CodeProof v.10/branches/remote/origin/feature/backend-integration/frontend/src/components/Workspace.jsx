import { useCallback, useEffect, useState } from 'react'
import { api } from '../api.js'
import FileTree from './FileTree.jsx'
import CodeView from './CodeView.jsx'
import AnalysisPanel from './AnalysisPanel.jsx'
import SkillMapPanel from './SkillMapPanel.jsx'
import BreakModal from './BreakModal.jsx'
import Investigation from './Investigation.jsx'
import PatchReview from './PatchReview.jsx'
import BottomPanel from './BottomPanel.jsx'

const VIEWS = [
  { key: 'analysis', label: 'Analysis' },
  { key: 'skills', label: 'Skill Map' },
  { key: 'code', label: 'Code' },
]

export default function Workspace({ overview, skills }) {
  const [view, setView] = useState('analysis')
  const [source, setSource] = useState('original')
  const [tree, setTree] = useState([])
  const [selectedFile, setSelectedFile] = useState(null)
  const [fileContent, setFileContent] = useState(null)
  const [showBreak, setShowBreak] = useState(false)
  const [breakInfo, setBreakInfo] = useState(null)
  const [challenge, setChallenge] = useState(null)
  const [hints, setHints] = useState([])
  const [verdict, setVerdict] = useState(null)
  const [patchUnlocked, setPatchUnlocked] = useState(false)
  const [proposal, setProposal] = useState(null)
  const [applied, setApplied] = useState(false)
  const [applyMessage, setApplyMessage] = useState(null)
  const [validation, setValidation] = useState(null)
  const [readiness, setReadiness] = useState(null)
  const [bottomTab, setBottomTab] = useState('problems')
  const [running, setRunning] = useState(false)
  const [error, setError] = useState(null)
  const [filesVersion, setFilesVersion] = useState(0)
  const [investigationFiles, setInvestigationFiles] = useState({})

  const fail = (err) => setError(err.message)

  useEffect(() => {
    api.files(source).then((t) => setTree(t.nodes)).catch(fail)
  }, [source, filesVersion])

  useEffect(() => {
    if (view !== 'code' || !selectedFile) { setFileContent(null); return }
    api.file(selectedFile, source).then(setFileContent).catch(fail)
  }, [view, selectedFile, source, filesVersion])

  useEffect(() => {
    if (view !== 'investigation' || !challenge) return
    Promise.all(
      challenge.investigation_files.map((p) => api.file(p, 'challenge')),
    ).then((contents) => {
      setInvestigationFiles(Object.fromEntries(contents.map((c) => [c.path, c])))
    }).catch(fail)
  }, [view, challenge, filesVersion])

  const openBreak = useCallback(async () => {
    try {
      const info = await api.startChallenge()
      setBreakInfo(info)
      setShowBreak(true)
    } catch (err) { fail(err) }
  }, [])

  const beginInvestigation = useCallback(() => {
    const info = breakInfo
    setShowBreak(false)
    setChallenge(info)
    setSource('challenge')
    setView('investigation')
    setBottomTab('problems')
  }, [breakInfo])

  const revealHint = useCallback(async (level) => {
    try {
      const hint = await api.hint(level)
      setHints((prev) => (prev.some((h) => h.level === hint.level) ? prev : [...prev, hint]))
    } catch (err) { fail(err) }
  }, [])

  const submitExplanation = useCallback(async (text) => {
    try {
      const result = await api.explanation(text)
      setVerdict(result)
      setPatchUnlocked(result.patch_unlocked)
    } catch (err) { fail(err) }
  }, [])

  const reviewPatch = useCallback(async () => {
    try {
      setProposal(await api.patch())
      setView('patch')
    } catch (err) { fail(err) }
  }, [])

  const applyPatch = useCallback(async () => {
    try {
      const result = await api.applyPatch()
      setApplied(true)
      setApplyMessage(result.message)
      setFilesVersion((v) => v + 1)
    } catch (err) { fail(err) }
  }, [])

  const runTests = useCallback(async () => {
    setRunning(true)
    setBottomTab('tests')
    try {
      const v = await api.validate()
      setValidation(v)
      setReadiness(await api.readiness())
    } catch (err) { fail(err) } finally { setRunning(false) }
  }, [])

  return (
    <div className="workspace">
      <div className="sidebar">
        <h3>Workspace</h3>
        <div className="source-toggle">
          <button
            className={`btn sm${source === 'original' ? ' active' : ''}`}
            onClick={() => { setSource('original'); setView('code') }}
          >
            Original
          </button>
          <button
            className={`btn sm${source === 'challenge' ? ' active' : ''}`}
            disabled={!challenge}
            title={challenge ? 'Disposable challenge copy' : 'Start a challenge first'}
            onClick={() => { setSource('challenge'); setView('code') }}
          >
            Challenge
          </button>
        </div>
        {VIEWS.map((v) => (
          <div
            key={v.key}
            className={`tree-row${view === v.key ? ' selected' : ''}`}
            onClick={() => setView(v.key)}
          >
            <span className="icon">{v.key === 'analysis' ? '📊' : v.key === 'skills' ? '🧭' : '📁'}</span>
            {v.label}
          </div>
        ))}
        <div className="tree-row" onClick={openBreak} style={{ color: 'var(--red)' }}>
          <span className="icon">💥</span>
          Break My App
        </div>
        {challenge && (
          <div className="tree-row" onClick={() => setView('investigation')}>
            <span className="icon">🔍</span>
            Investigation
          </div>
        )}
        {proposal && (
          <div className="tree-row" onClick={() => setView('patch')}>
            <span className="icon">🩹</span>
            Patch Review
          </div>
        )}
        <h3>Files — {source} copy</h3>
        <FileTree
          nodes={tree}
          selected={selectedFile}
          onSelect={(path) => { setSelectedFile(path); setView('code') }}
        />
      </div>

      <div className="main">
        {error && <div className="error-banner" onClick={() => setError(null)}>{error} (click to dismiss)</div>}
        {view === 'analysis' && <AnalysisPanel overview={overview} />}
        {view === 'skills' && <SkillMapPanel skills={skills} />}
        {view === 'code' && (
          fileContent ? (
            <CodeView content={fileContent.content} highlights={fileContent.highlights} />
          ) : (
            <div className="empty-state">
              <span>{tree.length === 0 ? 'Loading files…' : 'Select a file from the explorer.'}</span>
            </div>
          )
        )}
        {view === 'investigation' && challenge && (
          <Investigation
            challenge={challenge}
            files={investigationFiles}
            hints={hints}
            verdict={verdict}
            patchUnlocked={patchUnlocked}
            onHint={revealHint}
            onExplain={submitExplanation}
            onReviewPatch={reviewPatch}
          />
        )}
        {view === 'patch' && proposal && (
          <PatchReview
            proposal={proposal}
            applied={applied}
            applyMessage={applyMessage}
            hasValidation={!!validation}
            onApply={applyPatch}
            onRunTests={runTests}
          />
        )}
        <BottomPanel
          tab={bottomTab}
          setTab={setBottomTab}
          challenge={challenge}
          validation={validation}
          readiness={readiness}
          onRunTests={runTests}
          running={running}
        />
      </div>

      {showBreak && breakInfo && (
        <BreakModal challenge={breakInfo} onStart={beginInvestigation} onClose={() => setShowBreak(false)} />
      )}
    </div>
  )
}
