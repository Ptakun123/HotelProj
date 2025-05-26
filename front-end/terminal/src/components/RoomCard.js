import { Link } from 'react-router-dom';
export default function RoomCard({ room }) {
  return (
    <div className="bg-white shadow-lg rounded-2xl p-6 space-y-2">
      <h3 className="text-lg font-semibold">{room.hotel_name} (★{room.hotel_stars})</h3>
      <p className="text-gray-600">{room.city}, {room.country}</p>
      <p className="text-gray-600">Pojemność: {room.capacity} gości</p>
      <p className="text-gray-800 font-medium">Cena za noc: {room.price_per_night} PLN</p>
      <Link to={`/room/${room.id_room}`} className="text-primary hover:underline">
        Zobacz szczegóły
      </Link>
    </div>
  );
}