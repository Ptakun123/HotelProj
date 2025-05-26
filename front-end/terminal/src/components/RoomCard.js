import { Link } from 'react-router-dom';

export default function RoomCard({ room }) {
  return (
    <div className="room-card">
      <h3>{room.name}</h3>
      <p>{room.description}</p>
      <p>Cena: {room.price} zł / noc</p>
      <Link to={`/room/${room.id}`}>Zobacz szczegóły</Link>
    </div>
  );
}