def sexa_to_dec(la, la_n, lo, lo_n):
    if la == 'N':
        la = 1
    elif la == 'S':
        la = -1

    if lo == 'E':
        lo = 1
    elif lo == 'W':
        lo = -1

    la_n = (la_n[0] + la_n[1] / 60 + la_n[2] / 3600) * la

    lo_n = (lo_n[0] + lo_n[1] / 60 + lo_n[2] / 3600) * lo

    return la_n, lo_n
