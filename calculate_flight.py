def trajectory_point_with_resistance(x, y, vx, vy, delta_t, g, m, cf, s, rho):
    v = (vx ** 2 + vy ** 2) ** 0.5

    fx = -vx * cf * rho * v / 2 * s
    fy = -vy * cf * rho * v / 2 * s

    ax = fx / m
    ay = fy / m + -g

    x += vx * delta_t + ax * delta_t ** 2 / 2
    y += vy * delta_t + ay * delta_t ** 2 / 2

    vx += ax * delta_t
    vy += ay * delta_t
    return x, y, vx, vy, ax, ay


def fly_height(y0, vy, ay):
    return y0 - vy ** 2 / (2 * ay)


def fly_distance(x0, y0, vx, vy, ax, ay):
    t = flight_time(y0, vy, ay)
    return x0 + vx * t + ax * t ** 2 / 2


def trajectory_point_without_resistance(x, y, vx, vy, t, g):
    x += vx * t
    y += vy * t - g * t ** 2 / 2
    return x, y


def flight_time(y0, vy, ay):
    return (-vy - (vy ** 2 - 2 * ay * y0) ** 0.5) / ay
