from random import choice, randint

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()

# Словарь допустимых разворотов: (нажатая клавиша, текущее направление)
# → новое направление. Запрещает разворот на 180 градусов.
KEY_TO_DIRECTION = {
    (pg.K_UP, DOWN): DOWN,
    (pg.K_DOWN, UP): UP,
    (pg.K_LEFT, RIGHT): RIGHT,
    (pg.K_RIGHT, LEFT): LEFT,
}

# Множество клавиш, которые меняют направление движения:
DIRECTION_KEYS = {key for key, _ in KEY_TO_DIRECTION}


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, body_color=None):
        """Задаёт позицию в центре поля и цвет объекта."""
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color = body_color

    def draw_cell(self, position, color):
        """Рисует одну клетку указанного цвета."""
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self):
        """Отрисовывает объект (переопределяется в наследниках)."""
        raise NotImplementedError(
            f'Метод draw не переопределён в {type(self).__name__}'
        )


class Apple(GameObject):
    """Яблоко, которое собирает змейка."""

    def __init__(self, body_color=APPLE_COLOR, occupied_cells=None):
        """Задаёт цвет яблока и стартовую позицию.

        :param occupied_cells: клетки, где яблоко появляться не должно.
        """
        super().__init__(body_color)
        self.randomize_position(occupied_cells)

    def randomize_position(self, occupied_cells=None):
        """Ставит яблоко в случайную свободную клетку поля."""
        occupied = set(occupied_cells or ())
        while True:
            position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )
            if position not in occupied:
                self.position = position
                return

    def draw(self):
        """Рисует яблоко квадратом размером в одну клетку."""
        self.draw_cell(self.position, self.body_color)


class Snake(GameObject):
    """Змейка: движение, рост, столкновения и отрисовка."""

    def __init__(self, body_color=SNAKE_COLOR):
        """Инициализирует змейку в начальном состоянии."""
        super().__init__(body_color)
        self.reset()

    def reset(self):
        """Возвращает змейку в начальное состояние."""
        self.length = 1
        self.positions = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None
        self.last = None

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def update_direction(self):
        """Применяет выбранное пользователем направление."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Сдвигает змейку на одну клетку.

        Проходит сквозь границы поля, появляясь с другой стороны.
        Если длина списка превышает self.length, удаляет хвост.
        """
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_head = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT,
        )
        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    def draw(self):
        """Рисует змейку и затирает след последнего сегмента."""
        for position in self.positions[:-1]:
            self.draw_cell(position, self.body_color)

        self.draw_cell(self.get_head_position(), self.body_color)

        if self.last:
            rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, rect)


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш, задавая новое направление."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit

        if event.type == pg.KEYDOWN and event.key in DIRECTION_KEYS:
            new_direction = KEY_TO_DIRECTION.get(
                (event.key, game_object.direction)
            )
            if new_direction:
                game_object.next_direction = new_direction


def main():
    """Запускает основной игровой цикл «Змейки»."""
    pg.init()
    snake = Snake()
    apple = Apple(occupied_cells=snake.positions)

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)
        elif snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)

        apple.draw()
        snake.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
