import javax.swing.*;
import java.awt.*;
import java.util.ArrayList;

class LiangBarskyClippingPanel extends JPanel {

    // Defining x_max, y_max and x_min, y_min for
    // clipping rectangle. Since diagonal points are
    // enough to define a rectangle
    static final int x_max = 50;
    static final int y_max = 40;
    static final int x_min = 20;
    static final int y_min = 20;

    static class Line {
        double x1, y1, x2, y2;
        public Line(double x1, double y1, double x2, double y2) {
            this.x1 = x1;
            this.y1 = y1;
            this.x2 = x2;
            this.y2 = y2;
        }
    }

    ArrayList<Line> lines = new ArrayList<>();
    ArrayList<Line> clippedLines = new ArrayList<>();

    public LiangBarskyClippingPanel() {
        // Add lines to be clipped
        lines.add(new Line(25, 25, 35, 35));  // Fully inside
        lines.add(new Line(35, 45, 55, 20)); // Partially inside
        lines.add(new Line(5, 25, 20, 5));  // Completely outside

        // Perform clipping
        for (Line line : lines) {
            Line clipped = liangBarskyClip(line);
            if (clipped != null) {
                clippedLines.add(clipped);
            }
        }
    }

    // Implementing Liang-Barsky algorithm
    static Line liangBarskyClip(Line line) {
        double x1 = line.x1, y1 = line.y1, x2 = line.x2, y2 = line.y2;
        double p1 = -(x2 - x1), p2 = -p1, p3 = -(y2 - y1), p4 = -p3;
        double q1 = x1 - x_min, q2 = x_max - x1, q3 = y1 - y_min, q4 = y_max - y1;

        double[] p = {p1, p2, p3, p4};
        double[] q = {q1, q2, q3, q4};

        double u1 = 0.0, u2 = 1.0;
        for (int i = 0; i < 4; i++) {
            if (p[i] < 0) {
                u1 = Math.max(u1, q[i] / p[i]);
            } else if (p[i] > 0) {
                u2 = Math.min(u2, q[i] / p[i]);
            } else if (q[i] < 0) {
                return null; // Line is outside
            }
        }

        if (u1 > u2) {
            return null; // Line is outside
        }

        double nx1 = x1 + u1 * (x2 - x1);
        double ny1 = y1 + u1 * (y2 - y1);
        double nx2 = x1 + u2 * (x2 - x1);
        double ny2 = y1 + u2 * (y2 - y1);

        return new Line(nx1, ny1, nx2, ny2);
    }

    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        int halfWidth = getWidth() / 2;

        // Draw the clipping rectangle on both sides
        g.setColor(Color.BLACK);
        g.drawRect(x_min * 10, getHeight() - y_max * 10, (x_max - x_min) * 10, (y_max - y_min) * 10);
        g.drawRect(x_min * 10 + halfWidth, getHeight() - y_max * 10, (x_max - x_min) * 10, (y_max - y_min) * 10);

        // Draw lines before clipping (left side)
        g.setColor(Color.RED);
        for (Line line : lines) {
            g.drawLine((int) (line.x1 * 10), getHeight() - (int) (line.y1 * 10), (int) (line.x2 * 10), getHeight() - (int) (line.y2 * 10));
        }

        // Draw lines after clipping (right side)
        g.setColor(Color.GREEN);
        for (Line line : clippedLines) {
            g.drawLine((int) (line.x1 * 10) + halfWidth, getHeight() - (int) (line.y1 * 10), (int) (line.x2 * 10) + halfWidth, getHeight() - (int) (line.y2 * 10));
        }
    }

    public static void main(String[] args) {
        JFrame frame = new JFrame("Liang-Barsky Line Clipping");
        LiangBarskyClippingPanel panel = new LiangBarskyClippingPanel();
        frame.add(panel);
        frame.setSize(1300, 700);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setVisible(true);
    }
}
