const BASE = '/demo'

async function request(path, options = {}) {
  const response = await fetch(BASE + path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!response.ok) {
    let detail = `Request failed (${response.status})`
    try {
      const body = await response.json()
      if (body.detail) detail = body.detail
    } catch {
      // keep the generic detail
    }
    throw new Error(detail)
  }
  return response.json()
}

export const api = {
  overview: () => request('/overview'),
  skillMap: () => request('/skill-map'),
  files: (source) => request(`/files?source=${source}`),
  file: (path, source) => request(`/file?path=${encodeURIComponent(path)}&source=${source}`),
  startChallenge: () => request('/challenge/start', { method: 'POST' }),
  hint: (level) => request('/hint', { method: 'POST', body: JSON.stringify({ level }) }),
  explanation: (text) => request('/explanation', { method: 'POST', body: JSON.stringify({ explanation: text }) }),
  patch: () => request('/patch'),
  applyPatch: () => request('/patch/apply', { method: 'POST' }),
  validate: () => request('/validation', { method: 'POST' }),
  readiness: () => request('/release-readiness'),
  state: () => request('/state'),
  reset: () => request('/reset', { method: 'POST' }),
}
