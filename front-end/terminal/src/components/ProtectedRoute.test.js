import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';
import ProtectedRoute from './ProtectedRoute';

// Komponenty-zaślepki do symulacji stron
const HomePage = () => <div>Strona Główna</div>;
const LoginPage = () => <div>Strona Logowania</div>;
const ProfilePage = () => <div>Strona Profilu</div>;
const ProtectedPage = () => <div>Chroniona Strona</div>;

const TestApp = ({ user, initialPath, publicOnly = false }) => (
  <MemoryRouter initialEntries={[initialPath]}>
    <AuthContext.Provider value={{ user }}>
      <Routes>
        <Route path="/home" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route
          path="/protected"
          element={
            <ProtectedRoute publicOnly={publicOnly}>
              <ProtectedPage />
            </ProtectedRoute>
          }
        />
      </Routes>
    </AuthContext.Provider>
  </MemoryRouter>
);

describe('ProtectedRoute Component', () => {
  describe('Standardowa ochrona (publicOnly=false)', () => {
    test('powinien renderować komponent potomny, jeśli użytkownik jest zalogowany', () => {
      render(<TestApp user={{ id: 1 }} initialPath="/protected" />);
      expect(screen.getByText('Chroniona Strona')).toBeInTheDocument();
    });

    test('powinien przekierować do /login, jeśli użytkownik nie jest zalogowany', () => {
      render(<TestApp user={null} initialPath="/protected" />);
      expect(screen.getByText('Strona Logowania')).toBeInTheDocument();
      expect(screen.queryByText('Chroniona Strona')).not.toBeInTheDocument();
    });
  });

  describe('Trasa tylko publiczna (publicOnly=true)', () => {
    test('powinien renderować komponent potomny, jeśli użytkownik nie jest zalogowany', () => {
      render(<TestApp user={null} initialPath="/protected" publicOnly={true} />);
      expect(screen.getByText('Chroniona Strona')).toBeInTheDocument();
    });

    test('powinien przekierować do /profile, jeśli użytkownik jest zalogowany', () => {
      render(<TestApp user={{ id: 1 }} initialPath="/protected" publicOnly={true} />);
      expect(screen.getByText('Strona Profilu')).toBeInTheDocument();
      expect(screen.queryByText('Chroniona Strona')).not.toBeInTheDocument();
    });
  });
});