import { useParams } from 'react-router-dom';
export default function RoomDetailPage() {
  const { roomId } = useParams();
  return <h1>Rezerwacja pokoju {roomId}</h1>;
}