import { useState } from 'react'
import { login, signup, getMe, askQuestion } from './api'
import './App.css'

export default function App() {
  const [mode, setMode] = useState('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState('employee')
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [loading, setLoading] = useState(false)
  const [user, setUser] = useState(null)
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState([])
  const [queryLoading, setQueryLoading] = useState(false)
  const [queryError, setQueryError] = useState('')

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setNotice('')
    setLoading(true)

    try {
      if (mode === 'signup') {
        const result = await signup(email, password, role)
        setNotice(result.message || `Account created. Status: ${result.account_status}`)
        setMode('login')
        setPassword('')
      } else {
        const result = await login(email, password)
        sessionStorage.setItem('access_token', result.access_token)

        const currentUser = await getMe(result.access_token)
        setUser(currentUser)
      }
    } catch (err) {
      setError(err.message || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  function logout() {
    sessionStorage.removeItem('access_token')
    setUser(null)
    setEmail('')
    setPassword('')
    setMode('login')
  }


async function handleAsk(event) {
  event.preventDefault()

  const text = question.trim()
  if (!text || queryLoading) return

  setQueryError('')
  setQueryLoading(true)

  try {
    const token = sessionStorage.getItem('access_token')
    const result = await askQuestion(token, text)

    setMessages(previous => [
      ...previous,
      {
        question: result.question,
        answer: result.answer,
        sources: result.sources || [],
      },
    ])

    setQuestion('')
  } catch (err) {
    setQueryError(err.message || 'Something went wrong')
  } finally {
    setQueryLoading(false)
  }
}


  
if (user) {
  return (
    <main className="screen">
      <section className="window workspace-window">
        <div className="titlebar">
          <div className="traffic-lights"><i /><i /><i /></div>
          <span>Ask Safe · Workspace</span>
          <button className="titlebar-logout" onClick={logout}>
            Log out
          </button>
        </div>

        <div className="workspace">
          <header className="chat-header">
            <div className="logo">S</div>
            <p className="overline">ENTERPRISE POLICY ASSISTANT</p>
            <h1>What do you need to know?</h1>
            <p className="subtitle">
              Ask a question about your organization's policies.
            </p>
          </header>

          <div className="chat-messages">
            {messages.length === 0 && (
              <p className="empty-state">
                Your answers will appear here, with their supporting sources.
              </p>
            )}

            {messages.map((message, index) => (
              <article className="message" key={index}>
                <div className="question-bubble">
                  {message.question}
                </div>

                <div className="answer">
                  <p className="answer-label">ANSWER</p>
                  <p className="answer-text">{message.answer}</p>

                  {message.sources.length > 0 && (
                    <details className="sources">
                      <summary>
                        Sources ({message.sources.length})
                      </summary>

                      <div className="source-list">
                        {message.sources.map((source, sourceIndex) => (
                          <div
                            className="source-item"
                            key={`${source.document_id}-${source.chunk_index}-${sourceIndex}`}
                          >
                            <strong>{source.filename}</strong>
                            <span>
                              Page {source.page_number}
                              {' · '}
                              Relevance: {
                                typeof source.similarity === 'number'
                                  ? `${(source.similarity * 100).toFixed(1)}%`
                                  : 'N/A'
                              }
                            </span>
                          </div>
                        ))}
                      </div>
                    </details>
                  )}
                </div>
              </article>
            ))}

            {queryLoading && (
              <p className="loading-answer">Looking through your policies…</p>
            )}
          </div>

          {queryError && (
            <p className="feedback error">{queryError}</p>
          )}

          <form className="chat-form" onSubmit={handleAsk}>
            <textarea
              placeholder="Ask about leave, benefits, workplace policies…"
              value={question}
              onChange={event => setQuestion(event.target.value)}
              rows={2}
              required
            />

            <button
              className="primary-button"
              type="submit"
              disabled={queryLoading || !question.trim()}
            >
              {queryLoading ? 'Thinking…' : 'Ask'}
            </button>
          </form>

          <p className="chat-footnote">
            Signed in as {user.email} · {user.role}
          </p>
        </div>
      </section>
    </main>
  )
}


  return (
    <main className="screen">
      <section className="window auth-window">
        <div className="titlebar">
          {/* <div className="traffic-lights"><i /><i /><i /></div> */}
          <span>Ask Safe</span>
        </div>

        <div className="auth-content">
          {/* <div className="logo">S</div> */}
          {/* <p className="overline">ENTERPRISE POLICY ASSISTANT</p> */}
          <h1>{mode === 'login' ? 'Welcome back.' : 'Create your account.'}</h1>
          <p></p>
          {/* <p className="subtitle">
            {mode === 'login'
              ? 'Sign in to find clear answers in your company policies.'
              : 'Create an account to access your policy workspace.'}
          </p> */}

          <div className="mode-switch">
            <button
              className={mode === 'login' ? 'selected' : ''}
              onClick={() => { setMode('login'); setError(''); setNotice('') }}
            >
              Sign in
            </button>
            <button
              className={mode === 'signup' ? 'selected' : ''}
              onClick={() => { setMode('signup'); setError(''); setNotice('') }}
            >
              Sign up
            </button>
          </div>

          <form onSubmit={handleSubmit}>
            <label htmlFor="email">Email address</label>
            <input
              id="email"
              type="email"
              autoComplete="email"
              placeholder="Enter your email"
              value={email}
              onChange={event => setEmail(event.target.value)}
              required
            />

            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
              placeholder="Enter your password"
              value={password}
              onChange={event => setPassword(event.target.value)}
              minLength={8}
              required
            />

            {mode === 'signup' && (
              <>
                <label htmlFor="role">Requested role</label>
                <select id="role" value={role} onChange={event => setRole(event.target.value)}>
                  <option value="employee">Employee</option>
                  <option value="manager">Manager</option>
                  <option value="hr_admin">HR administrator</option>
                </select>
                <p className="hint">
                  Employee accounts activate immediately. Manager and HR accounts need approval.
                </p>
              </>
            )}

            {error && <p className="feedback error">{error}</p>}
            {notice && <p className="feedback success">{notice}</p>}

            <button className="primary-button" type="submit" disabled={loading}>
              {loading ? 'Please wait…' : mode === 'login' ? 'Sign in' : 'Create account'}
              {/* {!loading && <span>↗</span>} */}
            </button>
          </form>

          {/* <p className="privacy-note">
            Your access is governed by your account permissions.
          </p> */}
        </div>
      </section>
    </main>
  )
}