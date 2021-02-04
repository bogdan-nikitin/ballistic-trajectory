import math


def trajectory_point_with_resistance(x, y, vx, vy, delta_t, g, m, cf, s, rho):
    fx = -1 * math.copysign(1, vx) * (cf * rho * vx ** 2 / 2 * s)
    fy = -1 * math.copysign(1, vy) * (cf * rho * vy ** 2 / 2 * s)
    ax = fx / m
    ay = fy / m + -g
    x += vx * delta_t + ax * delta_t ** 2 / 2
    y += vy * delta_t + ay * delta_t ** 2 / 2
    vx += ax * delta_t
    vy += ay * delta_t
    return x, y, vx, vy


def fly_height(y0, vy, g):
    return y0 + vy ** 2 / (2 * g)


def fly_distance(x0, y0, vx, vy, g):
    t = (vy + (vy ** 2 + 2 * y0 * g) ** 0.5) / g
    return x0 + vx * t


def trajectory_point_without_resistance(x, y, vx, vy, t, g):
    x += vx * t
    y += vy * t - g * t ** 2 / 2
    return x, y
