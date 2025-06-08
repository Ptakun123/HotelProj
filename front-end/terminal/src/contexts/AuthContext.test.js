import { renderHook, act } from '@testing-library/react';
import { AuthProvider } from './AuthContext';
import api from '../api/api';

jest.mock('../api/api');

describe('AuthContext', () => {


  test('powinien poprawnie zalogować użytkownika', async () => {

    const mockStorage = {};
    const mockSetItem = jest.fn((key, value) => { mockStorage[key] = value; });
    const mockGetItem = jest.fn((key) => mockStorage[key] || null);
    
    const localStorageSpy = jest.spyOn(window, 'localStorage', 'get');
    localStorageSpy.mockImplementation(() => ({
      setItem: mockSetItem,
      getItem: mockGetItem,
    }));


    const mockUserData = { id_user: 1, name: 'Test User' };
    const mockResponse = { data: { user: mockUserData, access_token: 'fake-token' } };
    api.post.mockResolvedValue(mockResponse);
    const { result } = renderHook(() => require('../contexts/AuthContext').useAuth(), {
      wrapper: ({ children }) => <AuthProvider>{children}</AuthProvider>
    });


    await act(async () => {
      await result.current.login('test@test.pl', 'password');
    });


    expect(result.current.user).toEqual(mockUserData);
    expect(mockSetItem).toHaveBeenCalledWith('user', JSON.stringify(mockUserData));
    expect(mockSetItem).toHaveBeenCalledWith('token', 'fake-token');
    expect(mockStorage['user']).toBe(JSON.stringify(mockUserData));


    localStorageSpy.mockRestore();
  });

  test('powinien poprawnie wylogować użytkownika', () => {

    const initialUser = { id_user: 1, name: 'Test User' };
    const mockStorage = {
      user: JSON.stringify(initialUser),
      token: 'fake-token-dla-logout'
    };
    const mockRemoveItem = jest.fn((key) => { delete mockStorage[key]; });
    const localStorageSpy = jest.spyOn(window, 'localStorage', 'get');
    localStorageSpy.mockImplementation(() => ({

      getItem: (key) => mockStorage[key] || null,
      removeItem: mockRemoveItem,
    }));


    const { result } = renderHook(() => require('../contexts/AuthContext').useAuth(), {
      wrapper: ({ children }) => <AuthProvider>{children}</AuthProvider>
    });

    expect(result.current.user).toEqual(initialUser);
    
    act(() => {
      result.current.logout();
    });


    expect(result.current.user).toBeNull();
    expect(mockRemoveItem).toHaveBeenCalledWith('user');
    expect(mockRemoveItem).toHaveBeenCalledWith('token');


    localStorageSpy.mockRestore();
  });

  test('powinien poprawnie wywołać API rejestracji bez logowania', async () => {

    const mockStorage = {};
    const mockSetItem = jest.fn((key, value) => { mockStorage[key] = value; });
    const localStorageSpy = jest.spyOn(window, 'localStorage', 'get');
    localStorageSpy.mockImplementation(() => ({
      setItem: mockSetItem,
      getItem: () => null,
    }));
    
    api.post.mockResolvedValue({ data: { success: true } });
    const { result } = renderHook(() => require('../contexts/AuthContext').useAuth(), {
      wrapper: ({ children }) => <AuthProvider>{children}</AuthProvider>
    });

    await act(async () => {
      await result.current.register({ name: 'New User' });
    });

    expect(api.post).toHaveBeenCalledTimes(1);
    expect(result.current.user).toBeNull();
    expect(mockSetItem).not.toHaveBeenCalled();

    localStorageSpy.mockRestore();
  });
});