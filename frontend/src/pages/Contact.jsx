
import { useState } from "react";
import { apiRequest } from "../services/api";

function Contact({ onHome }) {

  // Store the inquiry form values.
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    subject: "",
    message: ""
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

  // Send the inquiry to Flask.
  async function handleSubmit(event) {
    event.preventDefault();

    setError("");
    setSuccess("");
    setLoading(true);

    try {
      const result = await apiRequest("/api/contact", {
        method: "POST",
        body: JSON.stringify(form)
      });

      setSuccess(result.message);

      // Clear the form after a successful submission.
      setForm({
        full_name: "",
        email: "",
        subject: "",
        message: ""
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

        <h1>Contact Us</h1>

        <p>
          Have a question about the library, membership
          or our resources? Send us a message.
        </p>

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

          <label>Subject</label>
          <input
            type="text"
            name="subject"
            placeholder="What is your inquiry about?"
            value={form.subject}
            onChange={handleChange}
            maxLength={200}
            required
          />

          <label>Message</label>
          <textarea
            name="message"
            placeholder="Write your message here..."
            value={form.message}
            onChange={handleChange}
            rows={6}
            maxLength={5000}
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
            {loading ? "Sending..." : "Send Message"}
          </button>

        </form>

      </div>

    </div>
  );
}

export default Contact;
