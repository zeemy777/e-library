
import { useEffect, useState } from "react";
import { apiRequest } from "../services/api";
import ThemeToggle from "../components/ThemeToggle";

// Sidebar sections for the admin area.
const SECTIONS = [
  { key: "dashboard", label: "Dashboard" },
  { key: "categories", label: "Categories" },
  { key: "types", label: "Book Types" },
  { key: "resources", label: "Books & Videos" },
  { key: "loans", label: "Loans" },
  { key: "messages", label: "Messages" },
  { key: "report", label: "Report" },
  { key: "users", label: "Users" },
  { key: "profile", label: "Profile" }
];

// Capitalize a stored lowercase value such as "book".
function labelOf(value) {
  if (!value) return "";
  return value.charAt(0).toUpperCase() + value.slice(1);
}

// Display a readable date.
function formatDate(value) {
  return value ? new Date(value).toLocaleString() : "—";
}

// =====================================
// DASHBOARD
// =====================================

function Dashboard() {

  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    apiRequest("/api/admin/dashboard")
      .then(setData)
      .catch((err) => setError(err.message));
  }, []);

  if (error) {
    return <p className="form-error">{error}</p>;
  }

  if (!data) {
    return <p className="loading-message">Loading dashboard...</p>;
  }

  const stats = data.stats;

  const cards = [
    { label: "Resources", value: stats.resources },
    { label: "Books", value: stats.books },
    { label: "Videos", value: stats.videos },
    { label: "Categories", value: stats.categories },
    { label: "Book Types", value: stats.book_types },
    { label: "Members", value: stats.members },
    { label: "Active Loans", value: stats.active_loans },
    { label: "Overdue Loans", value: stats.overdue_loans },
    { label: "New Messages", value: stats.new_messages }
  ];

  return (
    <>
      <h2 className="admin-heading">Dashboard</h2>

      <div className="stat-grid">
        {cards.map((card) => (
          <div className="stat-card" key={card.label}>
            <strong>{card.value}</strong>
            <span>{card.label}</span>
          </div>
        ))}
      </div>

      <h3 className="admin-subheading">Recently Added</h3>

      <div className="table-wrap">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Title</th>
              <th>Type</th>
              <th>Category</th>
              <th>Published</th>
              <th>Added</th>
            </tr>
          </thead>
          <tbody>
            {data.recent_resources.map((resource) => (
              <tr key={resource.id}>
                <td>{resource.title}</td>
                <td>{labelOf(resource.resource_type)}</td>
                <td>{resource.category}</td>
                <td>
                  {resource.is_published ? "Yes" : "No"}
                </td>
                <td>{formatDate(resource.created_at)}</td>
              </tr>
            ))}
            {data.recent_resources.length === 0 && (
              <tr>
                <td colSpan="5">No resources yet.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </>
  );
}

// =====================================
// CATEGORIES
// =====================================

const emptyCategory = {
  id: null,
  name: "",
  description: "",
  allow_download: false
};

function CategoriesManager() {

  const [categories, setCategories] = useState([]);
  const [form, setForm] = useState(emptyCategory);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  async function load() {
    const result = await apiRequest("/api/admin/categories");
    setCategories(result.categories || []);
  }

  useEffect(() => {
    load().catch((err) => setError(err.message));
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setNotice("");

    try {
      const result = await apiRequest(
        form.id
          ? `/api/admin/categories/${form.id}`
          : "/api/admin/categories",
        {
          method: form.id ? "PUT" : "POST",
          body: JSON.stringify({
            name: form.name,
            description: form.description,
            allow_download: form.allow_download
          })
        }
      );

      setNotice(result.message);
      setForm(emptyCategory);
      await load();

    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDelete(category) {
    if (!window.confirm(`Delete category "${category.name}"?`)) {
      return;
    }

    setError("");
    setNotice("");

    try {
      const result = await apiRequest(
        `/api/admin/categories/${category.id}`,
        { method: "DELETE" }
      );
      setNotice(result.message);
      await load();

    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <>
      <h2 className="admin-heading">Categories</h2>

      {notice && <p className="form-success">{notice}</p>}
      {error && <p className="form-error">{error}</p>}

      <form className="admin-form" onSubmit={handleSubmit}>
        <div className="form-grid">
          <div>
            <label>Category Name</label>
            <input
              type="text"
              value={form.name}
              onChange={(event) =>
                setForm({ ...form, name: event.target.value })
              }
              required
            />
          </div>

          <div>
            <label>Description</label>
            <input
              type="text"
              value={form.description}
              onChange={(event) =>
                setForm({
                  ...form,
                  description: event.target.value
                })
              }
            />
          </div>

          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={form.allow_download}
              onChange={(event) =>
                setForm({
                  ...form,
                  allow_download: event.target.checked
                })
              }
            />
            Allow downloads by default
          </label>
        </div>

        <div className="button-row">
          <button type="submit" className="admin-button">
            {form.id ? "Save Changes" : "Add Category"}
          </button>

          {form.id && (
            <button
              type="button"
              className="admin-button secondary"
              onClick={() => setForm(emptyCategory)}
            >
              Cancel
            </button>
          )}
        </div>
      </form>

      <div className="table-wrap">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Description</th>
              <th>Downloads</th>
              <th>Resources</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {categories.map((category) => (
              <tr key={category.id}>
                <td>{category.name}</td>
                <td>{category.description || "—"}</td>
                <td>
                  {category.allow_download ? "Allowed" : "Blocked"}
                </td>
                <td>{category.resource_count}</td>
                <td className="table-actions">
                  <button
                    type="button"
                    onClick={() => setForm(category)}
                  >
                    Edit
                  </button>
                  <button
                    type="button"
                    className="danger"
                    onClick={() => handleDelete(category)}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
            {categories.length === 0 && (
              <tr>
                <td colSpan="5">No categories yet.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </>
  );
}

// =====================================
// BOOK TYPES
// =====================================

const emptyType = { id: null, name: "", description: "" };

function TypesManager() {

  const [types, setTypes] = useState([]);
  const [form, setForm] = useState(emptyType);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  async function load() {
    const result = await apiRequest("/api/admin/book-types");
    setTypes(result.book_types || []);
  }

  useEffect(() => {
    load().catch((err) => setError(err.message));
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setNotice("");

    try {
      const result = await apiRequest(
        form.id
          ? `/api/admin/book-types/${form.id}`
          : "/api/admin/book-types",
        {
          method: form.id ? "PUT" : "POST",
          body: JSON.stringify({
            name: form.name,
            description: form.description
          })
        }
      );

      setNotice(result.message);
      setForm(emptyType);
      await load();

    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDelete(bookType) {
    if (!window.confirm(`Delete book type "${bookType.name}"?`)) {
      return;
    }

    setError("");
    setNotice("");

    try {
      const result = await apiRequest(
        `/api/admin/book-types/${bookType.id}`,
        { method: "DELETE" }
      );
      setNotice(result.message);
      await load();

    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <>
      <h2 className="admin-heading">Book Types</h2>

      {notice && <p className="form-success">{notice}</p>}
      {error && <p className="form-error">{error}</p>}

      <form className="admin-form" onSubmit={handleSubmit}>
        <div className="form-grid">
          <div>
            <label>Type Name</label>
            <input
              type="text"
              value={form.name}
              onChange={(event) =>
                setForm({ ...form, name: event.target.value })
              }
              placeholder="e.g. book, video, magazine"
              required
            />
          </div>

          <div>
            <label>Description</label>
            <input
              type="text"
              value={form.description}
              onChange={(event) =>
                setForm({
                  ...form,
                  description: event.target.value
                })
              }
            />
          </div>
        </div>

        <div className="button-row">
          <button type="submit" className="admin-button">
            {form.id ? "Save Changes" : "Add Book Type"}
          </button>

          {form.id && (
            <button
              type="button"
              className="admin-button secondary"
              onClick={() => setForm(emptyType)}
            >
              Cancel
            </button>
          )}
        </div>
      </form>

      <div className="table-wrap">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Description</th>
              <th>Resources</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {types.map((bookType) => (
              <tr key={bookType.id}>
                <td>{labelOf(bookType.name)}</td>
                <td>{bookType.description || "—"}</td>
                <td>{bookType.resource_count}</td>
                <td className="table-actions">
                  <button
                    type="button"
                    onClick={() => setForm(bookType)}
                  >
                    Edit
                  </button>
                  <button
                    type="button"
                    className="danger"
                    onClick={() => handleDelete(bookType)}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

// =====================================
// RESOURCES
// =====================================

const emptyResource = {
  id: null,
  title: "",
  resource_type: "",
  category_id: "",
  author: "",
  publisher: "",
  description: "",
  video_url: "",
  download_override: "inherit",
  is_published: false
};

function ResourcesManager() {

  const [resources, setResources] = useState([]);
  const [categories, setCategories] = useState([]);
  const [types, setTypes] = useState([]);

  const [filters, setFilters] = useState({
    search: "",
    category_id: "",
    resource_type: ""
  });

  const [form, setForm] = useState(emptyResource);
  const [file, setFile] = useState(null);
  const [cover, setCover] = useState(null);
  const [formKey, setFormKey] = useState(0);

  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [loading, setLoading] = useState(true);

  // Load categories and book types once.
  useEffect(() => {
    Promise.all([
      apiRequest("/api/admin/categories"),
      apiRequest("/api/admin/book-types")
    ])
      .then(([categoryResult, typeResult]) => {
        setCategories(categoryResult.categories || []);
        setTypes(typeResult.book_types || []);
      })
      .catch((err) => setError(err.message));
  }, []);

  // Reload resources whenever the filters change.
  useEffect(() => {
    let cancelled = false;

    async function loadResources() {
      setLoading(true);

      try {
        const params = new URLSearchParams();

        if (filters.search.trim()) {
          params.set("search", filters.search.trim());
        }

        if (filters.category_id) {
          params.set("category_id", filters.category_id);
        }

        if (filters.resource_type) {
          params.set("resource_type", filters.resource_type);
        }

        const query = params.toString();

        const result = await apiRequest(
          `/api/admin/resources${query ? `?${query}` : ""}`
        );

        if (!cancelled) {
          setResources(result.resources || []);
        }

      } catch (err) {
        if (!cancelled) setError(err.message);

      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadResources();

    return () => {
      cancelled = true;
    };
  }, [filters]);

  function resetForm() {
    setForm(emptyResource);
    setFile(null);
    setCover(null);
    setFormKey((key) => key + 1);
  }

  function handleEdit(resource) {
    setError("");
    setNotice("");

    setForm({
      id: resource.id,
      title: resource.title,
      resource_type: resource.resource_type,
      category_id: String(resource.category_id),
      author: resource.author || "",
      publisher: resource.publisher || "",
      description: resource.description || "",
      video_url: resource.video_url || "",
      download_override:
        resource.download_override === null
          ? "inherit"
          : resource.download_override ? "allow" : "deny",
      is_published: resource.is_published
    });

    setFile(null);
    setCover(null);
    setFormKey((key) => key + 1);

    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setNotice("");

    const data = new FormData();

    data.append("title", form.title);
    data.append("resource_type", form.resource_type);
    data.append("category_id", form.category_id);
    data.append("author", form.author);
    data.append("publisher", form.publisher);
    data.append("description", form.description);
    data.append("video_url", form.video_url);
    data.append("download_override", form.download_override);
    data.append(
      "is_published",
      form.is_published ? "true" : "false"
    );

    if (file) data.append("file", file);
    if (cover) data.append("cover", cover);

    try {
      const result = await apiRequest(
        form.id
          ? `/api/admin/resources/${form.id}`
          : "/api/admin/resources",
        {
          method: form.id ? "PUT" : "POST",
          body: data
        }
      );

      setNotice(result.message);
      resetForm();

      // Refresh the table with the current filters.
      setFilters({ ...filters });

    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDelete(resource) {
    if (!window.confirm(`Delete "${resource.title}"?`)) {
      return;
    }

    setError("");
    setNotice("");

    try {
      const result = await apiRequest(
        `/api/admin/resources/${resource.id}`,
        { method: "DELETE" }
      );
      setNotice(result.message);
      setFilters({ ...filters });

    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <>
      <h2 className="admin-heading">Books &amp; Videos</h2>

      {notice && <p className="form-success">{notice}</p>}
      {error && <p className="form-error">{error}</p>}

      <form
        key={formKey}
        className="admin-form"
        onSubmit={handleSubmit}
      >
        <h3 className="admin-subheading">
          {form.id ? `Edit: ${form.title}` : "Add New Resource"}
        </h3>

        <div className="form-grid">
          <div>
            <label>Title</label>
            <input
              type="text"
              value={form.title}
              onChange={(event) =>
                setForm({ ...form, title: event.target.value })
              }
              required
            />
          </div>

          <div>
            <label>Book Type</label>
            <select
              value={form.resource_type}
              onChange={(event) =>
                setForm({
                  ...form,
                  resource_type: event.target.value
                })
              }
              required
            >
              <option value="">Select a type</option>
              {types.map((bookType) => (
                <option
                  key={bookType.id}
                  value={bookType.name}
                >
                  {labelOf(bookType.name)}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label>Category</label>
            <select
              value={form.category_id}
              onChange={(event) =>
                setForm({
                  ...form,
                  category_id: event.target.value
                })
              }
              required
            >
              <option value="">Select a category</option>
              {categories.map((category) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label>Author</label>
            <input
              type="text"
              value={form.author}
              onChange={(event) =>
                setForm({ ...form, author: event.target.value })
              }
            />
          </div>

          <div>
            <label>Publisher</label>
            <input
              type="text"
              value={form.publisher}
              onChange={(event) =>
                setForm({
                  ...form,
                  publisher: event.target.value
                })
              }
            />
          </div>

          <div>
            <label>Video URL</label>
            <input
              type="url"
              value={form.video_url}
              onChange={(event) =>
                setForm({
                  ...form,
                  video_url: event.target.value
                })
              }
              placeholder="https://..."
            />
          </div>

          <div>
            <label>Download Permission</label>
            <select
              value={form.download_override}
              onChange={(event) =>
                setForm({
                  ...form,
                  download_override: event.target.value
                })
              }
            >
              <option value="inherit">
                Inherit from category
              </option>
              <option value="allow">Allow download</option>
              <option value="deny">Block download</option>
            </select>
          </div>

          <div>
            <label>Book File (PDF / EPUB)</label>
            <input
              type="file"
              accept=".pdf,.epub"
              onChange={(event) =>
                setFile(event.target.files[0] || null)
              }
            />
          </div>

          <div>
            <label>Cover Image</label>
            <input
              type="file"
              accept="image/*"
              onChange={(event) =>
                setCover(event.target.files[0] || null)
              }
            />
          </div>

          <div className="form-wide">
            <label>Description</label>
            <textarea
              rows={3}
              value={form.description}
              onChange={(event) =>
                setForm({
                  ...form,
                  description: event.target.value
                })
              }
            />
          </div>

          <label className="checkbox-label form-wide">
            <input
              type="checkbox"
              checked={form.is_published}
              onChange={(event) =>
                setForm({
                  ...form,
                  is_published: event.target.checked
                })
              }
            />
            Published (visible in the catalogue)
          </label>
        </div>

        <div className="button-row">
          <button type="submit" className="admin-button">
            {form.id ? "Save Changes" : "Add Resource"}
          </button>

          {form.id && (
            <button
              type="button"
              className="admin-button secondary"
              onClick={resetForm}
            >
              Cancel
            </button>
          )}
        </div>
      </form>

      <div className="filter-row">
        <input
          type="text"
          placeholder="Search title, author or publisher"
          value={filters.search}
          onChange={(event) =>
            setFilters({ ...filters, search: event.target.value })
          }
        />

        <select
          value={filters.category_id}
          onChange={(event) =>
            setFilters({
              ...filters,
              category_id: event.target.value
            })
          }
        >
          <option value="">All categories</option>
          {categories.map((category) => (
            <option key={category.id} value={category.id}>
              {category.name}
            </option>
          ))}
        </select>

        <select
          value={filters.resource_type}
          onChange={(event) =>
            setFilters({
              ...filters,
              resource_type: event.target.value
            })
          }
        >
          <option value="">All types</option>
          {types.map((bookType) => (
            <option
              key={bookType.id}
              value={bookType.name}
            >
              {labelOf(bookType.name)}
            </option>
          ))}
        </select>
      </div>

      {loading ? (
        <p className="loading-message">Loading resources...</p>
      ) : (
        <div className="table-wrap">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Type</th>
                <th>Category</th>
                <th>Published</th>
                <th>File</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {resources.map((resource) => (
                <tr key={resource.id}>
                  <td>{resource.title}</td>
                  <td>{labelOf(resource.resource_type)}</td>
                  <td>{resource.category}</td>
                  <td>
                    <span
                      className={
                        resource.is_published
                          ? "badge success"
                          : "badge"
                      }
                    >
                      {resource.is_published ? "Yes" : "No"}
                    </span>
                  </td>
                  <td>
                    {resource.has_file ? "Uploaded" : "—"}
                  </td>
                  <td className="table-actions">
                    <button
                      type="button"
                      onClick={() => handleEdit(resource)}
                    >
                      Edit
                    </button>
                    <button
                      type="button"
                      className="danger"
                      onClick={() => handleDelete(resource)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
              {resources.length === 0 && (
                <tr>
                  <td colSpan="6">No resources found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}

// =====================================
// LOANS
// =====================================

const LOAN_FILTERS = [
  { key: "all", label: "All" },
  { key: "active", label: "Active" },
  { key: "overdue", label: "Overdue" },
  { key: "returned", label: "Returned" }
];

function LoansManager() {

  const [status, setStatus] = useState("active");
  const [loans, setLoans] = useState([]);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  useEffect(() => {
    setError("");

    apiRequest(`/api/admin/loans?status=${status}`)
      .then((result) => setLoans(result.loans || []))
      .catch((err) => setError(err.message));
  }, [status]);

  async function markReturned(loan) {
    setError("");
    setNotice("");

    try {
      const result = await apiRequest(
        `/api/admin/loans/${loan.id}/return`,
        { method: "POST" }
      );

      setNotice(result.message);

      const refreshed = await apiRequest(
        `/api/admin/loans?status=${status}`
      );
      setLoans(refreshed.loans || []);

    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <>
      <h2 className="admin-heading">Book Loans</h2>

      {notice && <p className="form-success">{notice}</p>}
      {error && <p className="form-error">{error}</p>}

      <div className="category-list loan-filters">
        {LOAN_FILTERS.map((filter) => (
          <button
            type="button"
            key={filter.key}
            className={
              status === filter.key
                ? "category-button active"
                : "category-button"
            }
            onClick={() => setStatus(filter.key)}
          >
            {filter.label}
          </button>
        ))}
      </div>

      {loans.length === 0 ? (
        <p className="empty-message">No loans in this view.</p>
      ) : (
        <div className="table-wrap">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Book</th>
                <th>Member</th>
                <th>Borrowed</th>
                <th>Due</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {loans.map((loan) => (
                <tr key={loan.id}>
                  <td>{loan.resource.title}</td>
                  <td>
                    {loan.member.full_name}
                    <br />
                    <small>{loan.member.email}</small>
                  </td>
                  <td>{formatDate(loan.borrowed_at)}</td>
                  <td>{formatDate(loan.due_date)}</td>
                  <td>
                    <span
                      className={
                        loan.status === "overdue"
                          ? "badge warning"
                          : loan.status === "returned"
                            ? "badge"
                            : "badge success"
                      }
                    >
                      {loan.status}
                    </span>
                  </td>
                  <td>
                    {loan.status !== "returned" && (
                      <button
                        type="button"
                        onClick={() => markReturned(loan)}
                      >
                        Mark returned
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}

// =====================================
// MESSAGES
// =====================================

function MessagesManager() {

  const [messages, setMessages] = useState([]);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  async function load() {
    const result = await apiRequest("/api/admin/messages");
    setMessages(result.messages || []);
  }

  useEffect(() => {
    load().catch((err) => setError(err.message));
  }, []);

  async function setStatus(message, status) {
    setError("");
    setNotice("");

    try {
      const result = await apiRequest(
        `/api/admin/messages/${message.id}`,
        {
          method: "PATCH",
          body: JSON.stringify({ status })
        }
      );
      setNotice(result.message);
      await load();

    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDelete(message) {
    if (!window.confirm("Delete this message?")) return;

    setError("");
    setNotice("");

    try {
      const result = await apiRequest(
        `/api/admin/messages/${message.id}`,
        { method: "DELETE" }
      );
      setNotice(result.message);
      await load();

    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <>
      <h2 className="admin-heading">Contact Messages</h2>

      {notice && <p className="form-success">{notice}</p>}
      {error && <p className="form-error">{error}</p>}

      {messages.length === 0 ? (
        <p className="empty-message">No messages yet.</p>
      ) : (
        <div className="message-list">
          {messages.map((message) => (
            <article
              className="message-card"
              key={message.id}
            >
              <div className="message-head">
                <div>
                  <strong>{message.subject}</strong>
                  <span>
                    {message.full_name} · {message.email}
                  </span>
                </div>

                <span
                  className={
                    message.status === "new"
                      ? "badge warning"
                      : "badge"
                  }
                >
                  {message.status}
                </span>
              </div>

              <p>{message.message}</p>

              <div className="message-foot">
                <small>
                  {formatDate(message.created_at)}
                </small>

                <div className="table-actions">
                  <button
                    type="button"
                    onClick={() =>
                      setStatus(
                        message,
                        message.status === "new" ? "read" : "new"
                      )
                    }
                  >
                    {message.status === "new"
                      ? "Mark as read"
                      : "Mark as unread"}
                  </button>
                  <button
                    type="button"
                    className="danger"
                    onClick={() => handleDelete(message)}
                  >
                    Delete
                  </button>
                </div>
              </div>
            </article>
          ))}
        </div>
      )}
    </>
  );
}

// =====================================
// REPORT
// =====================================

function ReportView() {

  const [report, setReport] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    apiRequest("/api/admin/reports/categories")
      .then(setReport)
      .catch((err) => setError(err.message));
  }, []);

  if (error) {
    return <p className="form-error">{error}</p>;
  }

  if (!report) {
    return <p className="loading-message">Loading report...</p>;
  }

  return (
    <>
      <div className="report-heading">
        <h2 className="admin-heading">
          Books by Category
        </h2>
        <button
          type="button"
          className="admin-button"
          onClick={() => window.print()}
        >
          Print Report
        </button>
      </div>

      <div className="table-wrap">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Category</th>
              <th>Downloads</th>
              <th>Books</th>
              <th>Videos</th>
              <th>Total</th>
              <th>Downloadable</th>
            </tr>
          </thead>
          <tbody>
            {report.rows.map((row) => (
              <tr key={row.id}>
                <td>{row.name}</td>
                <td>
                  {row.allow_download ? "Allowed" : "Blocked"}
                </td>
                <td>{row.books}</td>
                <td>{row.videos}</td>
                <td>{row.resources}</td>
                <td>{row.downloadable}</td>
              </tr>
            ))}
            <tr className="total-row">
              <td><strong>Total</strong></td>
              <td>—</td>
              <td><strong>{report.totals.books}</strong></td>
              <td><strong>{report.totals.videos}</strong></td>
              <td><strong>{report.totals.resources}</strong></td>
              <td><strong>{report.totals.downloadable}</strong></td>
            </tr>
          </tbody>
        </table>
      </div>
    </>
  );
}

// =====================================
// USERS
// =====================================

function UsersManager() {

  const [users, setUsers] = useState([]);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const [resetTarget, setResetTarget] = useState(null);
  const [resetPassword, setResetPassword] = useState("");

  async function load() {
    const result = await apiRequest("/api/admin/users");
    setUsers(result.users || []);
  }

  useEffect(() => {
    load().catch((err) => setError(err.message));
  }, []);

  async function toggleActive(user) {
    setError("");
    setNotice("");

    try {
      const result = await apiRequest(
        `/api/admin/users/${user.id}`,
        {
          method: "PATCH",
          body: JSON.stringify({
            is_active: !user.is_active
          })
        }
      );
      setNotice(result.message);
      await load();

    } catch (err) {
      setError(err.message);
    }
  }

  async function handleReset(event) {
    event.preventDefault();
    setError("");
    setNotice("");

    try {
      const result = await apiRequest(
        `/api/admin/users/${resetTarget.id}/reset-password`,
        {
          method: "POST",
          body: JSON.stringify({
            new_password: resetPassword
          })
        }
      );
      setNotice(result.message);
      setResetTarget(null);
      setResetPassword("");

    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <>
      <h2 className="admin-heading">Registered Users</h2>

      {notice && <p className="form-success">{notice}</p>}
      {error && <p className="form-error">{error}</p>}

      {resetTarget && (
        <form className="admin-form" onSubmit={handleReset}>
          <h3 className="admin-subheading">
            Reset password for {resetTarget.full_name}
          </h3>

          <div className="form-grid">
            <div>
              <label>New Password</label>
              <input
                type="password"
                value={resetPassword}
                onChange={(event) =>
                  setResetPassword(event.target.value)
                }
                minLength={8}
                maxLength={128}
                required
              />
            </div>
          </div>

          <div className="button-row">
            <button type="submit" className="admin-button">
              Reset Password
            </button>
            <button
              type="button"
              className="admin-button secondary"
              onClick={() => {
                setResetTarget(null);
                setResetPassword("");
              }}
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      <div className="table-wrap">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Role</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id}>
                <td>{user.full_name}</td>
                <td>{user.email}</td>
                <td>{labelOf(user.role)}</td>
                <td>
                  <span
                    className={
                      user.is_active
                        ? "badge success"
                        : "badge warning"
                    }
                  >
                    {user.is_active ? "Active" : "Disabled"}
                  </span>
                </td>
                <td className="table-actions">
                  <button
                    type="button"
                    onClick={() => toggleActive(user)}
                  >
                    {user.is_active ? "Disable" : "Enable"}
                  </button>
                  <button
                    type="button"
                    onClick={() => setResetTarget(user)}
                  >
                    Reset password
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

// =====================================
// PROFILE
// =====================================

function ProfileManager({ onUserUpdated }) {

  const [form, setForm] = useState({
    full_name: "",
    email: ""
  });

  const [passwordForm, setPasswordForm] = useState({
    current_password: "",
    new_password: "",
    confirm_password: ""
  });

  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [passwordError, setPasswordError] = useState("");
  const [passwordNotice, setPasswordNotice] = useState("");

  useEffect(() => {
    apiRequest("/api/admin/profile")
      .then((result) =>
        setForm({
          full_name: result.user.full_name,
          email: result.user.email
        })
      )
      .catch((err) => setError(err.message));
  }, []);

  async function handleProfile(event) {
    event.preventDefault();
    setError("");
    setNotice("");

    try {
      const result = await apiRequest("/api/admin/profile", {
        method: "PUT",
        body: JSON.stringify(form)
      });

      setNotice(result.message);
      onUserUpdated(result.user);

    } catch (err) {
      setError(err.message);
    }
  }

  async function handlePassword(event) {
    event.preventDefault();
    setPasswordError("");
    setPasswordNotice("");

    if (passwordForm.new_password !== passwordForm.confirm_password) {
      setPasswordError("The new passwords do not match.");
      return;
    }

    try {
      const result = await apiRequest(
        "/api/auth/change-password",
        {
          method: "POST",
          body: JSON.stringify({
            current_password: passwordForm.current_password,
            new_password: passwordForm.new_password
          })
        }
      );

      setPasswordNotice(result.message);
      setPasswordForm({
        current_password: "",
        new_password: "",
        confirm_password: ""
      });

    } catch (err) {
      setPasswordError(err.message);
    }
  }

  return (
    <>
      <h2 className="admin-heading">Admin Profile</h2>

      {notice && <p className="form-success">{notice}</p>}
      {error && <p className="form-error">{error}</p>}

      <form className="admin-form" onSubmit={handleProfile}>
        <h3 className="admin-subheading">Profile Details</h3>

        <div className="form-grid">
          <div>
            <label>Full Name</label>
            <input
              type="text"
              value={form.full_name}
              onChange={(event) =>
                setForm({
                  ...form,
                  full_name: event.target.value
                })
              }
              required
            />
          </div>

          <div>
            <label>Email Address</label>
            <input
              type="email"
              value={form.email}
              onChange={(event) =>
                setForm({
                  ...form,
                  email: event.target.value
                })
              }
              required
            />
          </div>
        </div>

        <div className="button-row">
          <button type="submit" className="admin-button">
            Save Profile
          </button>
        </div>
      </form>

      <form className="admin-form" onSubmit={handlePassword}>
        <h3 className="admin-subheading">Change Password</h3>

        {passwordNotice && (
          <p className="form-success">{passwordNotice}</p>
        )}
        {passwordError && (
          <p className="form-error">{passwordError}</p>
        )}

        <div className="form-grid">
          <div>
            <label>Current Password</label>
            <input
              type="password"
              value={passwordForm.current_password}
              onChange={(event) =>
                setPasswordForm({
                  ...passwordForm,
                  current_password: event.target.value
                })
              }
              required
            />
          </div>

          <div>
            <label>New Password</label>
            <input
              type="password"
              value={passwordForm.new_password}
              onChange={(event) =>
                setPasswordForm({
                  ...passwordForm,
                  new_password: event.target.value
                })
              }
              minLength={8}
              maxLength={128}
              required
            />
          </div>

          <div>
            <label>Confirm New Password</label>
            <input
              type="password"
              value={passwordForm.confirm_password}
              onChange={(event) =>
                setPasswordForm({
                  ...passwordForm,
                  confirm_password: event.target.value
                })
              }
              minLength={8}
              maxLength={128}
              required
            />
          </div>
        </div>

        <div className="button-row">
          <button type="submit" className="admin-button">
            Change Password
          </button>
        </div>
      </form>
    </>
  );
}

// =====================================
// ADMIN SHELL
// =====================================

function Admin({
  currentUser,
  theme,
  onToggleTheme,
  onHome,
  onLogout,
  onUserUpdated
}) {

  const [section, setSection] = useState("dashboard");

  return (
    <div className="admin-page">

      <header className="admin-topbar">
        <div className="brand">
          <span className="brand-icon">E</span>
          <span>E-Library Admin</span>
        </div>

        <div className="admin-topbar-actions">
          <span className="admin-user">
            {currentUser.full_name}
          </span>

          <ThemeToggle theme={theme} onToggle={onToggleTheme} />

          <button
            type="button"
            className="admin-button secondary"
            onClick={onHome}
          >
            View Site
          </button>
          <button
            type="button"
            className="admin-button"
            onClick={onLogout}
          >
            Logout
          </button>
        </div>
      </header>

      <div className="admin-layout">

        <aside className="admin-sidebar">
          {SECTIONS.map((item) => (
            <button
              type="button"
              key={item.key}
              className={
                section === item.key
                  ? "admin-nav active"
                  : "admin-nav"
              }
              onClick={() => setSection(item.key)}
            >
              {item.label}
            </button>
          ))}
        </aside>

        <main className="admin-content">
          {section === "dashboard" && <Dashboard />}
          {section === "categories" && <CategoriesManager />}
          {section === "types" && <TypesManager />}
          {section === "resources" && <ResourcesManager />}
          {section === "loans" && <LoansManager />}
          {section === "messages" && <MessagesManager />}
          {section === "report" && <ReportView />}
          {section === "users" && <UsersManager />}
          {section === "profile" && (
            <ProfileManager onUserUpdated={onUserUpdated} />
          )}
        </main>

      </div>

    </div>
  );
}

export default Admin;
