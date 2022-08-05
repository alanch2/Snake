import random
import curses
from curses import textpad
import time

# distance from edge of window to snake game border
buffer = 2

highscore = 0


def main(scr):
    global highscore

    # make cursor not visible
    curses.curs_set(0)

    # make reading blocking
    scr.timeout(-1)

    (max_y, max_x) = scr.getmaxyx()

    scr.addstr(int(max_y/2), int(max_x/2)-7, "[1] Play Snake")
    scr.addstr(int(max_y/2)+1, int(max_x/2)-7, "[2] Quit")

    score = intro(scr)

    finished = False
    while not finished:
        # make reading blocking again - intro calls play_game() which makes reading non-blocking so need to set it back
        scr.timeout(-1)

        if score > highscore:
            highscore = score

        scr.erase()
        scr.addstr(int(max_y/2)-1, int(max_x/2)-7,
                   "Highscore: " + str(highscore))
        scr.addstr(int(max_y/2), int(max_x/2)-7, "[1] Play Again")
        scr.addstr(int(max_y/2)+1, int(max_x/2)-7, "[2] Quit")

        score, finished = outro(scr)


def intro(scr):
    input = scr.getch()

    if input == 49:
        return play_game(scr)
    elif input == 50:
        scr.endwin()
    else:
        intro(scr)


def outro(scr):
    input = scr.getch()

    if input == 49:
        return play_game(scr), False
    elif input == 50:
        scr.endwin()
    else:
        outro(scr)


def play_game(snake_scr):

    # make reading non-blocking
    snake_scr.timeout(0)

    gameover = False
    grow = False
    snake_len = 3
    direction = 3

    # list to store each (y, x) node of snake
    snake = [(4, 12), (4, 11), (4, 10)]

    # stores (y, x) of current food
    food = (10, 25)

    (max_y, max_x) = snake_scr.getmaxyx()

    textpad.rectangle(snake_scr, buffer, buffer, max_y-buffer, max_x-buffer)

    draw_snake(snake_scr, snake)
    draw_food(snake_scr, food)

    while not gameover:
        key = snake_scr.getch()

        # handle key presses and movement of snake
        if key == curses.KEY_UP and direction != 2:
            if out_of_bounds(snake_scr, snake[0]):
                gameover = True
            else:
                snake = move_up(snake_scr, snake, food, grow)
                direction = 1
        elif key == curses.KEY_DOWN and direction != 1:
            if out_of_bounds(snake_scr, snake[0]):
                gameover = True
            else:
                snake = move_down(snake_scr, snake, food, grow)
                direction = 2
        elif key == curses.KEY_RIGHT and direction != 4:
            if out_of_bounds(snake_scr, snake[0]):
                gameover = True
            else:
                snake = move_right(snake_scr, snake, food, grow)
                direction = 3
        elif key == curses.KEY_LEFT and direction != 3:
            if out_of_bounds(snake_scr, snake[0]):
                gameover = True
            else:
                snake = move_left(snake_scr, snake, food, grow)
                direction = 4
        else:
            if direction == 1:
                if out_of_bounds(snake_scr, snake[0]):
                    gameover = True
                else:
                    snake = move_up(snake_scr, snake, food, grow)
            elif direction == 2:
                if out_of_bounds(snake_scr, snake[0]):
                    gameover = True
                else:
                    snake = move_down(snake_scr, snake, food, grow)
            elif direction == 3:
                if out_of_bounds(snake_scr, snake[0]):
                    gameover = True
                else:
                    snake = move_right(snake_scr, snake, food, grow)
            elif direction == 4:
                if out_of_bounds(snake_scr, snake[0]):
                    gameover = True
                else:
                    snake = move_left(snake_scr, snake, food, grow)
            else:
                snake_scr.addstr(0, 0, "nothing" + str(len(snake)))
                snake_scr.refresh()

        # if snake head is on food, set grow variable to true
        if snake[0][0] == food[0] and snake[0][1] == food[1]:
            grow = True
        else:
            grow = False

        # randomly spawns food if snake eats prev food
        if len(snake) != snake_len:
            snake_len += 1
            food = new_food(snake_scr, snake)
            draw_food(snake_scr, food)

        # if snake hits itself, end game
        if snake[0] in snake[1:]:
            gameover = True

        # interval before screen updates gets 10% shorter every time snake gets one unit longer
        time.sleep(.15*(0.9**len(snake)))

    score = snake_len
    dead_animation(snake_scr, snake)

    # End screen
    snake_scr.addstr(int(max_y/2)-7, 0, """
                ██████╗  █████╗ ███╗   ███╗███████╗     ██████╗ ██╗   ██╗███████╗██████╗
                ██╔════╝ ██╔══██╗████╗ ████║██╔════╝    ██╔═══██╗██║   ██║██╔════╝██╔══██╗
                ██║  ███╗███████║██╔████╔██║█████╗      ██║   ██║██║   ██║█████╗  ██████╔╝
                ██║   ██║██╔══██║██║╚██╔╝██║██╔══╝      ██║   ██║╚██╗ ██╔╝██╔══╝  ██╔══██╗
                ╚██████╔╝██║  ██║██║ ╚═╝ ██║███████╗    ╚██████╔╝ ╚████╔╝ ███████╗██║  ██║
                ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝     ╚═════╝   ╚═══╝  ╚══════╝╚═╝  ╚═╝
    """)
    snake_scr.addstr(int(max_y/2)+3, int(max_x/2) -
                     5, "Score: " + str(snake_len))
    snake_scr.refresh()
    time.sleep(1.5)

    return score


