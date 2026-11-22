import { useEffect, useState } from "react";

import { API_BASE_URL, apiRequest, mediaUrl } from "../services/api";

// Convert common video links into an embeddable player address.
// Returns null when the link should be played directly instead.
function getVideoEmbedUrl(url) {

  // YouTube links: watch, share and embed formats.
  const youtube = url.match(
    /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([\w-]+)/
  );

  if (youtube) {
    return `https://www.youtube.com/embed/${youtube[1]}`;
  }

  // Vimeo links.
  const vimeo = url.match(/vimeo\.com\/(\d+)/);

  if (vimeo) {
    return `https://player.vimeo.com/video/${vimeo[1]}`;
  }

  return null;
}

function HeartIcon() {

  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path
        d="M12 20.8 4.6 13.6a5 5 0 0 1 0-7.2 5.2 5.2 0 0 1 7.3 0l.1.1.1-.1a5.2 5.2 0 0 1 7.3 0 5 5 0 0 1 0 7.2Z"
        fill="currentColor"
      />
    </svg>
  );
}

// Row of stars showing an average rating out of five.
function Stars({ value = 0 }) {
  const filled = Math.round(value);

  return (
    <span className="stars" aria-hidden="true">
      {[1, 2, 3, 4, 5].map((star) => (
        <span
          key={star}
          className={
            star <= filled ? "star is-filled" : "star"
          }
        >
          ★
        </span>
      ))}
    </span>
  );
}

// Clickable star selector used in the review form.
function StarPicker({ value, onChange }) {

  return (
    <div className="star-picker">
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          type="button"
          className={
            star <= value ? "star is-filled" : "star"
          }
          onClick={() => onChange(star)}
          aria-label={`${star} star${star > 1 ? "s" : ""}`}
          aria-pressed={star === value}
        >
          ★
        </button>
      ))}
    </div>
  );
}

function formatDay(value) {
  if (!value) return "";
  return new Date(value).toLocaleDateString(undefined, {
    day: "numeric",
    month: "short",
    year: "numeric"
  });
}

