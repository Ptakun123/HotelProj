import { Link } from 'react-router-dom';

export default function RoomCard({ room }) {
  if (!room || !room.id_room) {
    return (
      <div className="bg-white shadow-lg rounded-2xl p-6 space-y-2">
        <p className="text-red-600">Brak danych pokoju.</p>
      </div>
    );
  }

  return (
    <div className="bg-white shadow-lg rounded-2xl p-6 space-y-2">
      <h3 className="text-lg font-semibold">
        {room.hotel_name} {room.hotel_stars ? `(★${room.hotel_stars})` : ''}
      </h3>
      <p className="text-gray-600">
        {room.city}{room.city && room.country ? ', ' : ''}{room.country}
      </p>
      <p className="text-gray-600">
        Pojemność: {room.capacity ? room.capacity : 'brak danych'} gości
      </p>
      <p className="text-gray-800 font-medium">
        Cena za noc: {room.price_per_night ? `${room.price_per_night} PLN` : 'brak danych'}
      </p>
      <Link
        to={room.id_room ? `/room/${room.id_room}` : '#'}
        className={`text-primary hover:underline${room.id_room ? '' : ' pointer-events-none opacity-50'}`}
      >
        Zobacz szczegóły
      </Link>
    </div>
  );
}