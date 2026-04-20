import java.awt.*;
import javax.swing.*;

public class scaling extends JPanel {

    private int delay = 1500;

    public void paintComponent(Graphics g) {
        super.paintComponent(g);
        int sx = 2, sy = 2;

        int[] x = { 50, 150, 250 };
        int[] y = { 250, 50, 250 };

        int numPoints = 3;

        g.setColor(Color.GREEN);

        g.drawPolygon(x, y, numPoints);

        int[] rx = new int[x.length];

        for (int i = 0; i < x.length; i++) {
            rx[i] = x[i] * sx;

        }
        int[] ry = new int[y.length];

        for (int i = 0; i < y.length; i++) {
            ry[i] = y[i] * sy;

        }

        g.setColor(Color.PINK);

        g.drawPolygon(rx, ry, numPoints);

        try{
            Thread.sleep(delay);
        }catch(InterruptedException e){
            
        }
    }

    public static void main(String[] args) {
        scaling panel = new scaling();
        JFrame application = new JFrame();

        application.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        application.add(panel);
        application.setSize(800, 600);
        application.setVisible(true);
    }

}