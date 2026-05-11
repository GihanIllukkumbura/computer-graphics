class LiangBarskyClipping {

    // Defining x_max, y_max and x_min, y_min for
    // clipping rectangle. Since diagonal points are
    // enough to define a rectangle
    static final int x_max = 10;
    static final int y_max = 8;
    static final int x_min = 4;
    static final int y_min = 4;

    // Implementing Liang-Barsky algorithm
    // Clipping a line from P1 = (x1, y1) to P2 = (x2, y2)
    static void liangBarskyClip(double x1, double y1, double x2, double y2) {
        double p1 = -(x2 - x1), p2 = -p1, p3 = -(y2 - y1), p4 = -p3;
        double q1 = x1 - x_min, q2 = x_max - x1, q3 = y1 - y_min, q4 = y_max - y1;

        double[] p = { p1, p2, p3, p4 };
        double[] q = { q1, q2, q3, q4 };

        double u1 = 0.0, u2 = 1.0;
        for (int i = 0; i < 4; i++) {
            if (p[i] < 0) {
                u1 = Math.max(u1, q[i] / p[i]);
            } else if (p[i] > 0) {
                u2 = Math.min(u2, q[i] / p[i]);
            } else if (q[i] < 0) {
                System.out.println("Line rejected");
                return; // Line is outside
            }
        }

        if (u1 > u2) {
            System.out.println("Line rejected");
            return; // Line is outside
        }

        double nx1 = x1 + u1 * (x2 - x1);
        double ny1 = y1 + u1 * (y2 - y1);
        double nx2 = x1 + u2 * (x2 - x1);
        double ny2 = y1 + u2 * (y2 - y1);

        System.out.println("Line accepted from " + nx1 + ", " + ny1 + " to " + nx2 + ", " + ny2);
        // Here the user can add code to display the
        // rectangle along with the accepted (portion of) lines
    }

    public static void main(String[] args) {
        // First Line segment
        // P11 = (5, 5), P12 = (7, 7)
        liangBarskyClip(5, 5, 7, 7);

        // Second Line segment
        // P21 = (7, 9), P22 = (11, 4)
        liangBarskyClip(7, 9, 11, 4);

        // Third Line segment
        // P31 = (1, 5), P32 = (4, 1)
        liangBarskyClip(1, 5, 4, 1);
    }
}
