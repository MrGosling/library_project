import { render, screen } from '@testing-library/react';
import Message from '../components/Message.jsx';

test('показывает текст сообщения', () => {
  render(<Message type="error">Что-то пошло не так</Message>);
  expect(screen.getByText('Что-то пошло не так')).toBeInTheDocument();
});

test('ничего не рендерит если нет текста', () => {
  const { container } = render(<Message type="error" />);
  expect(container).toBeEmptyDOMElement();
});

test('у ошибки есть класс message--error', () => {
  render(<Message type="error">Ошибка</Message>);
  expect(screen.getByText('Ошибка')).toHaveClass('message--error');
});

test('у успеха есть класс message--success', () => {
  render(<Message type="success">Готово</Message>);
  expect(screen.getByText('Готово')).toHaveClass('message--success');
});