// Ratings and member reviews for a single resource.
function ReviewSection({ resource, currentUser }) {

  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState("");
  const [formError, setFormError] = useState("");
  const [formSuccess, setFormSuccess] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function loadReviews() {
    try {
      const result = await apiRequest(
        `/api/resources/${resource.id}/reviews`
      );
      const list = result.reviews || [];
      setReviews(list);

      const mine = list.find((review) => review.mine);

      if (mine) {
        setRating(mine.rating);
        setComment(mine.comment || "");
      }

    } catch {
      // Reviews are a bonus feature — fail quietly.
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadReviews();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [resource.id]);

  const average = reviews.length
    ? Math.round(
        (reviews.reduce((sum, item) => sum + item.rating, 0)
          / reviews.length) * 10
      ) / 10
    : null;

  const myReview = reviews.find((review) => review.mine);

  async function handleSubmit(event) {
    event.preventDefault();
    setFormError("");
    setFormSuccess("");

    if (rating < 1) {
      setFormError("Pick a star rating first.");
      return;
    }

    setSubmitting(true);

    try {
      const result = await apiRequest(
        `/api/resources/${resource.id}/reviews`,
        {
          method: "POST",
          body: JSON.stringify({ rating, comment })
        }
      );

      setFormSuccess(result.message || "Your review was saved.");
      await loadReviews();

    } catch (err) {
      setFormError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete() {
    setFormError("");
    setFormSuccess("");

    try {
      const result = await apiRequest(
        `/api/resources/${resource.id}/reviews/mine`,
        { method: "DELETE" }
      );

      setFormSuccess(result.message || "Your review was removed.");
      setRating(0);
      setComment("");
      await loadReviews();

    } catch (err) {
      setFormError(err.message);
    }
  }

  return (
    <section className="review-section">

      <div className="review-summary">
        <Stars value={average || 0} />
        <span>
          {average === null
            ? "No reviews yet"
            : `${average} · ${reviews.length} review${
                reviews.length === 1 ? "" : "s"
              }`}
        </span>
      </div>

      {currentUser && (
        <form className="review-form" onSubmit={handleSubmit}>

          <span className="review-form-label">
            {myReview ? "Your review (edit any time)" : "Write a review"}
          </span>

          <StarPicker value={rating} onChange={setRating} />

          <textarea
            className="review-input"
            rows="3"
            maxLength="1000"
            placeholder="What did you think? (optional)"
            value={comment}
            onChange={(event) => setComment(event.target.value)}
          />

          {formError && <p className="form-error">{formError}</p>}
          {formSuccess && (
            <p className="form-success">{formSuccess}</p>
          )}

          <div className="review-form-actions">
            <button
              type="submit"
              className="primary-button"
              disabled={submitting}
            >
              {submitting
                ? "Saving..."
                : myReview
                  ? "Update review"
                  : "Post review"}
            </button>

            {myReview && (
              <button
                type="button"
                className="secondary-button"
                onClick={handleDelete}
              >
                Delete my review
              </button>
            )}
          </div>

        </form>
      )}

      {!loading && reviews.length > 0 && (
        <div className="review-list">
          {reviews.map((review) => (
            <article className="review-card" key={review.id}>
              <div className="review-head">
                <Stars value={review.rating} />
                <strong>{review.reviewer}</strong>
                {review.mine && (
                  <span className="review-mine">you</span>
                )}
                <small>{formatDay(review.created_at)}</small>
              </div>
              {review.comment && <p>{review.comment}</p>}
            </article>
          ))}
        </div>
      )}

    </section>
  );
}

// Detail view for a single book or video tutorial.
function ResourceModal({
  resource,
  currentUser,
  isFavorite = false,
  isBorrowed = false,
  borrowedLoan = null,
  onFavorite,
  onBorrow,
  onClose
}) {

  const isVideo = resource.resource_type === "video";

  const embedUrl = isVideo && resource.video_url
    ? getVideoEmbedUrl(resource.video_url)
    : null;

  return (
    <div
      className="modal-backdrop"
      onClick={onClose}
      role="presentation"
    >
      <div
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-label={resource.title}
        onClick={(event) => event.stopPropagation()}
      >

        <button
          type="button"
          className="modal-close"
          onClick={onClose}
          aria-label="Close details"
        >
          ×
        </button>

        {/* Video or cover area */}
        {isVideo ? (
          <div className="modal-media">

            {embedUrl ? (
              <iframe
                src={embedUrl}
                title={resource.title}
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              />
            ) : resource.video_url ? (
              <video src={mediaUrl(resource.video_url)} controls />
            ) : (
              <p className="modal-hint">
                This video is not available yet.
              </p>
            )}

          </div>
        ) : (
          <div className="modal-cover">

            {resource.cover_image ? (
              <img
                src={mediaUrl(resource.cover_image)}
                alt={resource.title}
              />
            ) : (
              <span>
                {resource.title
                  .split(" ")
                  .slice(0, 2)
                  .map((word) => word[0])
                  .join("")
                  .toUpperCase()}
              </span>
            )}

          </div>
        )}

        <div className="modal-body">

          <span className="book-category">
            {resource.category} · {isVideo ? "Video Tutorial" : "Book"}
          </span>

          <h2>{resource.title}</h2>

          <p className="modal-meta">
            {resource.author || "Unknown author"}
            {resource.publisher ? ` · ${resource.publisher}` : ""}
          </p>

          <p>
            {resource.description || "No description available."}
          </p>

          <button
            type="button"
            className={
              isFavorite
                ? "shelf-save is-active"
                : "shelf-save"
            }
            onClick={() => onFavorite(resource)}
            aria-pressed={isFavorite}
          >
            <HeartIcon />
            {isFavorite
              ? "Saved to your shelf"
              : "Save to your shelf"}
          </button>

          {/* Borrowing is only offered for books. */}
          {!isVideo && (
            <div className="borrow-row">

              {isBorrowed ? (
                <p className="modal-hint">
                  On your loans
                  {borrowedLoan?.due_date
                    ? ` · due ${formatDay(borrowedLoan.due_date)}`
                    : ""}
                  . Find it under “My Loans”.
                </p>
              ) : (
                <button
                  type="button"
                  className="borrow-button"
                  onClick={() => onBorrow(resource)}
                >
                  Borrow this book · free for 14 days
                </button>
              )}

            </div>
          )}

          {/* Reading and download options for books */}
          {!isVideo && (
            <div className="download-row">

              {!currentUser && (
                <p className="modal-hint">
                  Log in to read or download this book.
                </p>
              )}

              {currentUser && resource.readable && (
                <a
                  className="primary-button"
                  href={
                    `${API_BASE_URL}/api/resources/` +
                    `${resource.id}/read`
                  }
                  target="_blank"
                  rel="noreferrer"
                >
                  Read online
                </a>
              )}

              {currentUser && !resource.can_download && (
                <p className="modal-hint">
                  Download is not permitted for this book.
                </p>
              )}

              {currentUser && resource.can_download
                && !resource.has_file && (
                <p className="modal-hint">
                  The book file has not been uploaded yet.
                </p>
              )}

              {currentUser && resource.can_download
                && resource.has_file && (
                <a
                  className="secondary-button"
                  href={
                    `${API_BASE_URL}/api/resources/` +
                    `${resource.id}/download`
                  }
                >
                  Download this book
                </a>
              )}

            </div>
          )}

          <ReviewSection
            resource={resource}
            currentUser={currentUser}
          />

        </div>

      </div>
    </div>
  );
}

export default ResourceModal;
