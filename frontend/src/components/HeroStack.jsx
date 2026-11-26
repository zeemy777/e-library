import { mediaUrl } from "../services/api";

function initials(title) {
  return title
    .split(" ")
    .slice(0, 2)
    .map((word) => word[0])
    .join("")
    .toUpperCase();
}

// A small animated fan of real covers from the top of the catalogue.
export default function HeroStack({ books = [] }) {

  const covers = books.slice(0, 3);

  return (
    <div className="hero-stack" aria-hidden="true">
      {covers.map((book, index) => (
        <div
          className={`hero-stack-book hero-stack-book-${index}`}
          key={book.id}
          style={{ "--i": index }}
        >
          {book.cover_image ? (
            <img src={mediaUrl(book.cover_image)} alt="" />
          ) : (
            <span>{initials(book.title)}</span>
          )}
          <span className="hero-stack-shine" />
        </div>
      ))}
    </div>
  );
}
