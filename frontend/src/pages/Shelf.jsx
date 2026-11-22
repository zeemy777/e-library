
import ResourceCard from "../components/ResourceCard";

function Shelf({
  currentUser,
  resources,
  loading,
  onHome,
  onOpen,
  onFavorite
}) {

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

        <span className="eyebrow">YOUR COLLECTION</span>

        <h1>My Shelf</h1>

        <p>
          Saved books and videos for{" "}
          <strong>{currentUser.full_name}</strong>. Tap the heart
          on any card to add it here.
        </p>

        <span className="shelf-pill">
          {resources.length} saved
        </span>

      </section>

      <section className="section shelf-content">

        {loading && (
          <div className="book-grid">
            {[0, 1, 2, 3].map((item) => (
              <div className="skeleton-card" key={item}>
                <div className="skeleton-cover" />
                <div className="skeleton-line" />
                <div className="skeleton-line short" />
              </div>
            ))}
          </div>
        )}

        {!loading && resources.length === 0 && (
          <div className="shelf-empty">

            <span className="shelf-empty-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24">
                <path
                  d="M12 20.8 4.6 13.6a5 5 0 0 1 0-7.2 5.2 5.2 0 0 1 7.3 0l.1.1.1-.1a5.2 5.2 0 0 1 7.3 0 5 5 0 0 1 0 7.2Z"
                  fill="currentColor"
                />
              </svg>
            </span>

            <h2>Your shelf is empty</h2>

            <p>
              Save books you want to read later so they are always
              one click away.
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

        {!loading && resources.length > 0 && (
          <div className="book-grid">
            {resources.map((resource, index) => (
              <ResourceCard
                key={resource.id}
                resource={resource}
                index={index}
                isFavorite
                onOpen={onOpen}
                onFavorite={onFavorite}
              />
            ))}
          </div>
        )}

      </section>

    </div>
  );
}

export default Shelf;
