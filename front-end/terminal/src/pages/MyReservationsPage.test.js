import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import MyReservationsPage from './MyReservationsPage';
import api from '../api/api';


jest.mock('../api/api');

jest.mock('../components/ui/Button', () => (props) => <button {...props}>{props.children}</button>);

const localStorageMock = (() => {
  let store = {};
  return {
    getItem: key => store[key] || null,
    setItem: (key, value) => { store[key] = value.toString(); },
    removeItem: key => { delete store[key]; },
    clear: () => { store = {}; },
  };
})();
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

describe('MyReservationsPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    window.localStorage.clear();
  });

  const mockReservations = [
    { id_reservation: 1, hotel: { name: 'Hotel 1' }, room: { id_room: 101 }, first_night: '2025-10-10', last_night: '2025-10-12', price: 500, bill_type: 'R' },
    { id_reservation: 2, hotel: { name: 'Hotel 2' }, room: { id_room: 102 }, first_night: '2025-11-11', last_night: '2025-11-13', price: 700, bill_type: 'I', nip: '1234567890' },
  ];

  const renderComponent = () =>
    render(
      <MemoryRouter>
        <MyReservationsPage />
      </MemoryRouter>
    );

  test('powinien wyświetlić błąd, gdy użytkownik nie jest zalogowany', async () => {
    renderComponent();
    expect(await screen.findByText('Musisz być zalogowany, aby zobaczyć rezerwacje.')).toBeInTheDocument();
  });

  test('powinien pobrać i wyświetlić rezerwacje dla zalogowanego użytkownika', async () => {
    window.localStorage.setItem('user', JSON.stringify({ id_user: 1 }));
    api.get.mockResolvedValue({ data: { reservations: mockReservations } });
    
    renderComponent();
    
    expect(await screen.findByText('Rezerwacja #1')).toBeInTheDocument();
    expect(screen.getByText('Rezerwacja #2')).toBeInTheDocument();
    expect(screen.getByText(/Hotel 1 – pokój 101/)).toBeInTheDocument();
  });

  test('powinien wyświetlić informację o braku rezerwacji', async () => {
    window.localStorage.setItem('user', JSON.stringify({ id_user: 1 }));
    api.get.mockResolvedValue({ data: { reservations: [] } });
    
    renderComponent();
    
    expect(await screen.findByText('Nie masz jeszcze żadnej rezerwacji.')).toBeInTheDocument();
  });
  
  test('powinien pozwolić na anulowanie rezerwacji', async () => {

    window.localStorage.setItem('user', JSON.stringify({ id_user: 1 }));
    api.get.mockResolvedValue({ data: { reservations: mockReservations } });
    api.post.mockResolvedValue({}); 

    renderComponent();

    const reservation1Text = 'Rezerwacja #1';

    expect(await screen.findByText(reservation1Text)).toBeInTheDocument();
    

    const cancelButton = screen.getAllByRole('button', { name: /anuluj/i })[0];
    

    fireEvent.click(cancelButton);
    

    await waitFor(() => {
      expect(screen.queryByText(reservation1Text)).not.toBeInTheDocument();
    });
    
    expect(api.post).toHaveBeenCalledWith('/post_cancellation', { id_reservation: 1, id_user: 1 });
    expect(screen.getByText('Rezerwacja #2')).toBeInTheDocument();
  });

   test('powinien obsłużyć błąd serwera podczas pobierania rezerwacji', async () => {
    window.localStorage.setItem('user', JSON.stringify({ id_user: 1 }));
    api.get.mockRejectedValue({ response: { status: 500 } }); 
    
    renderComponent();
    
    expect(await screen.findByText('Nie udało się pobrać listy rezerwacji')).toBeInTheDocument();
  });

  test('powinien pokazać alert, gdy anulowanie rezerwacji się nie powiedzie', async () => {
    window.localStorage.setItem('user', JSON.stringify({ id_user: 1 }));
    api.get.mockResolvedValue({ data: { reservations: mockReservations } });
    api.post.mockRejectedValue(new Error('Cancel failed')); 
    global.alert = jest.fn(); 

    renderComponent();
    
    const cancelButton = (await screen.findAllByRole('button', { name: /anuluj/i }))[0];
    fireEvent.click(cancelButton);

    await waitFor(() => {
      expect(global.alert).toHaveBeenCalledWith('Nie udało się anulować rezerwacji');
    });
  });

  test('powinien wyświetlić brak rezerwacji, gdy API zwróci pole "message"', async () => {
    window.localStorage.setItem('user', JSON.stringify({ id_user: 1 }));

    api.get.mockResolvedValue({ data: { message: 'No reservations found' } });
    
    renderComponent();
    
    expect(await screen.findByText('Nie masz jeszcze żadnej rezerwacji.')).toBeInTheDocument();
  });

  test('powinien wyświetlić błąd, gdy API zwróci nieoczekiwany format danych', async () => {
    window.localStorage.setItem('user', JSON.stringify({ id_user: 1 }));
    api.get.mockResolvedValue({ data: { some_other_field: 'value' } });
    
    renderComponent();
    
    expect(await screen.findByText('Nie udało się pobrać listy rezerwacji')).toBeInTheDocument();
  });
  
});