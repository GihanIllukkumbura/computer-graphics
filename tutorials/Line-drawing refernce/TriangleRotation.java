import java.awt.*;
import javax.swing.*;
import java.awt.geom.AffineTransform;

public class TriangleRotation extends JPanel {
    private double rotationDegrees = 45; 

    public TriangleRotation() {
        setPreferredSize(new Dimension(400, 400));
        setBackground(Color.WHITE);
    }

    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        Graphics2D g2d = (Graphics2D) g;

        // Define the triangle points
        int x1 = 200, y1 = 200;  // Fixed vertex
        int x2 = 300, y2 = 300;
        int x3 = 250, y3 = 150;

        // Draw the original triangle
        g2d.setColor(Color.BLUE);
        g2d.drawLine(x1, y1, x2, y2);
        g2d.drawLine(x2, y2, x3, y3);
        g2d.drawLine(x3, y3, x1, y1);

        int ox1 = x1, ox2 = x2, ox3 = x3, oy1 = y1, oy2 = y2, oy3 = y3;

        
        AffineTransform transform = new AffineTransform();
        transform.rotate(Math.toRadians(rotationDegrees), x1, y1);
        g2d.transform(transform);

        // Draw the rotated triangle
        g2d.setColor(Color.RED);
        g2d.drawLine(ox1, oy1, ox2, oy2);
        g2d.drawLine(ox2, oy2, ox3, oy3);
        g2d.drawLine(ox3, oy3, ox1, oy1);

        g2d.setColor(Color.BLACK);
        g2d.rotate(Math.toRadians(-rotationDegrees), 50, 57); 
        g2d.drawString("Original Triangle (Blue)", 80, 80);
        g2d.drawString("Rotated Triangle (Red)", 80, 90);
    }

    public static void main(String[] args) {
        JFrame frame = new JFrame("Rotate a Given Triangle with Respect to an Arbitrary Point");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.add(new TriangleRotation());
        frame.setSize(400, 400);
        frame.setVisible(true);
    }
}
