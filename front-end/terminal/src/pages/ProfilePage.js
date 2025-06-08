import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import api from '../api/api';

export default function ProfilePage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState(null);
  const [passwordEdit, setPasswordEdit] = useState(false);
  const [passwordForm, setPasswordForm] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    async function fetchUser() {
      try {
        const res = await api.get(`/user/${user.id_user}`);
        setForm(res.data);
      } catch (e) {
        setError('Nie udało się pobrać danych użytkownika.');
        setForm({}); 
      }
    }
    fetchUser();
  }, [user, navigate]);

  const handlePasswordChange = e => {
    setPasswordForm(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handlePasswordUpdate = async e => {
    e.preventDefault();
    setError('');
    setSuccess('');
    if (passwordForm.new_password !== passwordForm.confirm_password) {
      setError('Nowe hasło i potwierdzenie muszą być takie same.');
      return;
    }
    try {
      await api.put(
        `/user/${user.id_user}/password`,
        {
          current_password: passwordForm.current_password,
          new_password: passwordForm.new_password
        }
      );
      setSuccess('Hasło zostało zaktualizowane.');
      setPasswordEdit(false);
      setPasswordForm({ current_password: '', new_password: '', confirm_password: '' });
    } catch (e) {
      setError(e.response?.data?.message || 'Błąd podczas zmiany hasła.');
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Czy na pewno chcesz usunąć konto? Tej operacji nie można cofnąć!')) return;
    try {
      await api.delete(`/user/${user.id_user}`);
      logout();
      navigate('/register');
    } catch (e) {
      setError('Błąd podczas usuwania konta.');
    }
  };

  if (!form) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-lg text-gray-600">Ładowanie profilu...</div>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-xl p-8">
        <h2 className="text-2xl font-bold text-center mb-4 text-primary">
          Witaj, {form.first_name}!
        </h2>

        {error && <p className="text-red-600 text-center mb-2">{error}</p>}
        {success && <p className="text-green-600 text-center mb-2">{success}</p>}

        {!passwordEdit ? (
          <>
            <div className="space-y-2 mb-6">
              <div><span className="font-semibold">Imię:</span> {form.first_name}</div>
              <div><span className="font-semibold">Nazwisko:</span> {form.last_name}</div>
              <div><span className="font-semibold">Email:</span> {form.email}</div>
              <div><span className="font-semibold">Telefon:</span> {form.phone_number}</div>
              <div><span className="font-semibold">Data urodzenia:</span> {form.birth_date}</div>
            </div>
            <div className="flex gap-4">
              <button
                onClick={() => setPasswordEdit(true)}
                className="w-1/2 bg-primary text-white font-semibold py-3 rounded-lg hover:bg-primary/90 transition"
              >
                Zmień hasło
              </button>
              <button
                onClick={handleDelete}
                className="w-1/2 bg-red-500 text-white font-semibold py-3 rounded-lg hover:bg-red-600 transition"
              >
                Usuń konto
              </button>
            </div>
          </>
        ) : (
          <form onSubmit={handlePasswordUpdate} className="space-y-4 mt-4">
            <input
              type="password"
              name="current_password"
              placeholder="Aktualne hasło"
              value={passwordForm.current_password}
              onChange={handlePasswordChange}
              required
              className="w-full border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-primary"
            />
            <input
              type="password"
              name="new_password"
              placeholder="Nowe hasło"
              value={passwordForm.new_password}
              onChange={handlePasswordChange}
              required
              className="w-full border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-primary"
            />
            <input
              type="password"
              name="confirm_password"
              placeholder="Potwierdź nowe hasło"
              value={passwordForm.confirm_password}
              onChange={handlePasswordChange}
              required
              className="w-full border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-primary"
            />
            <div className="flex gap-4">
              <button
                type="submit"
                className="w-full bg-primary text-white font-semibold py-3 rounded-lg hover:bg-primary/90 transition"
              >
                Zapisz hasło
              </button>
              <button
                type="button"
                onClick={() => setPasswordEdit(false)}
                className="w-full bg-gray-200 text-gray-700 font-semibold py-3 rounded-lg hover:bg-gray-300 transition"
              >
                Anuluj
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
