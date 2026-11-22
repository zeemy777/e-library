
import { mediaUrl } from "../services/api";

// Gradient tones cycle across the catalogue for visual variety.
const COVER_TONES = ["blue", "green", "orange", "purple"];

function initials(title) {

  return title
    .split(" ")
    .slice(0, 2)
    .map((word) => word[0])
    .join("")
    .toUpperCase();
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

function PlayIcon() {

  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M8 5.5v13l11-6.5Z" fill="currentColor" />
    </svg>
  );
}

function ResourceCard({
  resource,
  index = 0,
  isFavorite = false,
  onOpen,
  onFavorite
}) {

  const isVideo = resource.resource_type === "video";

  return (
    <article
      className="book-card reveal"
      style={{ "--reveal-delay": `${(index % 12) * 45}ms` }}
      role="button"
      tabIndex={0}
      onClick={() => onOpen(resource)}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          onOpen(resource);
        }
      }}
    >

      <div className={`book-cover ${COVER_TONES[index % COVER_TONES.length]}`}>

        {resource.cover_image ? (
          <img src={mediaUrl(resource.cover_image)} alt={resource.title} />
        ) : (
          <span>{initials(resource.title)}</span>
        )}

        {isVideo && (
          <span className="cover-play" aria-hidden="true">
            <PlayIcon />
          </span>
        )}

        <button
          type="button"
          className={
            isFavorite
              ? "favorite-button is-active"
              : "favorite-button"
          }
          aria-label={
            isFavorite
              ? `Remove ${resource.title} from your shelf`
              : `Save ${resource.title} to your shelf`
          }
          aria-pressed={isFavorite}
          onClick={(event) => {
            event.stopPropagation();
            onFavorite(resource);
          }}
          onKeyDown={(event) => event.stopPropagation()}
        >
          <HeartIcon />
        </button>

        <span className="cover-shine" aria-hidden="true" />

      </div>

      <div className="book-information">

        <span className="book-category">{resource.category}</span>

        <h3>{resource.title}</h3>

        <p>{resource.author || "Unknown author"}</p>

        <small>
          {resource.description || "No description available."}
        </small>

        <div className="book-footer">

          <span className={isVideo ? "type-chip is-video" : "type-chip"}>
            {isVideo ? "Video" : "Book"}
          </span>

          {resource.average_rating != null && (
            <span
              className="card-rating"
              title={`${resource.average_rating} out of 5`}
            >
              ★ {resource.average_rating}
              {resource.rating_count > 0 &&
                ` (${resource.rating_count})`}
            </span>
          )}

          <span className="card-link">View details →</span>

        </div>

      </div>

    </article>
  );
}

export default ResourceCard;
