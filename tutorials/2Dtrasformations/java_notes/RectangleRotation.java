import java.awt.*;
import javax.swing.*;
import java.awt.geom.AffineTransform;

public class RectangleRotation extends JPanel {
    private double rotationDegrees = 60;

    public RectangleRotation() {
        setPreferredSize(new Dimension(400, 400));
        setBackground(Color.WHITE);
    }

    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        Graphics2D g2d = (Graphics2D) g; // ensuress that the componets background i

        int x1 = 200, y1 = 200;
        int width = 200, height = 100;

        // draw the rectangle
        g2d.setColor(Color.BLUE);
        g2d.drawRect(x1, y1, width, height);

        // applying the rotation
        AffineTransform transform = new AffineTransform();
        transform.rotate(Math.toRadians(rotationDegrees),x1,y1);
        g2d.setTransform(transform);
        g2d.setColor(Color.RED);
        g2d.drawRect(x1,y1,width,height);



    }
    public static void main(String[] args) {

        // int MaxX = 1200, MaxY = 1000; // jframe size
        // JFrame window = new JFrame("Rectangle Transformation");
        // window.setBounds(30, 30, MaxX, MaxY);
        // window.getContentPane().add(new Rectangle());
        // window.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        // window.setVisible(true); // visibilty of the jframe

        JFrame frame = new JFrame("Rectangle Rotation");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.add(new RectangleRotation());
        frame.setSize(600,800);
        frame.setVisible(true);  // visibilty of the jframe

}

}
