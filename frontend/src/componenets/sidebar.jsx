import { useEffect, useState } from "react";
import {getAvailableDocuments, downloadDocument} from "../api"
import './sidebar.css'

const quickQuestions = [
    'How does leave approval work?',
    'What is our work from home policy?',
    'How are policy exceptions handled?'
]



const roleGroups = [
    {key : 'employee', label : "Employee"},
    {key : 'manager', label : "Manager"},
    {key : 'hr', label : "HR"},
]

const roleLabels = {
  employee: "Employee",
  manager: "Manager",
  hr_admin: "HR Admin",
}

const visibleGroups = {
  employee: ["employee"],
  manager: ["employee", "manager"],
  hr_admin: ["employee", "manager", "hr"],
}

export default function Sidebar({user, onQuickQuestion, onLogout}){

    const [documents, setDocuments] = useState([])
    const [expanded, setExpanded] = useState(['employee'])
    const [loadingDocs, setLoadingDocs] = useState(true)
    const [docError, setDocError]  = useState("")
    const [downloadingId, setDownloadingId] = useState(null)


    const userRole = user?.role 
    const allowedGroups = visibleGroups[userRole] || []


    useEffect(()=>{
        let cancelled = false

        async function loadDocuments(){
            const token = sessionStorage.getItem("access_token")

            try{
                const data = await getAvailableDocuments(token)
                if (!cancelled){
                    setDocuments(data)
                    setDocError("")
                }
               
            }
            catch(error){
                if(!cancelled){
                    setDocError(error.message)
                }
            }finally{
                if(!cancelled){
                    setLoadingDocs(false)
                }
            }
        }

        loadDocuments()

        return ()=>{
            cancelled = true
        }
    }, [])


    function toggleGroup(group){
        setExpanded(previous => 
            previous.includes(group)?
            previous.filter(item=> item!=group):
            [...previous, group]
        )
    }

    async function handleDownload(document){
        const token = sessionStorage.getItem('access_token')

        setDownloadingId(document.id)
        setDocError('')

        try{
            await downloadDocument(
                token,
                document.id,
                document.filename
            )
        }
        catch(error){
            setDocError(error.message)
        }finally{
            setDownloadingId(null)
        }


    }

    return(
        <aside className="app-sidebar">
            <div className="sidebar-brand">
                {/* <div className="sidebar-logo">✳</div> */}

                <div>
                <h2>Ask Safe</h2>
                <p>Ask Questions, Safely</p>
                </div>
            </div>

            <div className="sidebar-scroll">
                <section className="sidebar-section">
                <h3>QUICK QUESTIONS</h3>

                <div className="quick-question-list">
                    {quickQuestions.map(question => (
                    <button
                        className="quick-question"
                        key={question}
                        onClick={() => onQuickQuestion(question)}
                        title={question}
                    >
                        <span className="quick-question-icon">↗</span>
                        <span>{question}</span>
                    </button>
                    ))}
                </div>
                </section>

                <section className="sidebar-section documents-section">
                <h3>AVAILABLE DOCUMENTS</h3>

                {loadingDocs && (
                    <p className="sidebar-muted">Loading documents...</p>
                )}

                {!loadingDocs && !docError && documents.length === 0 && (
                    <p className="sidebar-muted">
                    No accessible documents yet.
                    </p>
                )}

                

                {!loadingDocs && roleGroups
                .filter(group=> allowedGroups.includes(group.key))
                .map(group => {
                    const groupDocuments = documents.filter(
                    document =>
                        document.access_level === group.key &&
                        document.status === "ready"
                    )


                    const isExpanded = expanded.includes(group.key)

                    return (
                    <div className="document-group" key={group.key}>
                        <button
                        className="document-group-heading"
                        onClick={() => toggleGroup(group.key)}
                        aria-expanded={isExpanded}
                        >
                        <span className="group-chevron">
                            {isExpanded ? "⌄" : ">"}
                        </span>

                        <span>{group.label}</span>

                        <span className="document-count">
                            {groupDocuments.length}
                        </span>
                        </button>

                        {isExpanded && (
                        <div className="document-list">
                            {groupDocuments.length === 0 ? (
                            <p className="sidebar-muted empty-group">
                                No documents
                            </p>
                            ) : (
                            groupDocuments.map(document => (
                                <button
                                key={document.id}
                                className="document-item"
                                onClick={() => handleDownload(document)}
                                disabled={downloadingId === document.id}
                                title={`Download ${document.filename}`}
                                >
                                <span className="document-icon">PDF</span>

                                <span className="document-name">
                                    {document.filename}
                                </span>

                                <span className="download-icon">
                                    {downloadingId === document.id
                                    ? "…"
                                    : "↓"}
                                </span>
                                </button>
                            ))
                            )}
                        </div>
                        )}
                    </div>
                    )
                })}

                {docError && (
                    <p className="sidebar-error">{docError}</p>
                )}
                </section>
            </div>

            <div className="sidebar-footer">
                <div className="sidebar-user">
                    <div className="user-avatar">
                        {(user?.email?.[0] || "U").toUpperCase()}
                    </div>

                    <div className="user-details">
                        <p className="user-email" title={user?.email}>
                        {user?.email || "Signed in"}
                        </p>

                        <p className="user-role">
                        {roleLabels[userRole] || userRole || "User"}
                        </p>
                    </div>

                    <button
                        className="logout-button"
                        onClick={onLogout}
                        title="Log out"
                        aria-label="Log out"
                    >
                        ↗
                    </button>
                    </div>

                    
            </div>

        </aside>
    )

}