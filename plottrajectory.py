def trajectory_point_with_resistance(x, y, vx, vy, delta_t, g, m, cf, s, rho):
    fx = -(cf * rho * vx ** 2 / 2 * s)
    fy = -(cf * rho * vy ** 2 / 2 * s)
    ax = fx / m
    ay = fy / m + -g
    x += vx * delta_t + ax * delta_t ** 2 / 2
    y += vy * delta_t + ay * delta_t ** 2 / 2
    vx += ax * delta_t
    vy += ay * delta_t
    return x, y, vx, vy


def trajectory_point_without_resistance(x, y, vx, vy, t, g):
    x += vx * t
    y += vy * t - g * t ** 2 / 2
    return x, y
