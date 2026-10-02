// @vitest-environment jsdom
// End-to-end UI flow against the real FastAPI demo backend (start it on 127.0.0.1:8000).
import { afterEach, beforeAll, expect, test } from 'vitest'
import { cleanup, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from './App.jsx'

beforeAll(() => {
  const real = globalThis.fetch
  const backend = process.env.CODEPROOF_TEST_URL || 'http://127.0.0.1:8000'
  globalThis.fetch = (u, o) => real(String(u).startsWith('/') ? `${backend}${u}` : u, o)
})
afterEach(cleanup)

test('full challenge flow matches the screenshots', async () => {
  const user = userEvent.setup()
  await fetch('/demo/reset', { method: 'POST' })
  render(<App />)
  expect(await screen.findByText(/Prove you can fix it/)).toBeTruthy()
  await user.click(await screen.findByRole('button', { name: 'Open Project' }))
  expect(await screen.findByText('Analysis complete')).toBeTruthy()
  expect(screen.getByRole('button', { name: /Investigation/ }).disabled).toBe(true)
  expect(screen.getByRole('button', { name: /Patch Review/ }).disabled).toBe(true)

  await user.click(screen.getByRole('button', { name: 'Break My App' }))
  await user.click(await screen.findByRole('button', { name: 'Start Challenge' }))
  expect(await screen.findByText('Challenge Copy: TEMPORARY')).toBeTruthy()
  expect(await screen.findByText('Hint 0 of 4')).toBeTruthy()

  await user.click(screen.getByRole('button', { name: 'Get Hint' }))
  expect(await screen.findByText(/Level 1 — Direction/)).toBeTruthy()

  const box = screen.getByPlaceholderText('Your explanation')
  await user.type(box, 'The database connection is slow and times out')
  await user.click(screen.getByRole('button', { name: 'Evaluate Explanation' }))
  expect(await screen.findByText(/INCORRECT/)).toBeTruthy()
  expect(screen.queryByRole('button', { name: 'Open Patch Review' })).toBeNull()

  await user.clear(box)
  await user.type(box, 'The frontend sends email instead of username so the handler returns 422 missing credentials')
  await user.click(screen.getByRole('button', { name: 'Evaluate Explanation' }))
  await user.click(await screen.findByRole('button', { name: 'Open Patch Review' }))
  expect(await screen.findByText(/Align the login request/)).toBeTruthy()
  expect(screen.getByText('PATCH UNLOCKED')).toBeTruthy()
  expect(screen.getByRole('button', { name: 'Start Mock Validation' }).disabled).toBe(true)

  await user.click(screen.getByRole('button', { name: 'Apply to Challenge Copy' }))
  expect(await screen.findByText('Challenge Copy: TEMPORARILY MODIFIED')).toBeTruthy()
  await user.click(screen.getByRole('button', { name: 'Start Mock Validation' }))
  expect(await screen.findByText('Starting sandbox ...', { exact: false })).toBeTruthy()
  await waitFor(() => expect(screen.getByText(/Authentication test/)).toBeTruthy(), { timeout: 5000 })
  expect(screen.getByText('READY FOR REVIEW')).toBeTruthy()
  await user.click(screen.getByRole('button', { name: 'View Release Readiness' }))
  expect(await screen.findByText(/Patch Tested in Temporary Copy/)).toBeTruthy()
}, 20000)
