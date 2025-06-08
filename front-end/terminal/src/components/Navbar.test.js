import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Navbar from './Navbar';
import { useAuth } from '../contexts/AuthContext';


jest.mock('../contexts/AuthContext');
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));


global.alert = jest.fn();

const renderNavbar = () => {
  return render(
    <MemoryRouter>
      <Navbar />
    </MemoryRouter>
  );
};

describe('Navbar Component', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Gdy użytkownik nie jest zalogowany', () => {
    beforeEach(() => {
      useAuth.mockReturnValue({ user: null, logout: jest.fn() });
    });

    test('powinien renderować linki Logowanie i Rejestracja', () => {
      renderNavbar();
      expect(screen.getByRole('link', { name: /logowanie/i })).toBeInTheDocument();
      expect(screen.getByRole('link', { name: /rejestracja/i })).toBeInTheDocument();
    });

    test('nie powinien renderować linków Moje Rezerwacje, Mój Profil i przycisku Wyloguj', () => {
      renderNavbar();
      expect(screen.queryByRole('link', { name: /moje rezerwacje/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('link', { name: /mój profil/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /wyloguj/i })).not.toBeInTheDocument();
    });
  });

  describe('Gdy użytkownik jest zalogowany', () => {
    const mockLogout = jest.fn();
    beforeEach(() => {
      useAuth.mockReturnValue({
        user: { email: 'test@example.com' },
        logout: mockLogout,
      });
    });

    test('powinien renderować linki Moje Rezerwacje, Mój Profil i przycisk Wyloguj', () => {
      renderNavbar();
      expect(screen.getByRole('link', { name: /moje rezerwacje/i })).toBeInTheDocument();
      expect(screen.getByRole('link', { name: /mój profil/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /wyloguj/i })).toBeInTheDocument();
    });

    test('nie powinien renderować linków Logowanie i Rejestracja', () => {
      renderNavbar();
      expect(screen.queryByRole('link', { name: /logowanie/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('link', { name: /rejestracja/i })).not.toBeInTheDocument();
    });

    test('powinien wywołać logout, alert i nawigację po kliknięciu Wyloguj', () => {
      renderNavbar();
      const logoutButton = screen.getByRole('button', { name: /wyloguj/i });
      fireEvent.click(logoutButton);

      expect(mockLogout).toHaveBeenCalledTimes(1);
      expect(global.alert).toHaveBeenCalledWith('Pomyślnie wylogowano.');
      expect(mockNavigate).toHaveBeenCalledWith('/login');
    });
  });
});