import { render, screen } from '@testing-library/react';
import Card from './Card';

describe('Card Component', () => {
  test('powinien renderować swoje elementy potomne (children)', () => {

    render(
      <Card>
        <span>Testowy tekst</span>
      </Card>
    );

    const childElement = screen.getByText('Testowy tekst');

    expect(childElement).toBeInTheDocument();
  });
});