import { render, screen } from '@testing-library/react';
import Card from './Card';

describe('Card Component', () => {
  test('powinien renderować swoje elementy potomne (children)', () => {
    // ARRANGE
    render(
      <Card>
        <span>Testowy tekst</span>
      </Card>
    );

    // ACT
    const childElement = screen.getByText('Testowy tekst');

    // ASSERT
    expect(childElement).toBeInTheDocument();
  });
});