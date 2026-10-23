const API_BASE_URL = 'http://127.0.0.1:8000'

export async function login(email, password) {
  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })

  const data = await response.json()

  if (!response.ok) {
    throw new Error(data.detail || 'Login failed')
  }

  return data
}

export async function signup(email, password, role) {
  const response = await fetch(`${API_BASE_URL}/api/auth/signup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, role }),
  })

  const data = await response.json()

  if (!response.ok) {
    throw new Error(data.detail || 'Signup failed')
  }

  return data
}

export async function getMe(token) {
  const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  })

  const data = await response.json()

  if (!response.ok) {
    throw new Error(data.detail || 'Could not load user')
  }

  return data
}


export async function askQuestion(token, question) {

  const response = await fetch(`${API_BASE_URL}/api/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      question,
      limit: 5,
    }),
  })

  const data = await response.json()

  if (!response.ok) {
    throw new Error(
      typeof data.detail === 'string'
        ? data.detail
        : 'Could not get an answer'
    )
  }
  console.log(data)
  return data
}



export async function askQuestionStream(token, question, onEvent) {
    const response = await fetch(
        `${API_BASE_URL}/api/query/stream`,
        {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify({
                question,
                limit: 5,
            }),
        }
    )

    if (!response.ok) {
        const data = await response.json().catch(() => ({}))
        throw new Error(
            data.detail || 'Could not start answer generation'
        )
    }

    if (!response.body) {
        throw new Error('Streaming is not supported by this response')
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    function processLine(line) {
        if (!line.trim()) return

        const event = JSON.parse(line)
        if (event.type === 'error') {
            throw new Error(event.message)
        }
        console.log(event)
        onEvent(event)
    }

    try {
        while (true) {
            const { value, done } = await reader.read()

            if (done) break

            buffer += decoder.decode(value, { stream: true })

            const lines = buffer.split('\n')
            buffer = lines.pop() || ''

            for (const line of lines) {
                processLine(line)
            }
        }

        buffer += decoder.decode()

        if (buffer.trim()) {
            processLine(buffer)
        }
    } finally {
        reader.releaseLock()
    }
}
