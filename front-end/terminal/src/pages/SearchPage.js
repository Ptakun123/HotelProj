import React, { useState } from 'react';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import PageLayout from '../components/layout/PageLayout';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import RoomCard from '../components/RoomCard';
import api from '../api/api';
import { FaStar } from 'react-icons/fa';

const ROOM_OPTIONS = ['Basen', 'Klimatyzacja', 'TV', 'Sejf'];
const HOTEL_OPTIONS = ['Basen', 'SPA', 'Siłownia', 'Restauracja'];

export default function SearchPage() {
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);
  const [guests, setGuests] = useState(1);
  const [lowestPrice, setLowestPrice] = useState('');
  const [highestPrice, setHighestPrice] = useState('');
  const [selectedRoomFac, setSelectedRoomFac] = useState([]);
  const [selectedHotelFac, setSelectedHotelFac] = useState([]);
  const [countries, setCountries] = useState('');
  const [cities, setCities] = useState('');
  const [minStars, setMinStars] = useState(0);
  const [maxStars, setMaxStars] = useState(5);
  const [rooms, setRooms] = useState([]);
  const [error, setError] = useState(null);
  const [openAdvanced, setOpenAdvanced] = useState(false);

  const toggleRoomFac = fac =>
    setSelectedRoomFac(prev =>
      prev.includes(fac) ? prev.filter(f => f !== fac) : [...prev, fac]
    );
  
    const toggleHotelFac = fac =>
    setSelectedHotelFac(prev =>
      prev.includes(fac) ? prev.filter(f => f !== fac) : [...prev, fac]
    );
  
  function StarRating({ value, onChange, max = 5 }) {
  return (
    <div className="flex space-x-1">
      {Array.from({ length: max }).map((_, i) => (
        <FaStar
          key={i}
          size={24}
          className={`cursor-pointer transition-colors ${i < value ? 'text-primary' : 'text-gray-300'}`}
          onClick={() => onChange(i + 1)}
        />
      ))}
    </div>
  );
}
  const handleSearch = async () => {
    if (!startDate || !endDate) return setError('Wybierz daty');
    if (guests <= 0) return setError('Liczba gości musi być > 0');
    setError(null);
    try {
      const payload = { start_date: startDate.toISOString().slice(0,10), end_date: endDate.toISOString().slice(0,10), guests };
      if (lowestPrice) payload.lowest_price = parseFloat(lowestPrice);
      if (highestPrice) payload.highest_price = parseFloat(highestPrice);
      if (selectedRoomFac.length) payload.room_facilities = selectedRoomFac;
      if (selectedHotelFac.length) payload.hotel_facilities = selectedHotelFac;
      if (countries) payload.countries = countries.split(',').map(c => c.trim());
      if (cities) payload.cities = cities.split(',').map(c => c.trim());
      payload.min_hotel_stars = minStars;
      payload.max_hotel_stars = maxStars;

      const { data } = await api.post('/search_free_rooms', payload);
      setRooms(data.available_rooms || []);
    } catch (err) {
      setError(err.response?.data?.error || 'Błąd wyszukiwania');
      setRooms([]);
    }
  };

  return (
    <PageLayout>
      <div className="max-w-5xl mx-auto py-10 px-2 sm:px-6 space-y-10">
        <h2 className="text-3xl font-bold text-center mb-2 text-primary">Wyszukaj dostępne pokoje</h2>
        {error && <p className="text-red-600 text-center font-semibold">{error}</p>}

        {/* Karta z podstawowymi filtrami */}
        <Card className="p-8 bg-white/90 shadow-xl rounded-2xl border border-gray-100">
          <h3 className="text-xl font-semibold mb-6 text-primary">Gdzie jedziesz?</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <span className="block text-sm font-medium mb-1 text-gray-700">Data rozpoczęcia</span>
              <DatePicker
                selected={startDate}
                onChange={d => { setStartDate(d); if (endDate && d > endDate) setEndDate(null); }}
                selectsStart
                startDate={startDate}
                endDate={endDate}
                placeholderText="Wybierz datę"
                dateFormat="yyyy-MM-dd"
                className="border border-gray-300 rounded-xl p-3 w-full focus:ring-2 focus:ring-primary"
              />
            </div>
            <div>
              <span className="block text-sm font-medium mb-1 text-gray-700">Data zakończenia</span>
              <DatePicker
                selected={endDate}
                onChange={setEndDate}
                selectsEnd
                startDate={startDate}
                endDate={endDate}
                minDate={startDate}
                placeholderText="Wybierz datę"
                dateFormat="yyyy-MM-dd"
                className="border border-gray-300 rounded-xl p-3 w-full focus:ring-2 focus:ring-primary"
              />
            </div>
            <div>
              <span className="block text-sm font-medium mb-1 text-gray-700">Liczba gości</span>
              <input
                type="number"
                min="1"
                value={guests}
                onChange={e => setGuests(+e.target.value || 1)}
                placeholder="Liczba gości"
                className="border border-gray-300 rounded-xl p-3 w-full focus:ring-2 focus:ring-primary"
              />
            </div>
          </div>
        </Card>

        {/* Karta z zaawansowanymi filtrami */}
        <Card className="p-8 bg-white/90 shadow-xl rounded-2xl border border-gray-100">
          <button
            onClick={() => setOpenAdvanced(o => !o)}
            className="w-full flex justify-between items-center text-lg font-semibold text-primary"
          >
            Zaawansowane filtry
            <span
              className={`transform transition-transform duration-300 ${openAdvanced ? 'rotate-180' : 'rotate-0'}`}
            >
              ▼
            </span>
          </button>

          <div
            className={`overflow-hidden transition-all duration-500 ${openAdvanced ? 'max-h-[800px] mt-6' : 'max-h-0'}`}
          >
            <div className="space-y-8">
              {/* CENA */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <span className="block text-sm font-medium mb-1 text-gray-700">Min cena (cały pobyt)</span>
                  <input
                    type="number"
                    step="0.01"
                    value={lowestPrice}
                    onChange={e => setLowestPrice(e.target.value)}
                    placeholder="Min cena"
                    className="border border-gray-300 rounded-xl p-3 w-full focus:ring-2 focus:ring-primary"
                  />
                </div>
                <div>
                  <span className="block text-sm font-medium mb-1 text-gray-700">Max cena (cały pobyt)</span>
                  <input
                    type="number"
                    step="0.01"
                    value={highestPrice}
                    onChange={e => setHighestPrice(e.target.value)}
                    placeholder="Max cena"
                    className="border border-gray-300 rounded-xl p-3 w-full focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>

              {/* UDOGODNIENIA POKOI */}
              <fieldset>
                <legend className="font-medium mb-2 text-gray-800">Udogodnienia pokoi</legend>
                <div className="flex flex-wrap gap-4">
                  {ROOM_OPTIONS.map(fac => (
                    <label
                      key={fac}
                      className="inline-flex items-center space-x-2 bg-gray-100 px-3 py-2 rounded-xl shadow-sm hover:bg-primary/10 transition"
                    >
                      <input
                        type="checkbox"
                        checked={selectedRoomFac.includes(fac)}
                        onChange={() => toggleRoomFac(fac)}
                        className="form-checkbox accent-primary"
                      />
                      <span className="text-gray-700">{fac}</span>
                    </label>
                  ))}
                </div>
              </fieldset>

              {/* UDOGODNIENIA HOTELU */}
              <fieldset>
                <legend className="font-medium mb-2 text-gray-800">Udogodnienia hotelu</legend>
                <div className="flex flex-wrap gap-4">
                  {HOTEL_OPTIONS.map(fac => (
                    <label
                      key={fac}
                      className="inline-flex items-center space-x-2 bg-gray-100 px-3 py-2 rounded-xl shadow-sm hover:bg-primary/10 transition"
                    >
                      <input
                        type="checkbox"
                        checked={selectedHotelFac.includes(fac)}
                        onChange={() => toggleHotelFac(fac)}
                        className="form-checkbox accent-primary"
                      />
                      <span className="text-gray-700">{fac}</span>
                    </label>
                  ))}
                </div>
              </fieldset>

              {/* KRAJE I MIASTA */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <span className="block text-sm font-medium mb-1 text-gray-700">Państwa (oddzielone przecinkami)</span>
                  <input
                    type="text"
                    value={countries}
                    onChange={e => setCountries(e.target.value)}
                    placeholder="Polska, Niemcy"
                    className="border border-gray-300 rounded-xl p-3 w-full focus:ring-2 focus:ring-primary"
                  />
                </div>
                <div>
                  <span className="block text-sm font-medium mb-1 text-gray-700">Miasta (oddzielone przecinkami)</span>
                  <input
                    type="text"
                    value={cities}
                    onChange={e => setCities(e.target.value)}
                    placeholder="Warszawa, Berlin"
                    className="border border-gray-300 rounded-xl p-3 w-full focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>

              {/* GWIAZDKI */}
              <div>
                <span className="block text-sm font-medium mb-1 text-gray-700">Minimalne gwiazdki hotelu</span>
                <StarRating value={minStars} onChange={setMinStars} max={5} />
              </div>
            </div>
          </div>
        </Card>


        <div className="flex justify-center">
          <Button
            onClick={handleSearch}
            variant="primary"
            className="px-10 py-4 text-lg rounded-2xl shadow-lg bg-primary text-white hover:bg-primary/90 transition font-semibold"
          >
            Szukaj
          </Button>
        </div>

        {/* Results */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {rooms.length > 0 ? (
            rooms.map(room => (
              <Card key={room.id_room} className="bg-white/95 rounded-2xl shadow-lg hover:shadow-2xl transition">
                <RoomCard room={room} />
              </Card>
            ))
          ) : (
            <p className="text-gray-500 col-span-full text-center text-lg">Brak dostępnych pokoi dla wybranych kryteriów.</p>
          )}
        </div>
      </div>
    </PageLayout>
  );
}