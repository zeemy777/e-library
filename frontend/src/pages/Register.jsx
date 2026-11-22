
import { useState } from "react";
import { apiRequest } from "../services/api";

function Register({ onLogin, onHome }) {

  // Store registration form information.
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    password: ""
  });

  // Manage messages and loading state.
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [registered, setRegistered] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  // Update form fields whenever the user types.
  function handleChange(event) {
    setForm({
      ...form,
      [event.target.name]: event.target.value
    });
  }

  // Submit registration information to Flask.
  async function handleSubmit(event) {
    event.preventDefault();

    setError("");
    setMessage("");
    setLoading(true);

    try {
      const result = await apiRequest(
        "/api/auth/register",
        {
          method: "POST",
          body: JSON.stringify(form)
        }
      );

      setMessage(result.message);
      setRegistered(true);

      // Clear the password from the form.
      setForm({
        full_name: "",
        email: "",
        password: ""
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

        <button className="auth-back" onClick={onHome}>
          ← Back to home
        </button>

        <h1>Create Account</h1>

        <p>Join the E-Library learning community.</p>

        <form onSubmit={handleSubmit}>

          <label>Full Name</label>
          <input
            type="text"
            name="full_name"
            placeholder="Enter your full name"
            value={form.full_name}
            onChange={handleChange}
            autoComplete="name"
            required
          />

          <label>Email Address</label>
          <input
            type="email"
            name="email"
            placeholder="Enter your email"
            value={form.email}
            onChange={handleChange}
            autoComplete="email"
            required
          />

          <label>Password</label>
          <div className="auth-password">
            <input
              type={showPassword ? "text" : "password"}
              name="password"
              placeholder="Create a password"
              value={form.password}
              onChange={handleChange}
              autoComplete="new-password"
              minLength={8}
              maxLength={128}
              required
            />
            <button
              type="button"
              className="auth-toggle"
              aria-label={showPassword ? "Hide password" : "Show password"}
              aria-pressed={showPassword}
              onClick={() => setShowPassword(prev => !prev)}
            >
              {showPassword ? "Hide" : "Show"}
            </button>
          </div>

          {error && (
            <p className="form-error">{error}</p>
          )}

          {message && (
            <p className="form-success">{message}</p>
          )}

          {!registered && (
            <button
              type="submit"
              className="auth-submit"
              disabled={loading}
            >
              {loading ? "Creating account..." : "Register"}
            </button>
          )}

          {registered && (
            <button
              type="button"
              className="auth-submit"
              onClick={onLogin}
            >
              Continue to Login
            </button>
          )}

        </form>

        {!registered && (
          <p className="auth-switch">
            Already have an account?{" "}
            <button onClick={onLogin}>Login</button>
          </p>
        )}

      </div>

    </div>
  );
}

export default Register;
