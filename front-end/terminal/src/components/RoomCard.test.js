import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import RoomCard from './RoomCard';

describe('RoomCard Component', () => {
  const mockRoom = {
    id_room: 101,
    hotel_name: 'Hotel Wspaniały',
    hotel_stars: 5,
    city: 'Gdańsk',
    country: 'Polska',
    capacity: 2,
    price_per_night: 450.0,
  };

  const TestWrapper = ({ children }) => <MemoryRouter>{children}</MemoryRouter>;

  test('powinien renderować wszystkie dane pokoju', () => {
    render(
      <TestWrapper>
        <RoomCard room={mockRoom} />
      </TestWrapper>
    );

    expect(screen.getByText('Hotel Wspaniały (★5)')).toBeInTheDocument();
    expect(screen.getByText('Gdańsk, Polska')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /zobacz szczegóły/i })).toHaveAttribute('href', '/room/101');
  });

  // ==========================================================
  // ===                 POPRAWIONY TEST                    ===
  // ==========================================================
  test('powinien renderować komunikat o błędzie, gdy brakuje id_room', () => {
    // Arrange: tworzymy pokój bez id_room
    const roomWithoutId = { ...mockRoom, id_room: null };
    render(
      <TestWrapper>
        <RoomCard room={roomWithoutId} />
      </TestWrapper>
    );

    // Assert: sprawdzamy, czy jest komunikat o błędzie
    expect(screen.getByText('Brak danych pokoju.')).toBeInTheDocument();
    
    // Sprawdzamy też, czy link na pewno NIE został wyrenderowany.
    // `queryBy` jest do tego idealne, bo zwraca `null` zamiast rzucać błędem.
    expect(screen.queryByText(/zobacz szczegóły/i)).not.toBeInTheDocument();
  });

  test('powinien poprawnie renderować, gdy brakuje niektórych danych (np. gwiazdek)', () => {
    const roomWithoutStars = { ...mockRoom, hotel_stars: null };
    render(
      <TestWrapper>
        <RoomCard room={roomWithoutStars} />
      </TestWrapper>
    );
    expect(screen.getByText('Hotel Wspaniały')).toBeInTheDocument();
    expect(screen.queryByText('(★5)')).not.toBeInTheDocument();
  });
});