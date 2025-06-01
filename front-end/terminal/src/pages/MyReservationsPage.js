import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import PageLayout from '../components/layout/PageLayout';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import api from '../api/api';

export default function MyReservationsPage() {
  const [reservations, setReservations] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  // pobieranie rezerwacji użytkownika
  useEffect(() => {
    async function fetchReservations() {
      try {
        const user = JSON.parse(localStorage.getItem('user'));
        if (!user) {
          setError('Musisz być zalogowany, aby zobaczyć rezerwacje.');
          setLoading(false);
          return;
        }
        const { data } = await api.get(`/user/${user.id_user}/reservations?status=active`);
        if (Array.isArray(data.reservations)) {
          setReservations(data.reservations);
        } else if (data.message) {
          setReservations([]);
        } else {
          setError('Nie udało się pobrać listy rezerwacji');
        }
      } catch (err) {
        // Obsługa 404: brak rezerwacji
        if (err.response && err.response.status === 404) {
          setReservations([]);
        } else {
          setError('Nie udało się pobrać listy rezerwacji');
        }
      } finally {
        setLoading(false);
      }
    }
    fetchReservations();
  }, []);

  // anulowanie rezerwacji
  const cancelReservation = async id_reservation => {
    try {
      const user = JSON.parse(localStorage.getItem('user'));
      await api.post('/post_cancellation', {
        id_reservation,
        id_user: user.id_user
      });
      setReservations(reservations.filter(r => r.id_reservation !== id_reservation));
    } catch (e) {
      alert('Nie udało się anulować rezerwacji');
    }
  };

  if (loading) {
    return (
      <PageLayout>
        <p className="text-center py-10">Ładowanie…</p>
      </PageLayout>
    );
  }

  if (error) {
    return (
      <PageLayout>
        <p className="text-red-600 text-center py-10">{error}</p>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <div className="max-w-4xl mx-auto py-12 space-y-8">
        <h1 className="text-3xl font-bold text-primary text-center">Moje rezerwacje</h1>

        {reservations.length === 0 ? (
          <p className="text-center text-gray-600">Nie masz jeszcze żadnej rezerwacji.</p>
        ) : (
          reservations.map(r => (
            <Card
              key={r.id_reservation}
              className="flex flex-col md:flex-row md:items-center justify-between gap-6 p-6 bg-white/95 rounded-2xl shadow-lg"
            >
              <div className="space-y-1 flex-1">
                <h2 className="text-xl font-semibold text-primary">
                  Rezerwacja #{r.id_reservation}
                </h2>
                <p>
                  <strong>Hotel:</strong>{' '}
                  <Link to={`/room/${r.room.id_room}`} className="underline text-primary/90 hover:text-primary">
                    {r.hotel.name} – pokój {r.room.id_room}
                  </Link>
                </p>
                <p>
                  <strong>Pobyt:</strong> {r.first_night} – {r.last_night}
                </p>
                <p>
                  <strong>Cena:</strong> {typeof r.price === 'number' ? r.price.toFixed(2) : 'brak danych'} zł
                </p>
                <p>
                  <strong>Typ rachunku:</strong> {r.bill_type === 'I' ? 'Faktura' : 'Paragon'}
                  {r.bill_type === 'I' && r.nip ? ` (NIP: ${r.nip})` : ''}
                </p>
              </div>

              <div className="flex md:flex-col justify-center items-center md:justify-center md:items-end">
                <Button
                  variant="danger"
                  onClick={() => cancelReservation(r.id_reservation)}
                  className="bg-red-600 hover:bg-red-700 text-white px-6 py-2 rounded-xl font-semibold transition"
                >
                  Anuluj
                </Button>
              </div>
            </Card>
          ))
        )}
      </div>
    </PageLayout>
  );
}