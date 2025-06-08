import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from './App';
import { AuthProvider } from './contexts/AuthContext';

test('powinien poprawnie renderować całą aplikację', () => {
  render(
    <MemoryRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </MemoryRouter>
  );

  const headingElement = screen.getByRole('heading', {
    name: /wyszukaj dostępne pokoje/i,
  });
  expect(headingElement).toBeInTheDocument();
});