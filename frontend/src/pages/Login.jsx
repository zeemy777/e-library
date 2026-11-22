
import { useState } from "react";
import { apiRequest } from "../services/api";

function Login({ onRegister, onHome, onLoggedIn }) {

  // Store login information.
  const [form, setForm] = useState({
    email: "",
    password: ""
  });

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  // Update the login fields.
  function handleChange(event) {
    setForm({
      ...form,
      [event.target.name]: event.target.value
    });
  }

  // Send login information to Flask.
  async function handleSubmit(event) {
    event.preventDefault();

    setError("");
    setLoading(true);

    try {
      const result = await apiRequest(
        "/api/auth/login",
        {
          method: "POST",
          body: JSON.stringify(form)
        }
      );

      // Pass the authenticated user to the parent.
      onLoggedIn(result.user);

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

        <h1>Welcome Back</h1>

        <p>Log in to continue exploring the E-Library.</p>

        <form onSubmit={handleSubmit}>

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
              placeholder="Enter your password"
              value={form.password}
              onChange={handleChange}
              autoComplete="current-password"
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

          <button
            type="submit"
            className="auth-submit"
            disabled={loading}
          >
            {loading ? "Logging in..." : "Login"}
          </button>

        </form>

        <p className="auth-switch">
          Don't have an account?{" "}
          <button onClick={onRegister}>Register</button>
        </p>

      </div>

    </div>
  );
}

export default Login;
