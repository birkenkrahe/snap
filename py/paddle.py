import turtle
import random

# Create a window
win = turtle.Screen()
win.title("Turtle Paddle Ball Game")
win.bgcolor("black")
win.setup(width=800, height=600)

# Paddle
paddle = turtle.Turtle()
paddle.speed(0)
paddle.shape("square")
paddle.color("white")
paddle.shapesize(stretch_wid=1, stretch_len=5)
paddle.penup()
paddle.goto(0, -250)

# Ball
ball = turtle.Turtle()
ball.speed(1)
ball.shape("circle")
ball.color("white")
ball.penup()
ball.goto(0, 0)
ball.dx = random.choice((-2, 2))  # Ball's x velocity. Randomly choose initial direction.
ball.dy = random.choice((-2, 2))  # Ball's y velocity. Randomly choose initial direction.

# Function to move the paddle
def paddle_left():
    x = paddle.xcor()
    if x > -350:
        x -= 20
        paddle.setx(x)

def paddle_right():
    x = paddle.xcor()
    if x < 350:
        x += 20
        paddle.setx(x)

# Keyboard bindings
win.listen()
win.onkeypress(paddle_left, "Left")
win.onkeypress(paddle_right, "Right")

# Main game loop
while True:
    win.update()

    # Ball movement
    ball.setx(ball.xcor() + ball.dx)
    ball.sety(ball.ycor() + ball.dy)

    # Border checking for ball
    if ball.ycor() > 290:
        ball.sety(290)
        ball.dy *= -1  # Reverse the ball direction
    if ball.ycor() < -290:
        ball.goto(0, 0)  # Reset ball position if it hits the bottom
        ball.dy *= -1
    if ball.xcor() > 390:
        ball.setx(390)
        ball.dx *= -1
    if ball.xcor() < -390:
        ball.setx(-390)
        ball.dx *= -1

    # Paddle and ball collisions
    if (ball.dx > 0) and (350 > paddle.xcor() - 50 < ball.xcor() < paddle.xcor() + 50) and (ball.ycor() < -230):
        ball.color("blue")
        ball.dy *= -1
    elif (ball.dx < 0) and (350 > paddle.xcor() - 50 < ball.xcor() < paddle.xcor() + 50) and (ball.ycor() < -230):
        ball.color("red")
        ball.dy *= -1

