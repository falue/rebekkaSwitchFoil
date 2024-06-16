import matplotlib.pyplot as plt
import random

# Define playfield: If human inside, its on
p1 = (-2000, 4000)
p2 = (2000, 4000)
p3 = (1500, 0)
p4 = (-1500, 0)
points = [p1, p2, p3, p4]

def is_point_on_edge(x, y, l1, l2):
    """
    Check if a point (x, y) is on the edge defined by points l1 and l2.
    """
    if (min(l1[0], l2[0]) <= x <= max(l1[0], l2[0]) and
            min(l1[1], l2[1]) <= y <= max(l1[1], l2[1])):
        if l1[0] != l2[0]:  # Non-vertical line
            slope = (l2[1] - l1[1]) / (l2[0] - l1[0])
            intercept = l1[1] - slope * l1[0]
            return y == slope * x + intercept
        else:  # Vertical line
            return x == l1[0]
    return False

def is_point_in_polygon(posX, posY):
    """
    Check if the point (posX, posY) is inside the polygon defined by points p1, p2, p3, p4.
    
    Args:
    posX (float): X coordinate of the point to check.
    posY (float): Y coordinate of the point to check.

    Returns:
    bool: True if the point is inside the polygon, False otherwise.
    """

    # Check if the point is on any of the polygon's edges
    for i in range(4):
        if is_point_on_edge(posX, posY, points[i], points[(i + 1) % 4]):
            return True

    # Ray-casting algorithm
    def is_inside_polygon(x, y, points):
        n = len(points)
        inside = False
        px, py = points[0]
        for i in range(1, n + 1):
            qx, qy = points[i % n]
            if y > min(py, qy):
                if y <= max(py, qy):
                    if x <= max(px, qx):
                        if py != qy:
                            x_intersect = (y - py) * (qx - px) / (qy - py) + px
                        if px == qx or x <= x_intersect:
                            inside = not inside
            px, py = qx, qy
        return inside

    return is_inside_polygon(posX, posY, points)

def plot_polygon_and_point(points, posX, posY, result):
    """
    Plots the polygon and the point, and shows if the point is inside or outside.
    """
    polygon = plt.Polygon(points, closed=True, edgecolor='k', facecolor='lightgrey')
    plt.gca().add_patch(polygon)
    plt.plot(posX, posY, 'bo' if result else 'ro')  # Red dot if inside, blue dot if outside
    plt.text(posX, posY, f' ({posX}, {posY})', fontsize=12, verticalalignment='bottom')
    plt.xlim(-4000, 4000)
    plt.ylim(-2000, 6000)
    plt.axhline(0, color='grey', linestyle='--')
    plt.axvline(0, color='grey', linestyle='--')
    plt.gca().set_aspect('equal', adjustable='box')
    plt.title(f'Point {"Inside" if result else "Outside"} the Polygon')
    plt.plot(0, 0, 'bo')  # sensor
    plt.show()


# Test cases
def run_tests():
    # Test case 1: Point inside the square
    test = is_point_in_polygon(-500, 2000)
    print(f"Test 1 (inside): Expected True, got {test}")

    # Test case 2: Point on the edge of the square
    test = is_point_in_polygon(-2000, 2000)
    print(f"Test 2 (on edge): Expected True, got {test}")

    # Test case 3: Point outside the square
    test = is_point_in_polygon(3333, 3000)
    print(f"Test 3 (outside): Expected False, got {test}")

    # Test case 4: Point exactly at a vertex
    test = is_point_in_polygon(-2000, 4000)
    print(f"Test 4 (vertex): Expected True, got {test}")

    # Test case 5: Point outside the square
    test = is_point_in_polygon(-6666, 6666)
    print(f"Test 5 (outside): Expected False, got {test}")

    # Test case 6: Point outside the square
    test = is_point_in_polygon(6666, -4)
    print(f"Test 6 (outside): Expected False, got {test}")

    while True:
        X = random.randint(-4000, 4000)
        Y = random.randint(-2000, 6000)
        result = is_point_in_polygon(X, Y)
        plot_polygon_and_point(points, X, Y, result)

if __name__ == "__main__":
    run_tests()
