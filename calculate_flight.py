from constants import ITERATIONS_LIMIT


def trajectory_point_with_resistance(x, y, vx, vy, delta_t, g, m, cf, s, rho):
    v = (vx ** 2 + vy ** 2) ** 0.5
    k = 0.5 * cf * rho * s

    fx = -vx * v * k
    fy = -vy * v * k

    ax = fx / m
    ay = fy / m + -g

    x += vx * delta_t + ax * delta_t ** 2 / 2
    y += vy * delta_t + ay * delta_t ** 2 / 2

    vx += ax * delta_t
    vy += ay * delta_t
    return x, y, vx, vy, ax, ay


def trajectory_with_resistance(x0, y0, vx, vy, g, m, cf, s, rho, delta_t):
    xn = [x0]
    yn = [y0]
    vxn = [vx]
    vyn = [vy]
    h = y0
    i = 1
    x, y = x0, y0
    ax, ay = 0, -g
    while (y > 0 or i == 1) and i < ITERATIONS_LIMIT:
        x, y, vx, vy, ax, ay = trajectory_point_with_resistance(
            x=x, y=y, vx=vx, vy=vy, m=m, cf=cf, s=s,
            rho=rho, g=g, delta_t=delta_t
        )
        xn += [x]
        yn += [y]
        vxn += [vx]
        vyn += [vy]
        i += 1
        if 0 < vy / -ay < delta_t:
            t = vy / -ay
            h = fly_height(y0=y, vy=vy, ay=ay)
            x_max = x + vx * t + ax * t ** 2 / 2
            xn += [x_max]
            yn += [h]
            vxn += [vx + ax * t]
            vyn += [vy + ay * t]
            i += 1
    s = fly_distance(x0=xn[i - 2], y0=yn[i - 2],
                     vx=vxn[i - 2], vy=vyn[i - 2], ax=ax, ay=ay)
    h = max(h, y)
    t = delta_t * (i - 2)
    t += flight_time(yn[i - 2], vyn[i - 2], ay)
    xn[i - 1], yn[i - 1] = s, 0
    return xn, yn, s, h, t, i


def fly_height(y0, vy, ay):
    return y0 - vy ** 2 / (2 * ay)


def fly_distance(x0, y0, vx, vy, ax, ay):
    t = flight_time(y0, vy, ay)
    return x0 + vx * t + ax * t ** 2 / 2


def trajectory_point_without_resistance(x, y, vx, vy, t, g):
    x += vx * t
    y += vy * t - g * t ** 2 / 2
    return x, y


def trajectory_without_resistance(x0, y0, vx, vy, g, delta_t):
    xn = [x0]
    yn = [y0]
    h = fly_height(y0=y0, vy=vy, ay=-g) if vy > 0 else y0
    s = fly_distance(x0=x0, y0=y0, vx=vx, vy=vy, ax=0, ay=-g)
    i = 1
    x, y = x0, y0
    while (y > 0 or i == 1) and i < ITERATIONS_LIMIT:
        x, y = trajectory_point_without_resistance(
            x=x0, y=y0, vx=vx, vy=vy, g=g, t=i * delta_t
        )
        xn += [x]
        yn += [y]
        i += 1
    xn[i - 1], yn[i - 1] = s, 0
    t = flight_time(y0, vy, -g)
    return xn, yn, s, h, t, i


def flight_time(y0, vy, ay):
    return (-vy - (vy ** 2 - 2 * ay * y0) ** 0.5) / ay
