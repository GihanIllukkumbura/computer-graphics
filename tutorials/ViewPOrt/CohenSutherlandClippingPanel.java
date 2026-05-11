import javax.swing.*;
import java.awt.*;
import java.util.ArrayList;

class CohenSutherlandClippingPanel extends JPanel {

    // Defining region codes
    static final int INSIDE = 0; // 0000
    static final int LEFT = 1; // 0001
    static final int RIGHT = 2; // 0010
    static final int BOTTOM = 4; // 0100
    static final int TOP = 8; // 1000

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

    public CohenSutherlandClippingPanel() {
        // Add lines to be clipped
        lines.add(new Line(25, 25, 35, 35));  // Fully inside
        lines.add(new Line(35, 45, 55, 20)); // Partially inside
        lines.add(new Line(5, 25, 20, 5));  // Completely outside

        // Perform clipping
        for (Line line : lines) {
            Line clipped = cohenSutherlandClip(line);
            if (clipped != null) {
                clippedLines.add(clipped);
            }
        }
    }

    // Function to compute region code for a point(x, y)
    static int computeCode(double x, double y) {
        int code = INSIDE;
        if (x < x_min) code |= LEFT;
        else if (x > x_max) code |= RIGHT;
        if (y < y_min) code |= BOTTOM;
        else if (y > y_max) code |= TOP;
        return code;
    }

    // Implementing Cohen-Sutherland algorithm
    // Clipping a line from P1 = (x1, y1) to P2 = (x2, y2)
    static Line cohenSutherlandClip(Line line) {
        double x1 = line.x1, y1 = line.y1, x2 = line.x2, y2 = line.y2;
        int code1 = computeCode(x1, y1);
        int code2 = computeCode(x2, y2);
        boolean accept = false;

        while (true) {
            if ((code1 == 0) && (code2 == 0)) {
                accept = true;
                break;
            } else if ((code1 & code2) != 0) {
                break;
            } else {
                int code_out;
                double x = 0, y = 0;
                if (code1 != 0) code_out = code1;
                else code_out = code2;

                if ((code_out & TOP) != 0) {
                    x = x1 + (x2 - x1) * (y_max - y1) / (y2 - y1);
                    y = y_max;
                } else if ((code_out & BOTTOM) != 0) {
                    x = x1 + (x2 - x1) * (y_min - y1) / (y2 - y1);
                    y = y_min;
                } else if ((code_out & RIGHT) != 0) {
                    y = y1 + (y2 - y1) * (x_max - x1) / (x2 - x1);
                    x = x_max;
                } else if ((code_out & LEFT) != 0) {
                    y = y1 + (y2 - y1) * (x_min - x1) / (x2 - x1);
                    x = x_min;
                }

                if (code_out == code1) {
                    x1 = x;
                    y1 = y;
                    code1 = computeCode(x1, y1);
                } else {
                    x2 = x;
                    y2 = y;
                    code2 = computeCode(x2, y2);
                }
            }
        }
        if (accept) {
            return new Line(x1, y1, x2, y2);
        } else {
            return null;
        }
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
        JFrame frame = new JFrame("Cohen-Sutherland Line Clipping");
        CohenSutherlandClippingPanel panel = new CohenSutherlandClippingPanel();
        frame.add(panel);
        frame.setSize(1300, 700);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setVisible(true);
    }
}
