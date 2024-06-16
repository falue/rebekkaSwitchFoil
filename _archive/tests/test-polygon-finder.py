import matplotlib.pyplot as plt
import random
import time
import signal
import sys

# Define playfield: If human inside, its on
p1 = (-2000, 4000)
p2 = (2000, 4000)
p3 = (1500, 0)
p4 = (-1500, 0)
points = [p1, p2, p3, p4]

# Flag to control the loop
running = True

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

def plot_polygon_and_points(points, targets, any_dot_in_polygon):
    """
    Plots the polygon and multiple points, and shows if any point is inside or outside.
    """
    plt.clf()  # Clear the previous plot
    polygon = plt.Polygon(points, closed=True, edgecolor='k', facecolor='lightgrey')
    plt.gca().add_patch(polygon)
    for posX, posY, result in targets:
        plt.plot(posX, posY, 'ro' if result else 'bo')  # Red dot if inside, blue dot if outside
        plt.text(posX, posY, f' ({posX}, {posY})', fontsize=12, verticalalignment='bottom')
    plt.xlim(-4000, 4000)
    plt.ylim(-2000, 6000)
    plt.axhline(0, color='grey', linestyle='--')
    plt.axvline(0, color='grey', linestyle='--')
    plt.gca().set_aspect('equal', adjustable='box')
    plt.title(f'{"At least one person is inside" if any_dot_in_polygon else "All persons outside"} the polygon')
    plt.plot(0, 0, 'ko')  # sensor
    plt.draw()
    plt.pause(0.1)  # Pause to update the plot

def handle_close(event):
    global running
    print('Window closed')
    running = False
    plt.ioff()
    plt.close('all')

def signal_handler(sig, frame):
    global running
    print('Exiting...')
    running = False
    plt.ioff()  # Turn off interactive mode
    plt.close('all')
    sys.exit(0)

# Register the signal handler for SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)

def run_tests():
    plt.ion()  # Turn on interactive mode
    fig = plt.figure()
    fig.canvas.mpl_connect('close_event', handle_close)  # Connect the close event to the handler

    global running

    # Initial targets
    targets = [(random.randint(-4000, 4000), random.randint(-2000, 6000)) for _ in range(3)]

    try:
        while running:
            # Move targets slightly by a random amount within -50 to +50 and clamp values
            targets = [
                (
                    max(-4000, min(4000, x + random.randint(-250, 250))),
                    max(-2000, min(6000, y + random.randint(-250, 250)))
                )
                for x, y in targets
            ]
            
            results = [(x, y, is_point_in_polygon(x, y)) for x, y in targets]
            any_dot_in_polygon = any(result for _, _, result in results)
            print(f"Any dot in polygon: {'Yes' if any_dot_in_polygon else 'No'}")
            plot_polygon_and_points(points, results, any_dot_in_polygon)
            time.sleep(1)  # Wait for 1 second before the next update
    except KeyboardInterrupt:
        print('Interrupted by user')
        running = False
        plt.ioff()  # Turn off interactive mode
        plt.close('all')
    except Exception as e:
        print(f"Exiting due to an error: {e}")
        running = False
        plt.ioff()  # Turn off interactive mode
        plt.close('all')

if __name__ == "__main__":
    run_tests()
