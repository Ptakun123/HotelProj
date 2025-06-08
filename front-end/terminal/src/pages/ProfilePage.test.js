import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import ProfilePage from './ProfilePage';
import { useAuth } from '../contexts/AuthContext';
import api from '../api/api';

// Mockowanie zależności
jest.mock('../contexts/AuthContext');
jest.mock('../api/api');

const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

// Mockowanie window.confirm
global.confirm = jest.fn();

describe('ProfilePage', () => {
  const mockUser = { id_user: 1, first_name: 'Jan' };
  const mockLogout = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    useAuth.mockReturnValue({ user: mockUser, logout: mockLogout });
    api.get.mockResolvedValue({ data: { id_user: 1, first_name: 'Jan', last_name: 'Kowalski', email: 'jan@test.pl' } });
  });

  const renderComponent = () =>
    render(
      <MemoryRouter>
        <ProfilePage />
      </MemoryRouter>
    );

  test('powinien pobrać i wyświetlić dane użytkownika', async () => {
    renderComponent();
    expect(await screen.findByText('Witaj, Jan!')).toBeInTheDocument();
    expect(screen.getByText('Kowalski')).toBeInTheDocument();
    expect(screen.getByText('jan@test.pl')).toBeInTheDocument();
  });

  test('powinien pokazać formularz zmiany hasła po kliknięciu przycisku', async () => {
    renderComponent();
    await screen.findByText('Witaj, Jan!');
    
    fireEvent.click(screen.getByRole('button', { name: /zmień hasło/i }));
    
    expect(screen.getByPlaceholderText('Aktualne hasło')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /zapisz hasło/i })).toBeInTheDocument();
  });

  test('powinien pomyślnie zaktualizować hasło', async () => {
    api.put.mockResolvedValue({ data: {} });
    renderComponent();
    await screen.findByText('Witaj, Jan!');
    
    fireEvent.click(screen.getByRole('button', { name: /zmień hasło/i }));
    
    fireEvent.change(screen.getByPlaceholderText('Aktualne hasło'), { target: { value: 'starehaslo' } });
    fireEvent.change(screen.getByPlaceholderText('Nowe hasło'), { target: { value: 'nowehaslo123' } });
    fireEvent.change(screen.getByPlaceholderText('Potwierdź nowe hasło'), { target: { value: 'nowehaslo123' } });
    
    fireEvent.click(screen.getByRole('button', { name: /zapisz hasło/i }));

    await waitFor(() => {
      expect(api.put).toHaveBeenCalledWith(`/user/${mockUser.id_user}/password`, expect.any(Object));
    });
    
    expect(await screen.findByText('Hasło zostało zaktualizowane.')).toBeInTheDocument();
  });

  test('powinien usunąć konto po potwierdzeniu', async () => {
    global.confirm.mockReturnValue(true); // Użytkownik klika "OK"
    api.delete.mockResolvedValue({});
    renderComponent();
    await screen.findByText('Witaj, Jan!');
    
    fireEvent.click(screen.getByRole('button', { name: /usuń konto/i }));
    
    expect(global.confirm).toHaveBeenCalledWith('Czy na pewno chcesz usunąć konto? Tej operacji nie można cofnąć!');
    await waitFor(() => {
      expect(api.delete).toHaveBeenCalledWith(`/user/${mockUser.id_user}`);
    });

    expect(mockLogout).toHaveBeenCalled();
    expect(mockNavigate).toHaveBeenCalledWith('/register');
  });

  test('powinien wyświetlić błąd, gdy pobranie danych użytkownika zawiedzie', async () => {
    api.get.mockRejectedValue(new Error('API Error'));
    renderComponent();
    expect(await screen.findByText('Nie udało się pobrać danych użytkownika.')).toBeInTheDocument();
  });

  test('powinien wyświetlić błąd, gdy hasła przy zmianie się nie zgadzają', async () => {
    renderComponent();
    await screen.findByText('Witaj, Jan!'); // Czekamy na załadowanie
    
    fireEvent.click(screen.getByRole('button', { name: /zmień hasło/i }));
    
    fireEvent.change(screen.getByPlaceholderText('Nowe hasło'), { target: { value: 'nowe1' } });
    fireEvent.change(screen.getByPlaceholderText('Potwierdź nowe hasło'), { target: { value: 'nowe2' } });
    
    fireEvent.click(screen.getByRole('button', { name: /zapisz hasło/i }));
    
    expect(await screen.findByText('Nowe hasło i potwierdzenie muszą być takie same.')).toBeInTheDocument();
    expect(api.put).not.toHaveBeenCalled();
  });

  test('powinien przekierować na stronę logowania, jeśli użytkownik nie jest zalogowany', () => {
    useAuth.mockReturnValue({ user: null }); // Symulujemy brak użytkownika
    renderComponent();
    expect(mockNavigate).toHaveBeenCalledWith('/login');
  });

  test('powinien obsłużyć błąd podczas usuwania konta', async () => {
    global.confirm.mockReturnValue(true);
    api.delete.mockRejectedValue(new Error('Server error')); // Symulujemy błąd API
    renderComponent();
    
    await screen.findByText('Witaj, Jan!');
    fireEvent.click(screen.getByRole('button', { name: /usuń konto/i }));

    expect(await screen.findByText('Błąd podczas usuwania konta.')).toBeInTheDocument();
  });

  test('powinien obsłużyć błąd podczas zmiany hasła', async () => {
    api.put.mockRejectedValue(new Error('Server error')); // Symulujemy błąd API
    renderComponent();
    await screen.findByText('Witaj, Jan!');
    
    fireEvent.click(screen.getByRole('button', { name: /zmień hasło/i }));
    fireEvent.change(screen.getByPlaceholderText('Nowe hasło'), { target: { value: 'password' } });
    fireEvent.change(screen.getByPlaceholderText('Potwierdź nowe hasło'), { target: { value: 'password' } });
    fireEvent.click(screen.getByRole('button', { name: /zapisz hasło/i }));

    expect(await screen.findByText('Błąd podczas zmiany hasła.')).toBeInTheDocument();
  });
});