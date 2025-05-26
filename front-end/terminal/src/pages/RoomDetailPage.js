import { useParams } from 'react-router-dom';
export default function RoomDetailPage() {
  const { id_room } = useParams();
  return <h1>Rezerwacja pokoju {id_room}</h1>;
}