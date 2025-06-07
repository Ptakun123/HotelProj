import React, { useState, useEffect } from 'react';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import PageLayout from '../components/layout/PageLayout';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import RoomCard from '../components/RoomCard';
import api from '../api/api';
import { FaStar } from 'react-icons/fa';
import { Link } from 'react-router-dom';

const ROOM_FACILITY_LABELS = {
  'Air Conditioning': 'Klimatyzacja',
  TV: 'TV',
  'Mini Bar': 'Mini Bar',
  Balcony: 'Balkon',
  Bathtub: 'Wanna',
  'Coffee Machine': 'Ekspres do kawy'
};

const HOTEL_FACILITY_LABELS = {
  WiFi: 'WiFi',
  Parking: 'Parking',
  'Swimming Pool': 'Basen',
  Gym: 'Siłownia',
  Restaurant: 'Restauracja',
  Spa: 'Spa',
  'Conference Room': 'Sala konferencyjna',
  'Pet-Friendly': 'Pet-Friendly',
};

const ROOM_OPTIONS = Object.entries(ROOM_FACILITY_LABELS).map(([value, label]) => ({
  label,
  value
}));

const HOTEL_OPTIONS = Object.entries(HOTEL_FACILITY_LABELS).map(([value, label]) => ({
  label,
  value
}));

