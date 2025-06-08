import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import RoomDetailPage from './RoomDetailPage';
import api from '../api/api';

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

describe('RoomDetailPage', () => {
  const mockRoom = { id_room: 101, id_hotel: 1, price_per_night: 300, capacity: 2 };
  const mockHotel = { id_hotel: 1, name: 'Grand Hotel', address: { street: 'Centralna', building: '1', city: 'Gdańsk', country: 'Polska' } };
  const mockUser = { id_user: 1, first_name: 'Jan', last_name: 'Kowalski' };

  beforeEach(() => {
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
    const mockStorage = { user: JSON.stringify(mockUser) };
    const localStorageSpy = jest.spyOn(window, 'localStorage', 'get');
    localStorageSpy.mockImplementation(() => ({
      getItem: (key) => mockStorage[key] || null,
    }));

    renderComponent();
    await screen.findByText(mockHotel.name);

    fireEvent.click(screen.getByRole('button', { name: /zarezerwuj/i }));
    
    expect(await screen.findByRole('button', { name: /potwierdź rezerwację/i })).toBeInTheDocument();

    localStorageSpy.mockRestore();
  });
  
  test('powinien pomyślnie utworzyć rezerwację', async () => {
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

  test('powinien wyświetlić alert, gdy użytkownik nie jest zalogowany i klika zarezerwuj', async () => {
    window.localStorage.clear(); 
    
    renderComponent();
    await screen.findByText(mockHotel.name);

    fireEvent.click(screen.getByRole('button', { name: /zarezerwuj/i }));

    expect(global.alert).toHaveBeenCalledWith('Musisz być zalogowany, aby zarezerwować pokój.');
    expect(mockNavigate).toHaveBeenCalledWith('/login');
  });

  test('powinien obsłużyć błąd serwera podczas tworzenia rezerwacji', async () => {
    window.localStorage.setItem('user', JSON.stringify(mockUser));
    window.localStorage.setItem('token', 'poprawny-token');
    window.localStorage.setItem('search_startDate', new Date().toISOString());
    window.localStorage.setItem('search_endDate', new Date().toISOString());
    api.post.mockRejectedValue(new Error('Błąd serwera 500')); 

    renderComponent();
    await screen.findByText(mockHotel.name);
    
    fireEvent.click(screen.getByRole('button', { name: /zarezerwuj/i }));
    const confirmButton = await screen.findByRole('button', { name: /potwierdź rezerwację/i });
    fireEvent.click(confirmButton);

    await waitFor(() => {
      expect(global.alert).toHaveBeenCalledWith('Nie udało się zarezerwować pokoju.');
    });
  });

  test('powinien zamknąć modal po kliknięciu przycisku zamknięcia', async () => {
    window.localStorage.setItem('user', JSON.stringify(mockUser));
    renderComponent();
    await screen.findByText(mockHotel.name);

    fireEvent.click(screen.getByRole('button', { name: /zarezerwuj/i }));

    const closeButton = await screen.findByLabelText('Zamknij');
    expect(closeButton).toBeInTheDocument();

    fireEvent.click(closeButton);

    await waitFor(() => {
      expect(screen.queryByLabelText('Zamknij')).not.toBeInTheDocument();
    });
  });
});