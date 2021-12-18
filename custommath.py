def LerpNumber(p0:float, p1:float, a:float):
        a = float(min(a, 1))
        return float(p0) + ((float(p1) - float(p0)) * a)

def clamp(minimum, x, maximum):
    return max(minimum, min(x, maximum))