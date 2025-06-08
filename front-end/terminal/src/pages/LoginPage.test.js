import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import LoginPage from './LoginPage';
import { useAuth } from '../contexts/AuthContext';


jest.mock('../contexts/AuthContext');


const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'), 
  useNavigate: () => mockNavigate,
}));

describe('LoginPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  const renderComponent = () =>
    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    );

  test('powinien poprawnie renderować formularz logowania', () => {
    useAuth.mockReturnValue({ login: jest.fn() });
    renderComponent();

    expect(screen.getByPlaceholderText('Email')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Hasło')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /zaloguj/i })).toBeInTheDocument();
    expect(screen.getByText(/nie masz konta\?/i)).toBeInTheDocument();
  });

  test('powinien pozwolić na wpisywanie danych w pola formularza', () => {
    useAuth.mockReturnValue({ login: jest.fn() });
    renderComponent();
    
    const emailInput = screen.getByPlaceholderText('Email');
    const passwordInput = screen.getByPlaceholderText('Hasło');

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });

    expect(emailInput.value).toBe('test@example.com');
    expect(passwordInput.value).toBe('password123');
  });

  test('powinien wywołać funkcję login i nawigować po udanym logowaniu', async () => {
    const mockLogin = jest.fn().mockResolvedValue(true);
    useAuth.mockReturnValue({ login: mockLogin });

    renderComponent();

    fireEvent.change(screen.getByPlaceholderText('Email'), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByPlaceholderText('Hasło'), { target: { value: 'password123' } });
    fireEvent.click(screen.getByRole('button', { name: /zaloguj/i }));

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'password123');
    });
    
    expect(mockNavigate).toHaveBeenCalledWith('/search');
  });

  test('powinien wyświetlić błąd w przypadku nieudanego logowania', async () => {
    const mockLogin = jest.fn().mockRejectedValue(new Error('Błąd logowania'));
    useAuth.mockReturnValue({ login: mockLogin });

    renderComponent();
    
    fireEvent.click(screen.getByRole('button', { name: /zaloguj/i }));

    const errorMessage = await screen.findByText('Błąd logowania');
    expect(errorMessage).toBeInTheDocument();
    expect(mockNavigate).not.toHaveBeenCalled();
  });
});