export default function SearchPage() {
  const [startDate, setStartDate]           = useState(null);
  const [endDate,   setEndDate]             = useState(null);
  const [guests,    setGuests]              = useState(1);
  const [lowestPrice,  setLowestPrice]      = useState('');
  const [highestPrice, setHighestPrice]     = useState('');
  const [selectedRoomFac,  setSelectedRoomFac]   = useState([]);
  const [selectedHotelFac, setSelectedHotelFac]  = useState([]);
  const [country, setCountry]              = useState('');
  const [countryOptions, setCountryOptions] = useState([]);
  const [cityOptions, setCityOptions]       = useState([]);
  const [cities,    setCities]              = useState('');
  const [minStars,  setMinStars]            = useState(0);
  const [rooms,     setRooms]               = useState([]);
  const [error,     setError]               = useState(null);
  const [openAdvanced, setOpenAdvanced]     = useState(false);
  const [roomOptions, setRoomOptions]       = useState(ROOM_OPTIONS);
  const [hotelOptions, setHotelOptions]     = useState(HOTEL_OPTIONS);

  /* ---------- helpers ---------- */
  const toggleRoomFac  = v => setSelectedRoomFac(prev =>
    prev.includes(v) ? prev.filter(f => f !== v) : [...prev, v]
  );
  const toggleHotelFac = v => setSelectedHotelFac(prev =>
    prev.includes(v) ? prev.filter(f => f !== v) : [...prev, v]
  );

  const StarRating = ({ value, onChange, max = 5 }) => (
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

  /* ---------- search ---------- */
  const handleSearch = async () => {
    if (!startDate || !endDate)  return setError('Wybierz daty');
    if (guests <= 0)             return setError('Liczba gości musi być > 0');
    setError(null);

    // ZAPISZ DATY DO localStorage
    localStorage.setItem('search_startDate', startDate.toISOString());
    localStorage.setItem('search_endDate', endDate.toISOString());

    try {
      const payload = {
        start_date: startDate.toISOString().slice(0, 10),
        end_date:   endDate.toISOString().slice(0, 10),
        guests
      };
      if (lowestPrice)         payload.lowest_price      = +lowestPrice;
      if (highestPrice)        payload.highest_price     = +highestPrice;
      if (selectedRoomFac.length)  payload.room_facilities  = selectedRoomFac;
      if (selectedHotelFac.length) payload.hotel_facilities = selectedHotelFac;
      if (selectedHotelFac.length) payload.hotel_facilities = selectedHotelFac;
      if (country)            payload.countries         = [country];
      if (cities)              payload.city              = cities.split(',').map(c => c.trim());
      if (minStars > 0)        payload.min_hotel_stars   = minStars;

      /* --- zapytanie do backendu --- */
      const { data } = await api.post('/search_free_rooms', payload);
      const rawRooms = data.available_rooms || [];

      /* odrzucamy rekordy bez id_hotel */
      const roomsArr = rawRooms.filter(r => r.id_hotel);

      /* ---------- zdjęcia hoteli (odporne na błędy) ---------- */
      const hotelIds = [...new Set(roomsArr.map(r => r.id_hotel))];
      const imagesMap = {};

      await Promise.allSettled(
        hotelIds.map(async id => {
          try {
            const { data: imgs } = await api.get(`/hotel_images/${id}`);
            if (imgs?.length) {
              const main = imgs.find(i => i.is_main) || imgs[0];
              imagesMap[id] = main.url;
            }
          } catch (e) {
            console.warn('DEBUG: /hotel_images error', id, e.message);
          }
        })
      );

      /* ---------- finalny stan ---------- */
      const finalRooms = roomsArr.map(r => ({
        ...r,
        hotel_image: imagesMap[r.id_hotel] || null
      }));

      setRooms(finalRooms);
    } catch (err) {
      setError(err.response?.data?.error || 'Błąd wyszukiwania');
      setRooms([]);
    }
  };

  /* ---------- fetch facilities (dynamic options) ---------- */
  useEffect(() => {
    async function fetchFacilities() {
      try {
        const { data: roomFacilities } = await api.get('/room_facilities');
        const { data: hotelFacilities } = await api.get('/hotel_facilities');
        const { data: countriesResp } = await api.get('/countries');
        const { data: citiesResp } = await api.get('/cities');

        setRoomOptions(
          roomFacilities.room_facilities.map(f => ({
            label: ROOM_FACILITY_LABELS[f] || f,
            value: f
          }))
        );
        setHotelOptions(
          hotelFacilities.hotel_facilities.map(f => ({
            label: HOTEL_FACILITY_LABELS[f] || f,
            value: f
          }))
        );
        setCountryOptions(countriesResp.countries);
        setCityOptions(citiesResp.cities);
      } catch (e) {
        console.warn('Nie udało się pobrać listy udogodnień', e.message);
      }
    }
    fetchFacilities();
  }, []);
    useEffect(() => {
    async function fetchCities() {
      try {
        const url = country ? `/cities?country=${encodeURIComponent(country)}` : '/cities';
        const { data } = await api.get(url);
        setCityOptions(data.cities);
      } catch (e) {
        console.warn('Nie udało się pobrać listy miast', e.message);
      }
    }
    fetchCities();
  }, [country]);
  /* ---------- render ---------- */
  return (
    <PageLayout>
      <div className="max-w-5xl mx-auto py-10 px-2 sm:px-6 space-y-10">
        <h2 className="text-3xl font-bold text-center mb-2 text-primary">
          Wyszukaj dostępne pokoje
        </h2>
        {error && <p className="text-red-600 text-center font-semibold">{error}</p>}

        {/* ----------- PODSTAWOWE FILTRY ----------- */}
        <Card className="p-8 bg-white/90 shadow-xl rounded-2xl border border-gray-100">
          <h3 className="text-xl font-semibold mb-6 text-primary">Gdzie jedziesz?</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* data rozpoczęcia */}
            <div>
              <span className="block text-sm font-medium mb-1 text-gray-700">Data rozpoczęcia</span>
              <DatePicker
                selected={startDate}
                onChange={d => {
                  setStartDate(d);
                  if (endDate && d > endDate) setEndDate(null);
                }}
                selectsStart
                startDate={startDate}
                endDate={endDate}
                placeholderText="Wybierz datę"
                dateFormat="yyyy-MM-dd"
                className="border border-gray-300 rounded-xl p-3 w-full focus:ring-2 focus:ring-primary"
              />
            </div>
            {/* data zakończenia */}
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
            {/* goście */}
            <div>
              <span className="block text-sm font-medium mb-1 text-gray-700">Liczba gości</span>
              <input
                type="number"
                min="1"
                value={guests}
                onChange={e => setGuests(Math.max(+e.target.value || 1, 1))}
                placeholder="Liczba gości"
                className="border border-gray-300 rounded-xl p-3 w-full focus:ring-2 focus:ring-primary"
              />
            </div>
          </div>
        </Card>

        {/* ----------- ZAAWANSOWANE FILTRY ----------- */}
        <Card className="p-8 bg-white/90 shadow-xl rounded-2xl border border-gray-100">
          <button
            onClick={() => setOpenAdvanced(o => !o)}
            className="w-full flex justify-between items-center text-lg font-semibold text-primary"
          >
            Zaawansowane filtry
            <span className={`transform transition-transform ${openAdvanced ? 'rotate-180' : 'rotate-0'}`}>▼</span>
          </button>

          <div className={`overflow-hidden transition-all duration-500 ${openAdvanced ? 'max-h-[800px] mt-6' : 'max-h-0'}`}>
            <div className="space-y-8">
              {/* CENA */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <span className="block text-sm font-medium mb-1 text-gray-700">Min cena (za noc)</span>
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
                  <span className="block text-sm font-medium mb-1 text-gray-700">Max cena (za noc)</span>
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

              {/* UDOGODNIENIA POKOJU */}
              <fieldset>
                <legend className="font-medium mb-2 text-gray-800">Udogodnienia pokoi</legend>
                <div className="flex flex-wrap gap-4">
                  {roomOptions.map(opt => (
                    <label
                      key={opt.value}
                      className="inline-flex items-center space-x-2 bg-gray-100 px-3 py-2 rounded-xl shadow-sm hover:bg-primary/10 transition"
                    >
                      <input
                        type="checkbox"
                        checked={selectedRoomFac.includes(opt.value)}
                        onChange={() => toggleRoomFac(opt.value)}
                        className="form-checkbox accent-primary"
                      />
                      <span className="text-gray-700">{opt.label}</span>
                    </label>
                  ))}
                </div>
              </fieldset>

              {/* UDOGODNIENIA HOTELU */}
              <fieldset>
                <legend className="font-medium mb-2 text-gray-800">Udogodnienia hotelu</legend>
                <div className="flex flex-wrap gap-4">
                  {hotelOptions.map(opt => (
                    <label
                      key={opt.value}
                      className="inline-flex items-center space-x-2 bg-gray-100 px-3 py-2 rounded-xl shadow-sm hover:bg-primary/10 transition"
                    >
                      <input
                        type="checkbox"
                        checked={selectedHotelFac.includes(opt.value)}
                        onChange={() => toggleHotelFac(opt.value)}
                        className="form-checkbox accent-primary"
                      />
                      <span className="text-gray-700">{opt.label}</span>
                    </label>
                  ))}
                </div>
              </fieldset>

              {/* LOKALIZACJA */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <span className="block text-sm font-medium mb-1 text-gray-700">Państwo</span>
                    <input
                      type="text"
                      list="country-list"
                      value={country}
                      onChange={e => setCountry(e.target.value)}
                      placeholder="Polska"
                      className="border border-gray-300 rounded-xl p-3 w-full focus:ring-2 focus:ring-primary"
                    />
                    <datalist id="country-list">
                      {countryOptions.map(c => (
                        <option key={c} value={c} />
                      ))}
                    </datalist>
                  </div>
                <div>
                  <span className="block text-sm font-medium mb-1 text-gray-700">Miasta (oddzielone przecinkami)</span>
                  <input
                    type="text"
                    list="city-list"
                    value={cities}
                    onChange={e => setCities(e.target.value)}
                    placeholder="Warszawa, Berlin"
                    className="border border-gray-300 rounded-xl p-3 w-full focus:ring-2 focus:ring-primary"
                  />
                  <datalist id="city-list">
                    {cityOptions.map(c => (
                      <option key={c} value={c} />
                    ))}
                  </datalist>
                </div>
              </div>
                  <datalist id="city-list">
                    {cityOptions.map(c => (
                      <option key={c} value={c} />
                    ))}
                  </datalist>
              {/* GWIAZDKI */}
              <div>
                <span className="block text-sm font-medium mb-1 text-gray-700">Minimalne gwiazdki hotelu</span>
                <StarRating value={minStars} onChange={setMinStars} />
              </div>
            </div>
          </div>
        </Card>

        {/* PRZYCISK SZUKAJ */}
        <div className="flex justify-center">
          <Button
            onClick={handleSearch}
            variant="primary"
            className="px-10 py-4 text-lg rounded-2xl shadow-lg bg-primary text-white hover:bg-primary/90 transition font-semibold"
          >
            Szukaj
          </Button>
        </div>

        {/* WYNIKI */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {rooms.length > 0 ? (
            rooms.map(room => (
              <Card
                key={room.id_room}
                className="bg-white/95 rounded-2xl shadow-lg hover:shadow-2xl transition flex flex-col items-center"
              >
                {room.hotel_image && (
                  <img
                    src={room.hotel_image}
                    alt={room.hotel_name}
                    className="w-full h-48 object-cover rounded-t-2xl mb-4"
                    onError={e => { e.currentTarget.style.display = 'none'; }}
                  />
                )}
                <Link
                  to={`/room/${room.id_room}`}
                  state={{
                    startDate,
                    endDate
                  }}
                >
                  <RoomCard room={room} />
                </Link>
              </Card>
            ))
          ) : (
            <p className="text-gray-500 col-span-full text-center text-lg">
              Brak dostępnych pokoi dla wybranych kryteriów.
            </p>
          )}
        </div>
      </div>
    </PageLayout>
  );
}
