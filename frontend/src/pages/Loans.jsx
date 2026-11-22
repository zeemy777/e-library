import { useEffect, useState } from "react";
import { apiRequest, mediaUrl } from "../services/api";

function formatDay(value) {
  if (!value) return "—";
  return new Date(value).toLocaleDateString(undefined, {
    day: "numeric",
    month: "short",
    year: "numeric"
  });
}

function initials(title) {
  return title
    .split(" ")
    .slice(0, 2)
    .map((word) => word[0])
    .join("")
    .toUpperCase();
}

function dueInfo(loan) {
  const days = Math.ceil(
    (new Date(loan.due_date).getTime() - Date.now()) / 86400000
  );

  if (loan.status === "overdue") {
    return {
      className: "loan-status is-overdue",
      text:
        days < -1
          ? `Overdue by ${-days} days`
          : "Overdue"
    };
  }

  if (days <= 0) {
    return { className: "loan-status is-due", text: "Due today" };
  }

  if (days === 1) {
    return { className: "loan-status is-due", text: "Due tomorrow" };
  }

  return {
    className: "loan-status",
    text: `Due ${formatDay(loan.due_date)} · ${days} days left`
  };
}

function Loans({ currentUser, onHome, onOpen, onReturn }) {

  const [active, setActive] = useState([]);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [returningId, setReturningId] = useState(null);

  async function load() {
    setLoading(true);
    setError("");

    try {
      const result = await apiRequest("/api/loans/mine");
      setActive(result.active || []);
      setHistory(result.history || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleReturn(loan) {
    setReturningId(loan.id);

    try {
      await onReturn(loan);
      await load();
    } catch {
      // App.jsx already shows a toast for the failure.
    } finally {
      setReturningId(null);
    }
  }

  return (
    <div className="shelf-page">

      <header className="shelf-topbar">

        <a href="#home" className="brand" onClick={onHome}>
          <span className="brand-icon">E</span>
          <span>E-Library</span>
        </a>

        <button
          type="button"
          className="auth-nav-button"
          onClick={onHome}
        >
          Back to library
        </button>

      </header>

      <section className="shelf-hero">

        <span className="eyebrow">YOUR BORROWINGS</span>

        <h1>My Loans</h1>

        <p>
          Books borrowed by{" "}
          <strong>{currentUser.full_name}</strong>. Loans are
          free for 14 days — return them any time.
        </p>

        <span className="shelf-pill">
          {active.length} active
        </span>

      </section>

      <section className="section shelf-content">

        {error && <p className="form-error">{error}</p>}

        {loading && (
          <div className="loan-list">
            {[0, 1].map((item) => (
              <div className="skeleton-card loan-skeleton" key={item}>
                <div className="skeleton-cover" />
                <div className="skeleton-line" />
                <div className="skeleton-line short" />
              </div>
            ))}
          </div>
        )}

        {!loading && active.length === 0 && (
          <div className="shelf-empty">

            <span className="shelf-empty-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24">
                <path
                  d="M5 4.5A2.5 2.5 0 0 1 7.5 2H19v17.5a2.5 2.5 0 0 1-2.5 2.5H7.5A2.5 2.5 0 0 1 5 19.5ZM5 19.5V4.5M9 7h6M9 11h4"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.6"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </span>

            <h2>No active loans</h2>

            <p>
              Borrow any book from the catalogue and it will
              appear here with its due date.
            </p>

            <button
              type="button"
              className="primary-button"
              onClick={onHome}
            >
              Browse the library
            </button>

          </div>
        )}

        {!loading && active.length > 0 && (
          <div className="loan-list">
            {active.map((loan) => {
              const due = dueInfo(loan);

              return (
                <article className="loan-card" key={loan.id}>

                  <button
                    type="button"
                    className="loan-cover"
                    onClick={() => onOpen(loan.resource)}
                    aria-label={`View ${loan.resource.title}`}
                  >
                    {loan.resource.cover_image ? (
                      <img
                        src={mediaUrl(loan.resource.cover_image)}
                        alt=""
                      />
                    ) : (
                      <span>{initials(loan.resource.title)}</span>
                    )}
                  </button>

                  <div className="loan-info">

                    <span className="book-category">
                      {loan.resource.category}
                    </span>

                    <h3>{loan.resource.title}</h3>

                    <p>
                      Borrowed {formatDay(loan.borrowed_at)}
                    </p>

                    <span className={due.className}>
                      {due.text}
                    </span>

                  </div>

                  <div className="loan-actions">

                    <button
                      type="button"
                      className="secondary-button"
                      onClick={() => onOpen(loan.resource)}
                    >
                      View book
                    </button>

                    <button
                      type="button"
                      className="primary-button"
                      disabled={returningId === loan.id}
                      onClick={() => handleReturn(loan)}
                    >
                      {returningId === loan.id
                        ? "Returning..."
                        : "Return book"}
                    </button>

                  </div>

                </article>
              );
            })}
          </div>
        )}

        {!loading && history.length > 0 && (
          <>
            <h2 className="loan-history-heading">
              Loan history
            </h2>

            <div className="table-wrap">
              <table className="admin-table loan-history">
                <thead>
                  <tr>
                    <th>Title</th>
                    <th>Borrowed</th>
                    <th>Due</th>
                    <th>Returned</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((loan) => (
                    <tr key={loan.id}>
                      <td>{loan.resource.title}</td>
                      <td>{formatDay(loan.borrowed_at)}</td>
                      <td>{formatDay(loan.due_date)}</td>
                      <td>{formatDay(loan.returned_at)}</td>
                      <td>
                        <span
                          className={
                            loan.status === "overdue"
                              ? "loan-status is-overdue"
                              : "loan-status is-returned"
                          }
                        >
                          {loan.status === "overdue"
                            ? "Returned late"
                            : "Returned"}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}

      </section>

    </div>
  );
}

export default Loans;
