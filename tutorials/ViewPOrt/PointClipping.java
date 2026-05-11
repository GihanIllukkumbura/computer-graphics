import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

public class PointClipping extends JPanel {
    // Define the area of interest (a rectangle)
    int xMin = 50, yMin = 50, xMax = 200, yMax = 200;

    // Point to be checked
    int xPoint = -1, yPoint = -1;
    boolean isInside = false;

    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);

        // Draw the area of interest
        g.setColor(Color.BLACK);
        g.drawRect(xMin, yMin, xMax - xMin, yMax - yMin);
        g.drawString("Area of Interest", xMin + 10, yMin - 10);

        // Draw the point if it has been set
        if (xPoint != -1 && yPoint != -1) {
            g.setColor(isInside ? Color.GREEN : Color.RED);
            g.fillOval(xPoint - 3, yPoint - 3, 6, 6);
            g.drawString(isInside ? "Inside" : "Outside", xPoint + 10, yPoint);
        }
    }

    public boolean checkPointInside(int x, int y) {
        return x >= xMin && x <= xMax && y >= yMin && y <= yMax;
    }

    public static void main(String[] args) {
        JFrame frame = new JFrame("Point Clipping");
        PointClipping panel = new PointClipping();

        // Input fields for user to enter point coordinates
        JTextField xField = new JTextField(5);
        JTextField yField = new JTextField(5);
        JButton checkButton = new JButton("Check Point");

        JPanel inputPanel = new JPanel();
        inputPanel.add(new JLabel("X:"));
        inputPanel.add(xField);
        inputPanel.add(new JLabel("Y:"));
        inputPanel.add(yField);
        inputPanel.add(checkButton);

        JLabel coordinatesLabel = new JLabel(
            String.format("Area of Interest Coordinates: (%d, %d), (%d, %d)", panel.xMin, panel.yMin, panel.xMax, panel.yMax)
        );

        checkButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                try {
                    int x = Integer.parseInt(xField.getText());
                    int y = Integer.parseInt(yField.getText());
                    panel.xPoint = x;
                    panel.yPoint = y;
                    panel.isInside = panel.checkPointInside(x, y);
                    panel.repaint();
                } catch (NumberFormatException ex) {
                    JOptionPane.showMessageDialog(frame, "Please enter valid integer coordinates.");
                }
            }
        });

        frame.setLayout(new BorderLayout());
        frame.add(panel, BorderLayout.CENTER);
        frame.add(inputPanel, BorderLayout.SOUTH);
        frame.add(coordinatesLabel, BorderLayout.NORTH);
        frame.setSize(300, 300);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setVisible(true);
    }
}
