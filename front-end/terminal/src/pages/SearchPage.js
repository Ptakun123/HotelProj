import React, { useState } from 'react';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import api from '../api/api';
import RoomCard from '../components/RoomCard';

export default function SearchPage() {
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);
  const [rooms, setRooms] = useState([]);
  const [error, setError] = useState(null);

  const handleSearch = async () => {
    if (!startDate || !endDate) {
      setError('Wybierz datę początku i końca pobytu');
      return;
    }
    try {
      const { data } = await api.post('/search_free_rooms', {
        first_night: startDate,
        last_night: endDate
      });
      setRooms(data.rooms);
      setError(null);
    } catch (err) {
      setError('Błąd podczas wyszukiwania pokoi');
    }
  };

  return (
    <div className="search-page">
      <h2>Wyszukaj dostępne pokoje</h2>
      {error && <p className="error">{error}</p>}
      <div className="date-picker-group">
        <DatePicker
          selected={startDate}
          onChange={date => setStartDate(date)}
          selectsStart
          startDate={startDate}
          endDate={endDate}
          placeholderText="Data rozpoczęcia"
        />
        <DatePicker
          selected={endDate}
          onChange={date => setEndDate(date)}
          selectsEnd
          startDate={startDate}
          endDate={endDate}
          minDate={startDate}
          placeholderText="Data zakończenia"
        />
        <button onClick={handleSearch} disabled={!startDate || !endDate}>
          Szukaj
        </button>
      </div>
      <div className="rooms-list">
        {rooms.length === 0
          ? <p>Brak dostępnych pokoi dla wybranych dat.</p>
          : rooms.map(room => (
              <RoomCard key={room.id} room={room} />
            ))
        }
      </div>
    </div>
  );
}