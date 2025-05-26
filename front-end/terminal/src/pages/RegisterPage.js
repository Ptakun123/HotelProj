import { useState, useContext } from 'react';
import { AuthContext } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom'; // ⬅️ dodaj to

export default function RegisterPage() {
  const { register } = useContext(AuthContext);
  const navigate = useNavigate(); // ⬅️ hook do przekierowania

  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password: '',
    phone_number: '',
    birth_date: ''
  });

  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false); // ⬅️ flaga powodzenia

  const handleChange = e => {
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async e => {
    e.preventDefault();
    setError(null);
    setSuccess(false);
    try {
      await register(form);
      setSuccess(true);
      setTimeout(() => navigate('/login'), 1500); // ⬅️ przekierowanie po 1.5s
    } catch (err) {
      setError(err.response?.data?.error || 'Błąd rejestracji');
    }
  };

  return (
    <div className="register-page">
      <h2>Rejestracja</h2>
      <form onSubmit={handleSubmit}>
        <input name="first_name" placeholder="Imię" value={form.first_name} onChange={handleChange} required />
        <input name="last_name" placeholder="Nazwisko" value={form.last_name} onChange={handleChange} required />
        <input type="email" name="email" placeholder="Email" value={form.email} onChange={handleChange} required />
        <input type="password" name="password" placeholder="Hasło" value={form.password} onChange={handleChange} required />
        <input name="phone_number" placeholder="Telefon" value={form.phone_number} onChange={handleChange} required />
        <input type="date" name="birth_date" placeholder="Data urodzenia" value={form.birth_date} onChange={handleChange} required />

        {error && <p className="error">{error}</p>}
        {success && <p className="success">Rejestracja zakończona! Przekierowanie...</p>}

        <button type="submit">Zarejestruj</button>
      </form>
    </div>
  );
}
