import { render, screen } from '@testing-library/react';
import PageLayout from './PageLayout';

describe('PageLayout Component', () => {
  test('powinien renderować swoje elementy potomne (children)', () => {
    render(
      <PageLayout>
        <h1>Nagłówek strony</h1>
      </PageLayout>
    );
    expect(screen.getByRole('heading', { name: /nagłówek strony/i })).toBeInTheDocument();
  });

  test('powinien renderować stopkę z rokiem 2025', () => {
    render(<PageLayout>Test</PageLayout>);
    expect(screen.getByRole('contentinfo')).toHaveTextContent('© 2025 Hotel UAIM Rezerwacje');
  });
});