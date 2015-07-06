# def llinregress(x,y):
#     """
#     Calculates a regression line on x,y pairs.
#
#     Usage:   llinregress(x,y)      x,y are equal-length lists of x-y coordinates
#     Returns: slope, intercept, r, two-tailed prob, sterr-of-estimate
#     """
#     TINY = 1.0e-20
#     if len(x) <> len(y):
#         raise ValueError, 'Input values not paired in linregress.  Aborting.'
#     n = len(x)
#     x = map(float,x)
#     y = map(float,y)
#     xmean = mean(x)
#     ymean = mean(y)
#     r_num = float(n*(summult(x,y)) - sum(x)*sum(y))
#     r_den = math.sqrt((n*ss(x) - square_of_sums(x))*(n*ss(y)-square_of_sums(y)))
#     r = r_num / r_den
#     z = 0.5*math.log((1.0+r+TINY)/(1.0-r+TINY))
#     df = n-2
#     t = r*math.sqrt(df/((1.0-r+TINY)*(1.0+r+TINY)))
#     prob = betai(0.5*df,0.5,df/(df+t*t))
#     slope = r_num / float(n*ss(x) - square_of_sums(x))
#     intercept = ymean - slope*xmean
#     sterrest = math.sqrt(1-r*r)*samplestdev(y)
#     return slope, intercept, r, prob, sterrest

import central

def slope ((x1, y1), (x2, y2)):
    """
    Estimates the slope between 2 points (x1,y1) and (x2,y2).
    """
    x2 = float(x2 - x1)
    y2 = float(y2 - y1)

    m = (y2/x2)
    return m

def intercept((x1, y1), (x2, y2)):
    m = slope((x1,y1),(x2,y2))
    b = y2 - (m*x2)
    return b


def slopelist(x,y):
    if len(x) != len(y):
        raise Exception('Both x and y must have the same length (got respectively %d and %d).'%(len(x),len(y)))
    n = len(x)
    r_num = float(n*(summult(x,y)) - sum(x)*sum(y))
    return r_num / float(n*ss(x) - square_of_sums(x))

def interceptlist(x,y):
    if len(x) != len(y):
        raise Exception('Both x and y must have the same length (got respectively %d and %d).'%(len(x),len(y)))

    x = map(float,x)
    y = map(float,y)
    xmean = central.lmean(x)
    ymean = central.lmean(y)


# y = mx + b
# m is slope, b is y-intercept
def compute_error_for_line_given_points(b, m, points):
    totalError = 0
    for i in range(0, len(points)):
        x = points[i][0]
        y = points[i][1]
        totalError += (y - (m * x + b)) ** 2
    return totalError / float(len(points))

def step_gradient(b_current, m_current, points, learningRate):
    b_gradient = 0
    m_gradient = 0
    N = float(len(points))
    for i in range(0, len(points)):
        x = points[i][0]
        y = points[i][1]
        b_gradient += -(2/N) * (y - ((m_current * x) + b_current))
        m_gradient += -(2/N) * x * (y - ((m_current * x) + b_current))
    new_b = b_current - (learningRate * b_gradient)
    new_m = m_current - (learningRate * m_gradient)
    return [new_b, new_m]

def gradient_descent_runner(points, starting_b, starting_m, learning_rate, num_iterations):
    b = starting_b
    m = starting_m
    for i in range(num_iterations):
        b, m = step_gradient(b, m, points, learning_rate)
    return [b, m]


if __name__ == '__main__':

    points = [(32.5, 31.7),(53.4, 68.8)]
    learning_rate = 0.0001
    initial_b = 0 # initial y-intercept guess
    initial_m = 0 # initial slope guess
    num_iterations = 500000
    print "Starting gradient descent at b = {0}, m = {1}, error = {2}".format(initial_b, initial_m, compute_error_for_line_given_points(initial_b, initial_m, points))
    print "Running..."
    [b, m] = gradient_descent_runner(points, initial_b, initial_m, learning_rate, num_iterations)
    print "After {0} iterations b(intercept) = {1}, m(slope) = {2}, error = {3}".format(num_iterations, b, m, compute_error_for_line_given_points(b, m, points))

    print "Slope:", slope((32.5,31.7),(53.4,68.8))
    print "Inter:", intercept((32.5,31.7),(53.4,68.8))

