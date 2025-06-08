import { render, screen } from '@testing-library/react';
import NotFoundPage from './NotFoundPage';

describe('NotFoundPage', () => {
  test('powinien renderować nagłówek 404', () => {
    render(<NotFoundPage />);
    const headingElement = screen.getByRole('heading', {
      name: /404 — Strona nie istnieje/i,
    });
    expect(headingElement).toBeInTheDocument();
  });
});