import { useState } from "react"
import "./chat.css"
import { askQuestion, askQuestionStream } from "../api"


const test_messages = [{role: "user", text: "hello"}, {role :"assistant", text: 'hi how are you', sources: [{filename: "file1", page_number: "2"}]}]

export default function ChatPage({user}){
    const [loading, setLoading] = useState(false)
    const [messages, setMessages] = useState(test_messages)
    const [question, setQuestion] = useState("")
    const [error, setError] = useState("")
    const[showSources, setShowSources] = useState(false)

    function handleSourcesClick(event){
        setShowSources(prev=>(!prev))
    }

    
    async function handleSubmitStream(event) {
        event.preventDefault()

        const text = question.trim()
        if (!text || loading) return

        const token = sessionStorage.getItem('access_token')

        setMessages(previous => [
            ...previous,
            { role: 'user', text },
            { role: 'assistant', text: '', sources: [] },
        ])

        setQuestion('')
        setLoading(true)
        setError('')

        try {
            await askQuestionStream(token, text, event => {
                if (event.type === 'sources') {
                    setMessages(previous => {
                        const updated = [...previous]
                        const last = updated.length - 1

                        updated[last] = {
                            ...updated[last],
                            sources: event.sources || [],
                        }

                        return updated
                    })
                }

                if (event.type === 'token') {
                    setMessages(previous => {
                        const updated = [...previous]
                        const last = updated.length - 1

                        updated[last] = {
                            ...updated[last],
                            text: updated[last].text + event.text,
                        }

                        return updated
                    })
                }
            })
        } catch (e) {
            setError(e.message)
        } finally {
            setLoading(false)
        }
    }


    async function handleSubmit(event) {
        event.preventDefault()

        const text = question.trim()

        if(!text || loading) return

        const token = sessionStorage.getItem('access_token')

        setMessages(previous => [
            ...previous,
            {role: 'user', text}
        ])

        setQuestion('')
        setLoading(true)
        setError('')

        try{
            const result = await askQuestion(token, text)

            setMessages(prev=>[
                ...prev,
                {
                    role : "assistant",
                    text : result.answer,
                    sources : result.sources? result.sources : []
                }   
            ])

        }
        catch(e){
            setError(e.message)
        } finally {
            setLoading(false)
        }

    }


return (
    <div className="chat-page">
        <header className="chat-header" >
            <div>
                <h2>Ask Safe</h2>
                <p>Ask questions, safely!</p>
            </div>

            <span>{user.email}</span>
            
        </header>

        <main className="chat-messages">
            {
                messages.length == 0 && (
                    <div className="chat-welcome">
                        <h1>How can I help?</h1>
                        <p>Ask me anything about the company policies</p>
                    </div>
                )

                
            }

            {messages.map((message, index)=>(
                <div key={index} className= {`message ${message.role}`}>
                    <div className="message-content">
                        {message.text}

                        {message.text && message.sources?.length>0 && (
                            <div className="message-sources">
                                <strong onClick={handleSourcesClick}>
                                    {showSources?"^" : ">"} Sources
                                </strong>
                                {showSources && message.sources.map((source, i)=>(
                                    <p key= {i}>
                                        {source.filename}
                                        {source.page_number != null && 
                                        ` Page: ${source.page_number}`}
                                    </p>

                                ))}
                            </div>
                        )}
                    </div>
                </div>
            ))}

            {loading && (
                <div className="message-assistant">
                    <div className="message-content typing">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            )}

            {error && <p className="chat-error">{error}</p>}

        </main>

        <form className="chat-input-area"
            onSubmit={handleSubmitStream}>

                <textarea
                    value={question}
                    onChange={(event)=>{setQuestion(event.target.value)}}
                    placeholder="Ask a question"
                    rows={2}
                    disabled= {loading}
                    onKeyDown={(event)=>{
                        if(event.key == 'Enter' &&
                            !event.shiftKey &&
                            !event.nativeEvent.isComposing
                        ){
                            event.preventDefault()
                            event.currentTarget.form.requestSubmit()
                        }
                    }}
                />

                <button type="submit" disabled={loading || !question.trim()}>
                    {loading? 'Thinking...': '^'}
                </button>

            </form>

    </div>
)

}