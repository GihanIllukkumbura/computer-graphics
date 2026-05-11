import javax.swing.*;
import java.awt.*;
import java.util.ArrayList;

class SutherlandHodgmanClippingPanel extends JPanel {

    // Defining x_max, y_max and x_min, y_min for
    // clipping rectangle. Since diagonal points are
    // enough to define a rectangle
    static final int x_max = 50;
    static final int y_max = 40;
    static final int x_min = 20;
    static final int y_min = 20;

    static class Point {
        double x, y;
        public Point(double x, double y) {
            this.x = x;
            this.y = y;
        }
    }

    ArrayList<Point> polygon = new ArrayList<>();
    ArrayList<Point> clippedPolygon = new ArrayList<>();

    public SutherlandHodgmanClippingPanel() {
        // Define a polygon to be clipped
        polygon.add(new Point(10, 30));
        polygon.add(new Point(30, 50));
        polygon.add(new Point(60, 50));
        polygon.add(new Point(70, 20));
        polygon.add(new Point(40, 10));

        // Perform clipping
        clippedPolygon = sutherlandHodgmanClip(polygon);
    }

    // Implementing Sutherland-Hodgman algorithm
    ArrayList<Point> sutherlandHodgmanClip(ArrayList<Point> polygon) {
        ArrayList<Point> outputList = new ArrayList<>(polygon);

        outputList = clipLeft(outputList);
        outputList = clipRight(outputList);
        outputList = clipBottom(outputList);
        outputList = clipTop(outputList);

        return outputList;
    }

    ArrayList<Point> clipLeft(ArrayList<Point> polygon) {
        ArrayList<Point> result = new ArrayList<>();
        Point prev = polygon.get(polygon.size() - 1);

        for (Point current : polygon) {
            if (current.x >= x_min) {
                if (prev.x < x_min) {
                    result.add(intersect(prev, current, x_min, true));
                }
                result.add(current);
            } else if (prev.x >= x_min) {
                result.add(intersect(prev, current, x_min, true));
            }
            prev = current;
        }
        return result;
    }

    ArrayList<Point> clipRight(ArrayList<Point> polygon) {
        ArrayList<Point> result = new ArrayList<>();
        Point prev = polygon.get(polygon.size() - 1);

        for (Point current : polygon) {
            if (current.x <= x_max) {
                if (prev.x > x_max) {
                    result.add(intersect(prev, current, x_max, true));
                }
                result.add(current);
            } else if (prev.x <= x_max) {
                result.add(intersect(prev, current, x_max, true));
            }
            prev = current;
        }
        return result;
    }

    ArrayList<Point> clipBottom(ArrayList<Point> polygon) {
        ArrayList<Point> result = new ArrayList<>();
        Point prev = polygon.get(polygon.size() - 1);

        for (Point current : polygon) {
            if (current.y >= y_min) {
                if (prev.y < y_min) {
                    result.add(intersect(prev, current, y_min, false));
                }
                result.add(current);
            } else if (prev.y >= y_min) {
                result.add(intersect(prev, current, y_min, false));
            }
            prev = current;
        }
        return result;
    }

    ArrayList<Point> clipTop(ArrayList<Point> polygon) {
        ArrayList<Point> result = new ArrayList<>();
        Point prev = polygon.get(polygon.size() - 1);

        for (Point current : polygon) {
            if (current.y <= y_max) {
                if (prev.y > y_max) {
                    result.add(intersect(prev, current, y_max, false));
                }
                result.add(current);
            } else if (prev.y <= y_max) {
                result.add(intersect(prev, current, y_max, false));
            }
            prev = current;
        }
        return result;
    }

    Point intersect(Point p1, Point p2, double boundary, boolean isVertical) {
        double x, y;
        if (isVertical) {
            x = boundary;
            y = p1.y + (p2.y - p1.y) * (boundary - p1.x) / (p2.x - p1.x);
        } else {
            y = boundary;
            x = p1.x + (p2.x - p1.x) * (boundary - p1.y) / (p2.y - p1.y);
        }
        return new Point(x, y);
    }

    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        int halfWidth = getWidth() / 2;

        // Draw the clipping rectangle on both sides
        g.setColor(Color.BLACK);
        g.drawRect(x_min * 10, getHeight() - y_max * 10, (x_max - x_min) * 10, (y_max - y_min) * 10);
        g.drawRect(x_min * 10 + halfWidth, getHeight() - y_max * 10, (x_max - x_min) * 10, (y_max - y_min) * 10);

        // Draw polygon before clipping (left side)
        g.setColor(Color.RED);
        drawPolygon(g, polygon, 0);

        // Draw polygon after clipping (right side)
        g.setColor(Color.GREEN);
        drawPolygon(g, clippedPolygon, halfWidth);
    }

    void drawPolygon(Graphics g, ArrayList<Point> polygon, int offsetX) {
        if (polygon.size() < 2) return;

        Point prev = polygon.get(polygon.size() - 1);
        for (Point current : polygon) {
            g.drawLine((int) (prev.x * 10) + offsetX, getHeight() - (int) (prev.y * 10),
                       (int) (current.x * 10) + offsetX, getHeight() - (int) (current.y * 10));
            prev = current;
        }
    }

    public static void main(String[] args) {
        JFrame frame = new JFrame("Sutherland-Hodgman Polygon Clipping");
        SutherlandHodgmanClippingPanel panel = new SutherlandHodgmanClippingPanel();
        frame.add(panel);
        frame.setSize(1300, 700);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setVisible(true);
    }
}
