import { Routes, Route } from 'react-router-dom';
import ProtectedRoute from './components/ProtectedRoute';

import LoginPage           from './pages/LoginPage';
import RegisterPage        from './pages/RegisterPage';
import SearchPage          from './pages/SearchPage';
import RoomDetailPage      from './pages/RoomDetailPage';
import MyReservationsPage  from './pages/MyReservationsPage';
import NotFoundPage        from './pages/NotFoundPage';

export default function App() {
  return (
    <Routes>
      {/* publiczne */}
      <Route path="/login"    element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      {/* dostępne dla wszystkich */}
      <Route path="/search"   element={<SearchPage />} />
      <Route path="/room/:id" element={<RoomDetailPage />} />

      {/* tylko dla zalogowanych */}
      <Route
        path="/my-reservations"
        element={
          <ProtectedRoute>
            <MyReservationsPage />
          </ProtectedRoute>
        }
      />

      {/* 404 */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}