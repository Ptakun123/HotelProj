import { renderHook, act } from '@testing-library/react';
import { AuthProvider, useAuth } from './AuthContext';
import api from '../api/api';

// Mockowanie modułu api
jest.mock('../api/api');

// Mockowanie localStorage
const localStorageMock = (() => {
  let store = {};
  return {
    getItem: key => store[key] || null,
    setItem: (key, value) => {
      store[key] = value.toString();
    },
    removeItem: key => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
  };
})();
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

// Wrapper do testowania hooka
const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>;

describe('AuthContext', () => {
  beforeEach(() => {
    // Czyszczenie mocków i localStorage przed każdym testem
    jest.clearAllMocks();
    window.localStorage.clear();
  });

  test('powinien poprawnie zalogować użytkownika', async () => {
    const mockUserData = { id_user: 1, name: 'Test User' };
    const mockResponse = { data: { user: mockUserData, access_token: 'fake-token' } };
    api.post.mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useAuth(), { wrapper });

    await act(async () => {
      await result.current.login('test@test.pl', 'password');
    });

    expect(api.post).toHaveBeenCalledWith('/login', { email: 'test@test.pl', password: 'password' });
    expect(result.current.user).toEqual(mockUserData);
    expect(window.localStorage.getItem('user')).toBe(JSON.stringify(mockUserData));
    expect(window.localStorage.getItem('token')).toBe('fake-token');
  });

  test('powinien zgłosić błąd, jeśli odpowiedź z logowania jest nieprawidłowa', async () => {
    const mockResponse = { data: { user: null, access_token: 'fake-token' } };
    api.post.mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useAuth(), { wrapper });

    await expect(result.current.login('test@test.pl', 'password')).rejects.toThrow(
      'Brak id_user w odpowiedzi backendu'
    );
  });

  test('powinien poprawnie zarejestrować użytkownika', async () => {
    const mockUserData = { id_user: 2, name: 'New User' };
    const mockFormData = { name: 'New User', email: 'new@test.pl' };
    const mockResponse = { data: { user: mockUserData, access_token: 'new-token' } };
    api.post.mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useAuth(), { wrapper });

    await act(async () => {
      await result.current.register(mockFormData);
    });

    expect(api.post).toHaveBeenCalledWith('/register', mockFormData, expect.any(Object));
    expect(result.current.user).toEqual(mockUserData);
    expect(window.localStorage.getItem('user')).toBe(JSON.stringify(mockUserData));
    expect(window.localStorage.getItem('token')).toBe('new-token');
  });

  test('powinien poprawnie wylogować użytkownika', async () => {
    // Najpierw symulujemy zalogowanego użytkownika
    const loggedInUser = { id_user: 1, name: 'Test User' };
    window.localStorage.setItem('user', JSON.stringify(loggedInUser));

    const { result } = renderHook(() => useAuth(), { wrapper });
    expect(result.current.user).toEqual(loggedInUser); // Sprawdzenie stanu początkowego

    act(() => {
      result.current.logout();
    });

    expect(result.current.user).toBeNull();
    expect(window.localStorage.getItem('user')).toBeNull();
  });
});