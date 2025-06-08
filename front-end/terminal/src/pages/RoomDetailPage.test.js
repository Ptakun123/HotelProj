import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import RoomDetailPage from './RoomDetailPage';
import api from '../api/api';

// --- MOCKOWANIE ZALEŻNOŚCI ---
jest.mock('../api/api');
jest.mock('react-image-gallery', () => () => <div data-testid="image-gallery">Image Gallery</div>);
jest.mock('../components/RoomCard', () => () => <div data-testid="room-card">Mocked RoomCard</div>);

const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({ id: '101' }),
  useNavigate: () => mockNavigate,
  useLocation: () => ({ state: {} }),
}));
global.alert = jest.fn();

// --- KONIEC MOCKOWANIA ---

describe('RoomDetailPage', () => {
  const mockRoom = { id_room: 101, id_hotel: 1, price_per_night: 300, capacity: 2 };
  const mockHotel = { id_hotel: 1, name: 'Grand Hotel', address: { street: 'Centralna', building: '1', city: 'Gdańsk', country: 'Polska' } };
  const mockUser = { id_user: 1, first_name: 'Jan', last_name: 'Kowalski' };

  beforeEach(() => {
    // Czyścimy tylko mocki API i nawigacji. localStorage będzie zarządzane wewnątrz każdego testu.
    jest.clearAllMocks();
    api.get.mockImplementation(url => {
      if (url.includes('/room/')) return Promise.resolve({ data: mockRoom });
      if (url.includes('/hotel/1')) return Promise.resolve({ data: mockHotel });
      if (url.includes('/hotel_images/')) return Promise.resolve({ data: [] });
      return Promise.reject(new Error('not found'));
    });
  });

  const renderComponent = () =>
    render(
      <MemoryRouter initialEntries={['/room/101']}>
        <Routes>
          <Route path="/room/:id" element={<RoomDetailPage />} />
        </Routes>
      </MemoryRouter>
    );

  test('powinien poprawnie pobrać i wyświetlić dane', async () => {
    renderComponent();
    expect(await screen.findByText(mockHotel.name)).toBeInTheDocument();
  });

  test('powinien pokazać modal, gdy zalogowany użytkownik klika "Zarezerwuj"', async () => {
    // Prymitywny mock localStorage TYLKO dla tego testu
    const mockStorage = { user: JSON.stringify(mockUser) };
    const localStorageSpy = jest.spyOn(window, 'localStorage', 'get');
    localStorageSpy.mockImplementation(() => ({
      getItem: (key) => mockStorage[key] || null,
    }));

    renderComponent();
    await screen.findByText(mockHotel.name);

    fireEvent.click(screen.getByRole('button', { name: /zarezerwuj/i }));
    
    expect(await screen.findByRole('button', { name: /potwierdź rezerwację/i })).toBeInTheDocument();

    // Sprzątamy po szpiegu
    localStorageSpy.mockRestore();
  });
  
  test('powinien pomyślnie utworzyć rezerwację', async () => {
    // Prymitywny mock localStorage TYLKO dla tego testu
    const mockStorage = {
      user: JSON.stringify(mockUser),
      token: 'poprawny-token',
      search_startDate: new Date().toISOString(),
      search_endDate: new Date().toISOString(),
    };
    const localStorageSpy = jest.spyOn(window, 'localStorage', 'get');
    localStorageSpy.mockImplementation(() => ({
      getItem: (key) => mockStorage[key] || null,
    }));
    api.post.mockResolvedValue({});

    renderComponent();
    await screen.findByText(mockHotel.name);
    
    fireEvent.click(screen.getByRole('button', { name: /zarezerwuj/i }));
    
    const confirmButton = await screen.findByRole('button', { name: /potwierdź rezerwację/i });
    fireEvent.click(confirmButton);
    
    await waitFor(() => {
        expect(api.post).toHaveBeenCalledWith('/post_reservation', expect.any(Object));
    });

    expect(mockNavigate).toHaveBeenCalledWith('/my-reservations');

    localStorageSpy.mockRestore();
  });
});