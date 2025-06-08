import { render, screen, fireEvent, act } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';
import RegisterPage from './RegisterPage';

// Mockowanie hooka useNavigate, aby śledzić nawigację
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

// Używamy "sztucznych" timerów, aby kontrolować setTimeout
jest.useFakeTimers();

describe('RegisterPage', () => {
  const mockRegister = jest.fn();

  // Resetowanie mocków przed każdym testem
  beforeEach(() => {
    jest.clearAllMocks();
  });

  const renderComponent = () =>
    render(
      <MemoryRouter>
        <AuthContext.Provider value={{ register: mockRegister }}>
          <RegisterPage />
        </AuthContext.Provider>
      </MemoryRouter>
    );

  test('powinien renderować wszystkie pola formularza rejestracji', () => {
    renderComponent();
    expect(screen.getByPlaceholderText('Imię')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Nazwisko')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Email')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Hasło')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /zarejestruj/i })).toBeInTheDocument();
  });

  test('powinien pokazać sukces i nawigować po udanej rejestracji', async () => {
    // Arrange
    mockRegister.mockResolvedValue(true);
    renderComponent();
    const registerButton = screen.getByRole('button', { name: /zarejestruj/i });

    // Wypełniamy tylko jedno pole, aby formularz był "ważny" do wysłania
    fireEvent.change(screen.getByPlaceholderText('Email'), { target: { value: 'test@example.com' } });

    // Act
    fireEvent.click(registerButton);

    // Assert
    // 1. Czekamy na pojawienie się komunikatu o sukcesie.
    // `findByText` automatycznie czeka, aż element pojawi się w DOM.
    expect(await screen.findByText('Rejestracja zakończona! Przekierowanie...')).toBeInTheDocument();

    // 2. Sprawdzamy, czy funkcja `register` została wywołana.
    expect(mockRegister).toHaveBeenCalledTimes(1);

    // 3. "Przyspieszamy" czas, aby wykonać funkcję wewnątrz setTimeout.
    // Musi być opakowane w `act`, ponieważ powoduje aktualizację (nawigację).
    act(() => {
      jest.runAllTimers();
    });

    // 4. Sprawdzamy, czy nastąpiła nawigacja.
    expect(mockNavigate).toHaveBeenCalledWith('/login');
  });

  test('powinien wyświetlić błąd w przypadku nieudanej rejestracji', async () => {
    // Arrange
    const errorResponse = { response: { data: { error: 'Użytkownik o tym emailu już istnieje.' } } };
    mockRegister.mockRejectedValue(errorResponse);
    renderComponent();

    // Act
    fireEvent.click(screen.getByRole('button', { name: /zarejestruj/i }));

    // Assert
    // Czekamy na pojawienie się komunikatu o błędzie.
    const errorMessage = await screen.findByText('Użytkownik o tym emailu już istnieje.');
    expect(errorMessage).toBeInTheDocument();

    // Upewniamy się, że nie było nawigacji.
    expect(mockNavigate).not.toHaveBeenCalled();
  });

  test('powinien wyświetlić generyczny błąd, gdy API odrzuci żądanie bez szczegółów', async () => {
    // Symulujemy błąd bez konkretnej wiadomości w `response.data.error`
    mockRegister.mockRejectedValue(new Error('Network Failed'));
    renderComponent();

    fireEvent.click(screen.getByRole('button', { name: /zarejestruj/i }));

    expect(await screen.findByText('Błąd rejestracji')).toBeInTheDocument();
  });
});