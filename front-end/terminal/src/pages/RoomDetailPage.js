import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import PageLayout from '../components/layout/PageLayout';
import Card from '../components/ui/Card';
import api from '../api/api';
import RoomCard from '../components/RoomCard';

export default function RoomDetailPage() {
  const { id_room } = useParams();
  const [room, setRoom] = useState(null);
  const [hotel, setHotel] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const { data: roomData } = await api.get(`/room/${id_room}`);
        setRoom(roomData);
        const { data: hotelData } = await api.get(`/hotel/${roomData.id_hotel}`);
        setHotel(hotelData);
      } catch (err) {
        setError('Nie udało się pobrać szczegółów pokoju lub hotelu');
      }
    }
    fetchData();
  }, [id_room]);

  if (error) return <PageLayout><p className="text-red-600">{error}</p></PageLayout>;
  if (!room || !hotel) return <PageLayout><p>Ładowanie...</p></PageLayout>;

  const hotelAddress = `${hotel.address.street} ${hotel.address.building}, ${hotel.address.city}, ${hotel.address.country}`;
  const latitude = hotel.geo_latitude;
  const longitude = hotel.geo_length;

  return (
    <PageLayout>
      <div className="max-w-3xl mx-auto py-10 px-2 sm:px-6 space-y-8">
        <h1 className="text-3xl font-bold text-primary mb-4">{hotel.name} – Pokój {id_room}</h1>
        <Card className="p-6 bg-white/90 shadow-xl rounded-2xl border border-gray-100">
          <div className="flex flex-col md:flex-row gap-6">
            {/* Możesz dodać obsługę obrazka jeśli masz */}
            <div className="flex-1 space-y-3">
              <p><strong>Adres hotelu:</strong> {hotelAddress}</p>
              <p><strong>Cena za noc:</strong> {room.price_per_night} zł</p>
              <p><strong>Udogodnienia pokoju:</strong> {room.facilities?.join(', ') || 'Brak'}</p>
              <p><strong>Udogodnienia hotelu:</strong> {hotel.facilities?.join(', ') || 'Brak'}</p>
            </div>
          </div>
        </Card>
        <Card className="p-6 bg-white/90 shadow-xl rounded-2xl border border-gray-100">
          <h2 className="text-xl font-semibold mb-4 text-primary">Lokalizacja hotelu</h2>
          {latitude && longitude ? (
            <div className="w-full h-80 rounded-xl overflow-hidden">
              <iframe
                title="Mapa hotelu"
                width="100%"
                height="100%"
                style={{ border: 0 }}
                loading="lazy"
                allowFullScreen
                src={`https://www.google.com/maps/embed/v1/place?key=AIzaSyDyo_84FCDAs5znOrrHXcZOXOkcbxietdU&q=${latitude},${longitude}&zoom=15`}
              />
            </div>
          ) : (
            <p>Brak danych o lokalizacji hotelu.</p>
          )}
        </Card>
        <Link to={`/room/${room.id_room}`}>
          <RoomCard room={room} />
        </Link>
      </div>
    </PageLayout>
  );
}