def draw_snake(scr, snake):
    for node in snake:
        scr.addch(node[0], node[1], curses.ACS_BOARD)


def draw_food(scr, food):
    scr.addch(food[0], food[1], curses.ACS_BOARD)


def new_food(scr, snake):
    (y, x) = scr.getmaxyx()
    food = (random.randrange(buffer, y - buffer),
            random.randrange(buffer, x - buffer))

    # make sure food is not where snake is
    if food in snake:
        food = new_food(scr, snake)

    return food


def move_up(scr, snake, food, grow):
    scr.erase()
    (max_y, max_x) = scr.getmaxyx()
    textpad.rectangle(scr, buffer, buffer, max_y-buffer, max_x-buffer)

    # move snake
    curr_head_y = snake[0][0]
    curr_head_x = snake[0][1]
    snake.insert(0, (curr_head_y - 1, curr_head_x))
    if not grow:
        snake.pop()

    draw_snake(scr, snake)
    draw_food(scr, food)

    return snake


def move_down(scr, snake, food, grow):
    scr.erase()
    (max_y, max_x) = scr.getmaxyx()
    textpad.rectangle(scr, buffer, buffer, max_y-buffer, max_x-buffer)

    # move snake
    curr_head_y = snake[0][0]
    curr_head_x = snake[0][1]
    snake.insert(0, (curr_head_y + 1, curr_head_x))
    if not grow:
        snake.pop()

    draw_snake(scr, snake)
    draw_food(scr, food)

    return snake


def move_right(scr, snake, food, grow):
    scr.erase()
    (max_y, max_x) = scr.getmaxyx()
    textpad.rectangle(scr, buffer, buffer, max_y-buffer, max_x-buffer)

    # move snake
    curr_head_y = snake[0][0]
    curr_head_x = snake[0][1]
    snake.insert(0, (curr_head_y, curr_head_x + 1))

    if not grow:
        snake.pop()

    draw_snake(scr, snake)
    draw_food(scr, food)

    return snake


def move_left(scr, snake, food, grow):
    scr.erase()
    (max_y, max_x) = scr.getmaxyx()
    textpad.rectangle(scr, buffer, buffer, max_y-buffer, max_x-buffer)

    # move snake
    curr_head_y = snake[0][0]
    curr_head_x = snake[0][1]
    snake.insert(0, (curr_head_y, curr_head_x - 1))
    if not grow:
        snake.pop()

    draw_snake(scr, snake)
    draw_food(scr, food)

    return snake


def out_of_bounds(scr, snake_head):
    (y, x) = snake_head
    (max_y, max_x) = scr.getmaxyx()

    if y <= buffer or y >= (max_y - buffer):
        return True
    elif x <= buffer or x >= (max_x - buffer):
        return True
    else:
        return False


def dead_animation(scr, snake):
    (max_y, max_x) = scr.getmaxyx()
    snake_len = len(snake)

    for i in range(1, snake_len+1):
        time.sleep(0.25)
        scr.erase()
        textpad.rectangle(scr, buffer, buffer, max_y-buffer, max_x-buffer)
        draw_snake(scr, snake[:snake_len - i])
        scr.refresh()

    time.sleep(0.5)
    scr.erase()


curses.wrapper(main)
