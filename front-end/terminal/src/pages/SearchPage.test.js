import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import SearchPage from './SearchPage';
import api from '../api/api';

jest.mock('../api/api');
jest.mock('react-datepicker', () => {
  return function DummyDatePicker({ selected, onChange, placeholderText }) {
    return (
      <input
        value={selected ? selected.toISOString().slice(0, 10) : ''}
        onChange={e => onChange(new Date(e.target.value))}
        placeholder={placeholderText}
        data-testid="date-picker"
      />
    );
  };
});
const localStorageMock = (() => {
  let store = {};
  return {
    getItem: jest.fn(key => store[key] || null),
    setItem: jest.fn((key, value) => { store[key] = value.toString(); }),
  };
})();
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

describe('SearchPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    api.get.mockImplementation(url => {
      if (url.includes('room_facilities')) return Promise.resolve({ data: { room_facilities: ['Klimatyzacja'] } });
      if (url.includes('hotel_facilities')) return Promise.resolve({ data: { hotel_facilities: ['Parking'] } });
      if (url.includes('countries')) return Promise.resolve({ data: { countries: ['Polska'] } });
      if (url.includes('cities')) return Promise.resolve({ data: { cities: ['Gdańsk'] } });
      return Promise.resolve({ data: [] });
    });
  });

  const renderComponent = () => render(<MemoryRouter><SearchPage /></MemoryRouter>);

  test('powinien renderować podstawowe pola wyszukiwania po załadowaniu danych', async () => {
    renderComponent();
    expect(await screen.findByText('Gdzie jedziesz?')).toBeInTheDocument();
    expect(screen.getAllByTestId('date-picker').length).toBe(2);
    expect(screen.getByRole('button', { name: /szukaj/i })).toBeInTheDocument();
  });

  test('powinien pomyślnie wyszukać pokoje i je wyświetlić', async () => {
    const mockSearchResults = { available_rooms: [{ id_room: 1, hotel_name: 'Super Hotel', id_hotel: 10 }] };
    api.post.mockResolvedValue({ data: mockSearchResults });
    
    renderComponent();
    await screen.findByRole('button', { name: /szukaj/i });

    const datePickers = screen.getAllByTestId('date-picker');
    fireEvent.change(datePickers[0], { target: { value: '2025-12-24' } });
    fireEvent.change(datePickers[1], { target: { value: '2025-12-26' } });

    fireEvent.click(screen.getByRole('button', { name: /szukaj/i }));

    expect(await screen.findByText('Super Hotel')).toBeInTheDocument();
    expect(localStorage.setItem).toHaveBeenCalledWith('search_startDate', expect.any(String));
  });

  test('powinien obsłużyć błąd podczas pobierania opcji filtrów', async () => {
    api.get.mockRejectedValue(new Error('Network Error'));
    const consoleSpy = jest.spyOn(console, 'warn').mockImplementation(() => {});

    renderComponent();

    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalledWith('Nie udało się pobrać listy udogodnień', 'Network Error');
    });

    consoleSpy.mockRestore();
  });

  test('powinien obsłużyć błąd podczas wyszukiwania', async () => {
    api.post.mockRejectedValue({ response: { data: { error: 'Błąd po stronie serwera' } } });
    renderComponent();
    await screen.findByRole('button', { name: /szukaj/i });

    const datePickers = screen.getAllByTestId('date-picker');
    fireEvent.change(datePickers[0], { target: { value: '2025-12-24' } });
    fireEvent.change(datePickers[1], { target: { value: '2025-12-26' } });
    fireEvent.click(screen.getByRole('button', { name: /szukaj/i }));

    expect(await screen.findByText('Błąd po stronie serwera')).toBeInTheDocument();
  });

  test('powinien wyczyścić datę końcową, jeśli nowa data początkowa jest późniejsza', async () => {
    renderComponent();
    await screen.findByRole('button', { name: /szukaj/i });
    
    const datePickers = screen.getAllByTestId('date-picker');
    const startDatePicker = datePickers[0];
    const endDatePicker = datePickers[1];

    fireEvent.change(startDatePicker, { target: { value: '2025-10-10' } });
    fireEvent.change(endDatePicker, { target: { value: '2025-10-15' } });
    expect(endDatePicker.value).toBe('2025-10-15');

    fireEvent.change(startDatePicker, { target: { value: '2025-10-20' } });

    expect(endDatePicker.value).toBe('');
  });
});