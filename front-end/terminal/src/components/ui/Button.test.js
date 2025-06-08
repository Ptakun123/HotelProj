import { render, screen, fireEvent } from '@testing-library/react';
import Button from './Button';

describe('Button Component', () => {
  test('powinien renderować tekst przekazany jako children', () => {
    render(<Button>Kliknij mnie</Button>);
    expect(screen.getByText('Kliknij mnie')).toBeInTheDocument();
  });

  test('powinien wywołać funkcję onClick po kliknięciu', () => {
    const handleClick = jest.fn(); // Tworzymy mockową funkcję
    render(<Button onClick={handleClick}>Kliknij mnie</Button>);

    const buttonElement = screen.getByText('Kliknij mnie');
    fireEvent.click(buttonElement);

    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  test('powinien mieć domyślną klasę dla wariantu "primary"', () => {
    render(<Button>Przycisk Primary</Button>);
    expect(screen.getByText('Przycisk Primary')).toHaveClass('bg-primary');
  });

  test('powinien mieć klasę dla wariantu "secondary"', () => {
    render(<Button variant="secondary">Przycisk Secondary</Button>);
    expect(screen.getByText('Przycisk Secondary')).toHaveClass('bg-secondary');
  });
});