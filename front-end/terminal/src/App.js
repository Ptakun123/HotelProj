import { Routes, Route, Navigate } from 'react-router-dom';

import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import SearchPage from './pages/SearchPage';
import RoomDetailPage from './pages/RoomDetailPage.js';
import MyReservationsPage from './pages/MyReservationsPage';
import NotFoundPage from './pages/NotFoundPage';

function App() {
  return (
    <div className="App">
      {/* możesz tu wstawić wspólny <Header/> z nawigacją */}
      <Routes>
        <Route path="/" element={<Navigate to="/search" replace />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="/reserve/:roomId" element={<RoomDetailPage />} />
        <Route path="/my-reservations" element={<MyReservationsPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </div>
  );
}

export default App;