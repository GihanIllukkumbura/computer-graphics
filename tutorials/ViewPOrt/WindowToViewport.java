import javax.swing.*;
import java.awt.*;

class WindowToViewport extends JPanel {

    // x_wmax, y_wmax, x_wmin, y_wmin define the boundaries of the window coordinates.
    // x_vmax, y_vmax, x_vmin, y_vmin define the boundaries of the viewport coordinates.

    int x_wmax = 100, y_wmax = 100, x_wmin = 0, y_wmin = 20;
    int x_vmax = 80, y_vmax = 80, x_vmin = 10, y_vmin = 20;

    // Points in window coordinates
    // windowPoints is an array of points in the window coordinate system.
    int[][] windowPoints = {
        {30, 80},
        {40, 60},
        {50, 70},
        {60, 50},
        {70, 60}
    };

    // Corresponding points in viewport coordinates
    // viewportPoints is an array to store the corresponding points in the viewport coordinate system.
    int[][] viewportPoints = new int[5][2];

    // sx and sy are the scaling factors for the transformation.
    float sx, sy;

    
    public WindowToViewport() {
        sx = (float)(x_vmax - x_vmin) / (x_wmax - x_wmin);
        sy = (float)(y_vmax - y_vmin) / (y_wmax - y_wmin);

        for (int i = 0; i < windowPoints.length; i++) {
            viewportPoints[i][0] = (int) (x_vmin + (float)((windowPoints[i][0] - x_wmin) * sx));
            viewportPoints[i][1] = (int) (y_vmin + (float)((windowPoints[i][1] - y_wmin) * sy));
        }
    }

    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);

        // Draw World Coordinate
        //Draws the rectangle representing the window coordinates.

        g.setColor(Color.BLACK);
        g.drawRect(x_wmin, getHeight() - y_wmax, x_wmax - x_wmin, y_wmax - y_wmin);
        g.drawString("Window", x_wmin + 10, getHeight() - y_wmax + 20);

        // Draw points in World Coordinate
        //Draws the points in the window coordinate system as filled ovals.
        for (int[] point : windowPoints) {
            g.fillOval(point[0] - 3, getHeight() - point[1] - 3, 6, 6);
        }

        // Draw Device Coordinate
        g.setColor(Color.BLACK);
        g.drawRect(x_vmin + 200, getHeight() - y_vmax, x_vmax - x_vmin, y_vmax - y_vmin);
        g.drawString("ViewPort", x_vmin + 210, getHeight() - y_vmax + 20);

        // Draw points in Device Coordinate
        for (int[] point : viewportPoints) {
            g.fillOval(point[0] + 200 - 3, getHeight() - point[1] - 3, 6, 6);
        }
    }

    public static void main(String[] args) {
        JFrame frame = new JFrame("Window to ViewPort Transformation");

        // Creating the panel for graphics
        WindowToViewport panel = new WindowToViewport();

        // Creating the table
        String[] columns = {"x_w", "y_w", "sx", "sy", "x_v", "y_v"};
        Object[][] data = new Object[5][6];
        for (int i = 0; i < panel.windowPoints.length; i++) {
            data[i][0] = panel.windowPoints[i][0];
            data[i][1] = panel.windowPoints[i][1];
            data[i][2] = panel.sx;
            data[i][3] = panel.sy;
            data[i][4] = panel.viewportPoints[i][0];
            data[i][5] = panel.viewportPoints[i][1];
        }
        JTable table = new JTable(data, columns);
        JScrollPane tableScrollPane = new JScrollPane(table);

        // Setting up the layout
        frame.setLayout(new BorderLayout());
        frame.add(panel, BorderLayout.CENTER);
        frame.add(tableScrollPane, BorderLayout.SOUTH);

        frame.setSize(600, 600);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setVisible(true);
    }
}
