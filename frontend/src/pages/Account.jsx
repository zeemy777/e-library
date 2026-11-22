
import { useState } from "react";
import { apiRequest } from "../services/api";
import ThemeToggle from "../components/ThemeToggle";

function Account({
  currentUser,
  onHome,
  onShelf,
  favoriteCount = 0,
  theme,
  onToggleTheme
}) {

  // Change-password form values.
  const [form, setForm] = useState({
    current_password: "",
    new_password: "",
    confirm_password: ""
  });

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  // Update a single form field.
  function handleChange(event) {
    setForm({
      ...form,
      [event.target.name]: event.target.value
    });
  }

  // Send the password change to Flask.
  async function handleSubmit(event) {
    event.preventDefault();

    setError("");
    setSuccess("");

    // The two new passwords must match.
    if (form.new_password !== form.confirm_password) {
      setError("The new passwords do not match.");
      return;
    }

    setLoading(true);

    try {
      const result = await apiRequest(
        "/api/auth/change-password",
        {
          method: "POST",
          body: JSON.stringify({
            current_password: form.current_password,
            new_password: form.new_password
          })
        }
      );

      setSuccess(result.message);

      setForm({
        current_password: "",
        new_password: "",
        confirm_password: ""
      });

    } catch (err) {
      setError(err.message);

    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page">

      <div className="auth-card">

        <div className="account-topbar">

          <button className="auth-back" onClick={onHome}>
            ← Back to home
          </button>

          <ThemeToggle theme={theme} onToggle={onToggleTheme} />

        </div>

        <h1>My Account</h1>

        <div className="account-summary">

          <div>
            <p>
              Signed in as <strong>{currentUser.full_name}</strong>
              <br />
              {currentUser.email}
            </p>
          </div>

          <button
            type="button"
            className="secondary-button"
            onClick={onShelf}
          >
            My Shelf
            <span className="summary-count">{favoriteCount}</span>
          </button>

        </div>

        <h2 className="account-subheading">
          Change Password
        </h2>

        <form onSubmit={handleSubmit}>

          <label>Current Password</label>
          <input
            type="password"
            name="current_password"
            placeholder="Enter your current password"
            value={form.current_password}
            onChange={handleChange}
            autoComplete="current-password"
            required
          />

          <label>New Password</label>
          <input
            type="password"
            name="new_password"
            placeholder="Enter a new password"
            value={form.new_password}
            onChange={handleChange}
            autoComplete="new-password"
            minLength={8}
            maxLength={128}
            required
          />

          <label>Confirm New Password</label>
          <input
            type="password"
            name="confirm_password"
            placeholder="Repeat the new password"
            value={form.confirm_password}
            onChange={handleChange}
            autoComplete="new-password"
            minLength={8}
            maxLength={128}
            required
          />

          {error && (
            <p className="form-error">{error}</p>
          )}

          {success && (
            <p className="form-success" role="status">
              {success}
            </p>
          )}

          <button
            type="submit"
            className="auth-submit"
            disabled={loading}
          >
            {loading ? "Saving..." : "Change Password"}
          </button>

        </form>

      </div>

    </div>
  );
}

export default Account;
