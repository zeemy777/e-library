import { useRef } from "react";

import { mediaUrl } from "../services/api";

function initials(title) {
  return title
    .split(" ")
    .slice(0, 2)
    .map((word) => word[0])
    .join("")
    .toUpperCase();
}

// Horizontally scrollable row of recently added books. Scroll-snap and
// keyboard-accessible buttons keep the animation useful on every device.
export default function FeaturedShelf({ books = [], onOpen }) {

  const railRef = useRef(null);

  if (!books.length) {
    return null;
  }

  function scrollRail(direction) {
    railRef.current?.scrollBy({
      left: direction * 280,
      behavior: "smooth"
    });
  }

  return (
    <section className="featured-section" aria-labelledby="featured-title">

      <div className="featured-heading reveal">
        <div>
          <span className="eyebrow">FRESH PICKS</span>
          <h2 id="featured-title">New on the shelves</h2>
          <p>A few of the latest arrivals, ready to open.</p>
        </div>

        <div className="featured-controls">
          <button
            type="button"
            aria-label="Scroll featured books left"
            onClick={() => scrollRail(-1)}
          >
            ←
          </button>
          <button
            type="button"
            aria-label="Scroll featured books right"
            onClick={() => scrollRail(1)}
          >
            →
          </button>
        </div>
      </div>

      <div className="featured-rail reveal" ref={railRef}>
        {books.map((book, index) => (
          <button
            type="button"
            className="featured-book"
            key={book.id}
            style={{ "--i": index }}
            onClick={() => onOpen(book)}
          >
            <span className="featured-cover">
              {book.cover_image ? (
                <img src={mediaUrl(book.cover_image)} alt="" />
              ) : (
                <span>{initials(book.title)}</span>
              )}
              <span className="featured-cover-glow" aria-hidden="true" />
            </span>

            <span className="featured-copy">
              <small>{book.category}</small>
              <strong>{book.title}</strong>
              <span>{book.author}</span>
            </span>
          </button>
        ))}
      </div>

    </section>
  );
}
