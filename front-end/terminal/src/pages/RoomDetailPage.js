import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate, useLocation } from 'react-router-dom';
import PageLayout from '../components/layout/PageLayout';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import api from '../api/api';
import RoomCard from '../components/RoomCard';
import ImageGallery from 'react-image-gallery';
import 'react-image-gallery/styles/css/image-gallery.css';

export default function RoomDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();

  const [room, setRoom] = useState(null);
  const [hotel, setHotel] = useState(null);
  const [images, setImages] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  // Stany na daty pobytu:
  const [startDate, setStartDate] = useState(() => {
    if (location.state?.startDate) return new Date(location.state.startDate);
    const stored = localStorage.getItem('search_startDate');
    return stored ? new Date(stored) : null;
  });
  const [endDate, setEndDate] = useState(() => {
    if (location.state?.endDate) return new Date(location.state.endDate);
    const stored = localStorage.getItem('search_endDate');
    return stored ? new Date(stored) : null;
  });

  // Modal: typ rachunku i NIP
  const [showModal, setShowModal] = useState(false);
  const [billType, setBillType] = useState('individual');
  const [nip, setNip] = useState('');

  // Parsowanie dat z location.state
  useEffect(() => {
    if (location.state?.startDate) {
      // Jeśli przekazano Date w state, new Date(...) odtworzy obiekt Date
      setStartDate(new Date(location.state.startDate));
    }
    if (location.state?.endDate) {
      setEndDate(new Date(location.state.endDate));
    }
  }, [location.state]);

  // Fetch pokoju i hotelu plus zdjęć
  useEffect(() => {
    (async () => {
      try {
        // Pobierz szczegóły pokoju po id
        const { data: roomData } = await api.get(`/room/${id}`);
        setRoom(roomData);

        // Pobierz dane hotelu
        const { data: hotelData } = await api.get(`/hotel/${roomData.id_hotel}`);
        setHotel(hotelData);

        // Pobierz galerie zdjęć hotelu
        const { data: imgs = [] } = await api.get(`/hotel_images/${roomData.id_hotel}`);
        setImages(
          imgs.map(img => ({
            original: img.url,
            thumbnail: img.url
          }))
        );
      } catch (err) {
        console.error(err);
        setError('Nie udało się pobrać szczegółów pokoju lub hotelu.');
      } finally {
        setLoading(false);
      }
    })();
  }, [id]);

  const handleMakeReservation = async () => {
    try {
      const user = JSON.parse(localStorage.getItem('user'));
      if (!user) {
        alert('Musisz być zalogowany, aby zarezerwować pokój.');
        return;
      }
      if (billType === 'company' && (!nip || nip.length < 10)) {
        alert('Podaj poprawny NIP do faktury.');
        return;
      }
      if (!startDate || !endDate) {
        alert('Brak dat rezerwacji. Wybierz daty na stronie wyszukiwania.');
        return;
      }

      await api.post(
        '/post_reservation',
        {
          id_room: room.id_room,
          id_user: user.id_user,
          first_night: startDate.toISOString().slice(0, 10),
          last_night: endDate.toISOString().slice(0, 10),
          full_name: `${user.first_name} ${user.last_name}`,
          bill_type: billType === 'company' ? 'I' : 'R',
          nip: billType === 'company' ? nip : undefined
        },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`
          }
        }
      );

      setShowModal(false);
      navigate('/my-reservations');
    } catch (e) {
      console.error(e);
      alert('Nie udało się zarezerwować pokoju.');
    }
  };

  if (loading) {
    return (
      <PageLayout>
        <p>Ładowanie…</p>
      </PageLayout>
    );
  }

  if (error) {
    return (
      <PageLayout>
        <p className="text-red-600">{error}</p>
      </PageLayout>
    );
  }

  if (!room || !hotel) {
    return (
      <PageLayout>
        <p className="text-center py-10">Brak danych pokoju lub hotelu.</p>
      </PageLayout>
    );
  }

  const hotelAddress = `${hotel.address.street} ${hotel.address.building}, ${hotel.address.city}, ${hotel.address.country}`;
  const { geo_latitude: lat, geo_length: lng } = hotel;

  return (
    <PageLayout>
      <div className="max-w-3xl mx-auto py-10 px-2 sm:px-6 space-y-8">
        <h1 className="text-3xl font-bold text-primary mb-4">
          {hotel.name}
        </h1>

        {/* GALERIA ZDJĘĆ */}
        {images.length > 0 && (
          <Card className="p-4 bg-white/90 shadow-xl rounded-2xl border border-gray-100">
            <ImageGallery items={images} showPlayButton={false} showFullscreenButton />
          </Card>
        )}

        {/* SZCZEGÓŁY */}
        <Card className="p-6 bg-white/90 shadow-xl rounded-2xl border border-gray-100">
          <div className="space-y-3">
            <p><strong>Adres hotelu:</strong> {hotelAddress}</p>
            <p><strong>Cena za noc:</strong> {room.price_per_night} zł</p>
            <p><strong>Pojemność pokoju:</strong> {room.capacity} os.</p>
            <p><strong>Udogodnienia pokoju:</strong> {room.facilities?.join(', ') || 'Brak'}</p>
            <p><strong>Udogodnienia hotelu:</strong> {hotel.facilities?.join(', ') || 'Brak'}</p>
            <p>
              <strong>Data pobytu:</strong>{' '}
              {startDate ? startDate.toISOString().slice(0, 10) : '---'} –{' '}
              {endDate ? endDate.toISOString().slice(0, 10) : '---'}
            </p>
          </div>
        </Card>

        {/* PRZYCISK ZAREZERWUJ */}
        <div className="flex justify-center">
          <Button
            onClick={() => setShowModal(true)}
            variant="primary"
            className="w-full md:w-auto px-10 py-4 text-lg rounded-2xl shadow-lg bg-primary text-white hover:bg-primary/90 transition font-semibold"
          >
            Zarezerwuj
          </Button>
        </div>

        {/* MODAL POTWIERDZENIA REZERWACJI */}
        {showModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
            <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md relative">
              <button
                className="absolute top-2 right-4 text-2xl text-gray-400 hover:text-gray-700"
                onClick={() => setShowModal(false)}
                aria-label="Zamknij"
              >×</button>
              <h2 className="text-xl font-bold mb-4 text-primary">Potwierdź rezerwację</h2>
              <div className="space-y-3 mb-4">
                <p>
                  <strong>Data pobytu:</strong>{' '}
                  {startDate ? startDate.toISOString().slice(0, 10) : '---'} –{' '}
                  {endDate ? endDate.toISOString().slice(0, 10) : '---'}
                </p>
                <p><strong>Cena za noc:</strong> {room.price_per_night} zł</p>
              </div>
              <div className="flex items-center gap-6 mb-4">
                <label className="flex items-center gap-2">
                  <input
                    type="radio"
                    name="billType"
                    value="individual"
                    checked={billType === 'individual'}
                    onChange={() => setBillType('individual')}
                  />
                  Paragon
                </label>
                <label className="flex items-center gap-2">
                  <input
                    type="radio"
                    name="billType"
                    value="company"
                    checked={billType === 'company'}
                    onChange={() => setBillType('company')}
                  />
                  Faktura
                </label>
                {billType === 'company' && (
                  <input
                    type="text"
                    value={nip}
                    onChange={e => setNip(e.target.value)}
                    placeholder="NIP"
                    className="border border-gray-300 rounded-xl p-2 w-32 ml-2"
                    maxLength={10}
                  />
                )}
              </div>
              <Button
                onClick={handleMakeReservation}
                variant="primary"
                className="w-full px-8 py-3 text-lg rounded-xl font-semibold"
              >
                Potwierdź rezerwację
              </Button>
            </div>
          </div>
        )}

        {/* MAPA */}
        <Card className="p-6 bg-white/90 shadow-xl rounded-2xl border border-gray-100">
          <h2 className="text-xl font-semibold mb-4 text-primary">Lokalizacja hotelu</h2>
          {lat && lng ? (
            <div className="w-full h-80 rounded-xl overflow-hidden">
              <iframe
                title="Mapa hotelu"
                width="100%"
                height="100%"
                style={{ border: 0 }}
                loading="lazy"
                allowFullScreen
                src={`https://www.google.com/maps/embed/v1/place?key=AIzaSyDyo_84FCDAs5znOrrHXcZOXOkcbxietdU&q=${lat},${lng}&zoom=15`}
              />
            </div>
          ) : (
            <p>Brak danych o lokalizacji hotelu.</p>
          )}
        </Card>

        {/* LINK Z POWROTEM DO WYNIKÓW */}
        <Link to={`/search`} className="block">
          <RoomCard room={room} />
        </Link>
      </div>
    </PageLayout>
  );
}