import { render, screen, fireEvent, act } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';
import RegisterPage from './RegisterPage';

const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));


jest.useFakeTimers();

describe('RegisterPage', () => {
  const mockRegister = jest.fn();


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

    mockRegister.mockResolvedValue(true);
    renderComponent();
    const registerButton = screen.getByRole('button', { name: /zarejestruj/i });

    fireEvent.change(screen.getByPlaceholderText('Email'), { target: { value: 'test@example.com' } });

    fireEvent.click(registerButton);

    expect(await screen.findByText('Rejestracja zakończona! Przekierowanie...')).toBeInTheDocument();

    expect(mockRegister).toHaveBeenCalledTimes(1);

    act(() => {
      jest.runAllTimers();
    });


    expect(mockNavigate).toHaveBeenCalledWith('/login');
  });

  test('powinien wyświetlić błąd w przypadku nieudanej rejestracji', async () => {

    const errorResponse = { response: { data: { error: 'Użytkownik o tym emailu już istnieje.' } } };
    mockRegister.mockRejectedValue(errorResponse);
    renderComponent();

 
    fireEvent.click(screen.getByRole('button', { name: /zarejestruj/i }));


    const errorMessage = await screen.findByText('Użytkownik o tym emailu już istnieje.');
    expect(errorMessage).toBeInTheDocument();


    expect(mockNavigate).not.toHaveBeenCalled();
  });

  test('powinien wyświetlić generyczny błąd, gdy API odrzuci żądanie bez szczegółów', async () => {

    mockRegister.mockRejectedValue(new Error('Network Failed'));
    renderComponent();

    fireEvent.click(screen.getByRole('button', { name: /zarejestruj/i }));

    expect(await screen.findByText('Błąd rejestracji')).toBeInTheDocument();
  });
});