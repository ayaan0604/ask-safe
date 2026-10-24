
import { useCallback, useEffect, useState } from "react";
import {
  getAdminDocuments,
  getPendingUsers,
  approveUser,
  rejectUser,
  deleteAdminDocument,
  uploadAdminDocument,
} from "../api";
import "./admin.css";

const token = () => sessionStorage.getItem("access_token");

export default function AdminPage({ user, onBackToChat, onLogout }) {
  const [tab, setTab] = useState("documents");
  const [documents, setDocuments] = useState([]);
  const [pendingUsers, setPendingUsers] = useState([]);
  const [file, setFile] = useState(null);
  const [accessLevel, setAccessLevel] = useState("employee");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const [docs, users] = await Promise.all([
        getAdminDocuments(token()),
        getPendingUsers(token()),
      ]);

      setDocuments(docs);
      setPendingUsers(users);
    } catch (err) {
      setError(err.message || "Could not load admin data.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  async function handleUpload(event) {
    event.preventDefault();

    const form = event.currentTarget;

    if (!file) {
      setError("Choose a PDF file first.");
      return;
    }

    setBusy(true);
    setError("");
    setNotice("");

    try {
      const result = await uploadAdminDocument(
        token(),
        file,
        accessLevel
      );

      setNotice(
        `Uploaded ${result.filename} successfully (${result.chunk_count} chunks).`
      );
      setFile(null);
      form.reset();
      await loadData();
    } catch (err) {
      setError(err.message || "Upload failed.");
    } finally {
      setBusy(false);
    }
  }

  async function handleDelete(document) {
    const confirmed = window.confirm(
      `Delete "${document.filename}"? This also removes its indexed chunks.`
    );

    if (!confirmed) return;

    setBusy(true);
    setError("");
    setNotice("");

    try {
      await deleteAdminDocument(token(), document.id);
      setNotice(`${document.filename} deleted.`);
      await loadData();
    } catch (err) {
      setError(err.message || "Could not delete document.");
    } finally {
      setBusy(false);
    }
  }

  async function handleUserDecision(userId, action) {
    const person = pendingUsers.find(item => item.id === userId);
    if (!person) return;

    const label = action === "approve" ? "approve" : "reject";
    if (!window.confirm(`${label[0].toUpperCase() + label.slice(1)} ${person.email}?`)) {
      return;
    }

    setBusy(true);
    setError("");
    setNotice("");

    try {
      if (action === "approve") {
        await approveUser(token(), userId);
      } else {
        await rejectUser(token(), userId);
      }

      setNotice(
        `${person.email} ${action === "approve" ? "approved" : "rejected"}.`
      );
      await loadData();
    } catch (err) {
      setError(err.message || `Could not ${action} user.`);
    } finally {
      setBusy(false);
    }
  }

  if (user?.role !== "hr_admin") {
    return (
      <div className="admin-page">
        <p>Access denied. HR administrator privileges are required.</p>
        <button onClick={onBackToChat}>Back to chat</button>
      </div>
    );
  }

  return (
    <div className="admin-page">
      <header className="admin-topbar">
        <div className="admin-brand">
         
          <div>
            <strong>Ask Safe</strong>
            <p>Administration</p>
          </div>
        </div>

        <div className="admin-top-actions">
          <span>{user.email}</span>
          <button className="admin-quiet-button" onClick={onBackToChat}>
            Back to chat
          </button>
          <button className="admin-quiet-button" onClick={onLogout}>
            Log out
          </button>
        </div>
      </header>

      <main className="admin-content">
        <div className="admin-heading">
          <div>
            
            <h1>Admin dashboard</h1>
            
          </div>
          <button
            className="admin-quiet-button"
            onClick={loadData}
            disabled={loading || busy}
          >
            ↻ Refresh
          </button>
        </div>

        <div className="admin-stats">
          <div className="admin-stat">
            <span>Total documents</span>
            <strong>{documents.length}</strong>
          </div>
          <div className="admin-stat">
            <span>Employee policies</span>
            <strong>{documents.filter(d => d.access_level === "employee").length}</strong>
          </div>
          <div className="admin-stat">
            <span>Manager policies</span>
            <strong>{documents.filter(d => d.access_level === "manager").length}</strong>
          </div>
          <div className="admin-stat">
            <span>Pending requests</span>
            <strong>{pendingUsers.length}</strong>
          </div>
        </div>

        {error && <div className="admin-alert error">{error}</div>}
        {notice && <div className="admin-alert success">{notice}</div>}

        <div className="admin-tabs">
          <button
            className={tab === "documents" ? "active" : ""}
            onClick={() => setTab("documents")}
          >
            Documents <span>{documents.length}</span>
          </button>
          <button
            className={tab === "users" ? "active" : ""}
            onClick={() => setTab("users")}
          >
            Access requests <span>{pendingUsers.length}</span>
          </button>
        </div>

        {loading ? (
          <div className="admin-empty">Loading workspace data…</div>
        ) : tab === "documents" ? (
          <>
            <section className="admin-panel">
              <div className="admin-panel-heading">
                <div>
                  <h2>Upload a policy</h2>
                  <p>PDF only · Maximum file size 10 MB</p>
                </div>
              </div>

              <form className="admin-upload-form" onSubmit={handleUpload}>
                <label className="admin-file-field">
                  <span>Policy PDF</span>
                  <input
                    type="file"
                    accept="application/pdf,.pdf"
                    onChange={event => setFile(event.target.files?.[0] || null)}
                    disabled={busy}
                  />
                  
                </label>

                <label className="admin-select-field">
                  <span>Who can access it?</span>
                  <select
                    value={accessLevel}
                    onChange={event => setAccessLevel(event.target.value)}
                    disabled={busy}
                  >
                    <option value="employee">Employee</option>
                    <option value="manager">Manager</option>
                    <option value="hr">HR only</option>
                  </select>
                </label>

                <button className="admin-primary-button" disabled={busy || !file}>
                  {busy ? "Processing…" : "Upload and index"}
                </button>
              </form>
              <small>{file ? file.name : "Choose a PDF from your device"}</small>
            </section>

            <section className="admin-panel">
              <div className="admin-panel-heading">
                <div>
                  <h2>Policy library</h2>
                  <p>Stored PDFs and their retrieval index status.</p>
                </div>
              </div>

              {documents.length === 0 ? (
                <div className="admin-empty">No documents found.</div>
              ) : (
                <div className="admin-table-wrap">
                  <table className="admin-table">
                    <thead>
                      <tr>
                        <th>Document</th>
                        <th>Access</th>
                        <th>Status</th>
                        <th>Chunks</th>
                        <th></th>
                      </tr>
                    </thead>
                    <tbody>
                      {documents.map(document => (
                        <tr key={document.id}>
                          <td>
                            <div className="admin-document-name">
                              <span className="admin-pdf-icon">PDF</span>
                              <span title={document.filename}>{document.filename}</span>
                            </div>
                          </td>
                          <td>
                            <span className={`admin-access access-${document.access_level}`}>
                              {document.access_level === "hr"
                                ? "HR only"
                                : document.access_level}
                            </span>
                          </td>
                          <td>
                            <span className={`admin-status status-${document.status}`}>
                              {document.status}
                            </span>
                          </td>
                          <td>{document.chunk_count}</td>
                          <td>
                            <button
                              className="admin-delete-button"
                              onClick={() => handleDelete(document)}
                              disabled={busy}
                            >
                              Delete
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>
          </>
        ) : (
          <section className="admin-panel">
            <div className="admin-panel-heading">
              <div>
                <h2>Pending account requests</h2>
                <p>Approve or reject manager and HR registrations.</p>
              </div>
            </div>

            {pendingUsers.length === 0 ? (
              <div className="admin-empty">
                <span className="admin-empty-mark">✓</span>
                <strong>You're all caught up</strong>
                <p>There are no pending access requests.</p>
              </div>
            ) : (
              <div className="admin-request-list">
                {pendingUsers.map(person => (
                  <div className="admin-request" key={person.id}>
                    <div className="admin-request-avatar">
                      {person.email[0].toUpperCase()}
                    </div>
                    <div className="admin-request-details">
                      <strong>{person.email}</strong>
                      <span>
                        Requested role: {person.role.replace("_", " ")}
                      </span>
                      <small>Account status: {person.account_status}</small>
                    </div>
                    <div className="admin-request-actions">
                      <button
                        className="admin-approve-button"
                        onClick={() => handleUserDecision(person.id, "approve")}
                        disabled={busy}
                      >
                        Approve
                      </button>
                      <button
                        className="admin-delete-button"
                        onClick={() => handleUserDecision(person.id, "reject")}
                        disabled={busy}
                      >
                        Reject
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        )}

        
      </main>
    </div>
  );
}
