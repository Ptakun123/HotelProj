import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import RoomDetailPage from './RoomDetailPage';
import api from '../api/api';

// --- MOCKOWANIE ZALEŻNOŚCI ---
jest.mock('../api/api');
jest.mock('react-image-gallery', () => () => <div data-testid="image-gallery">Image Gallery</div>);
// Mockujemy RoomCard, aby uniknąć problemu zagnieżdżonych linków
jest.mock('../components/RoomCard', () => () => <div data-testid="room-card">Room Card</div>);

const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({ id: '101' }),
  useNavigate: () => mockNavigate,
  useLocation: () => ({ state: {} }),
}));
global.alert = jest.fn();

const localStorageMock = (() => {
  let store = {};
  return {
    getItem: key => store[key] || null,
    setItem: (key, value) => { store[key] = value.toString(); },
    clear: () => { store = {}; },
  };
})();
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

// --- KONIEC MOCKOWANIA ---

describe('RoomDetailPage', () => {
  const mockRoom = { id_room: 101, id_hotel: 1, price_per_night: 300, capacity: 2, facilities: ['TV'] };
  const mockHotel = { id_hotel: 1, name: 'Grand Hotel', address: { street: 'Centralna', building: '1', city: 'Gdańsk', country: 'Polska' } };
  const mockImages = [{ url: 'image.jpg' }];
  const mockUser = { id_user: 1, first_name: 'Jan', last_name: 'Kowalski' };

  beforeEach(() => {
    jest.clearAllMocks();
    window.localStorage.clear();
    api.get.mockImplementation(url => {
      if (url.includes('/room/')) return Promise.resolve({ data: mockRoom });
      if (url.includes('/hotel/1')) return Promise.resolve({ data: mockHotel });
      if (url.includes('/hotel_images/')) return Promise.resolve({ data: mockImages });
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
    window.localStorage.setItem('user', JSON.stringify(mockUser));
    renderComponent();
    await screen.findByText(mockHotel.name);

    fireEvent.click(screen.getByRole('button', { name: /zarezerwuj/i }));
    
    // Używamy `findByRole`, aby jednoznacznie znaleźć przycisk w modalu
    expect(await screen.findByRole('button', { name: /potwierdź rezerwację/i })).toBeInTheDocument();
  });
  
  test('powinien pomyślnie utworzyć rezerwację', async () => {
    window.localStorage.setItem('user', JSON.stringify(mockUser));
    window.localStorage.setItem('search_startDate', new Date().toISOString());
    window.localStorage.setItem('search_endDate', new Date().toISOString());
    api.post.mockResolvedValue({});

    renderComponent();
    await screen.findByText(mockHotel.name);
    
    fireEvent.click(screen.getByRole('button', { name: /zarezerwuj/i }));
    
    const confirmButton = await screen.findByRole('button', { name: /potwierdź rezerwację/i });
    fireEvent.click(confirmButton);
    
    await waitFor(() => {
        // Sprawdzamy, czy api.post jest wywoływane z trzema argumentami
        expect(api.post).toHaveBeenCalledWith('/post_reservation', expect.any(Object), expect.any(Object));
    });

    expect(mockNavigate).toHaveBeenCalledWith('/my-reservations');
  });

  test('powinien wyświetlić błąd, jeśli pobieranie danych pokoju lub hotelu zawiedzie', async () => {
    api.get.mockRejectedValue(new Error('API Down')); // Symulujemy globalny błąd API
    renderComponent();
    expect(await screen.findByText('Nie udało się pobrać szczegółów pokoju lub hotelu.')).toBeInTheDocument();
  });

  test('powinien wyświetlić alert, jeśli daty nie są wybrane przy próbie rezerwacji', async () => {
    window.localStorage.setItem('user', JSON.stringify(mockUser));
    // Symulujemy brak dat w localStorage
    window.localStorage.removeItem('search_startDate');
    window.localStorage.removeItem('search_endDate');

    renderComponent();
    await screen.findByText(mockHotel.name);

    fireEvent.click(screen.getByRole('button', { name: /zarezerwuj/i }));
    const confirmButton = await screen.findByRole('button', { name: /potwierdź rezerwację/i });
    fireEvent.click(confirmButton);

    expect(global.alert).toHaveBeenCalledWith('Brak dat rezerwacji. Wybierz daty na stronie wyszukiwania.');
  });

  test('powinien wyświetlić alert, jeśli NIP jest niepoprawny', async () => {
    window.localStorage.setItem('user', JSON.stringify(mockUser));
    window.localStorage.setItem('search_startDate', new Date().toISOString());
    window.localStorage.setItem('search_endDate', new Date().toISOString());
    
    renderComponent();
    await screen.findByText(mockHotel.name);
    
    fireEvent.click(screen.getByRole('button', { name: /zarezerwuj/i }));
    
    // Zmieniamy na fakturę
    const companyRadio = await screen.findByLabelText('Faktura');
    fireEvent.click(companyRadio);

    // Wpisujemy za krótki NIP
    fireEvent.change(screen.getByPlaceholderText('NIP'), { target: { value: '123' } });

    // Próbujemy potwierdzić
    fireEvent.click(screen.getByRole('button', { name: /potwierdź rezerwację/i }));

    expect(global.alert).toHaveBeenCalledWith('Podaj poprawny NIP do faktury.');
  });
});