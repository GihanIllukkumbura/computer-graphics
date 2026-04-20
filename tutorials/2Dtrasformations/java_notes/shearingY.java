import java.awt.*;
import javax.swing.*;

public class shearingY extends JPanel {

  private int delay = 1500;

  public void paintComponent(Graphics g) {
    super.paintComponent(g);
    int centerX = 200;
    int centerY = 600;

    int Xx = 1000, Xy = 600;
    int Yx = 200, Yy = 100;

    g.setColor(Color.BLACK);

    g.drawLine(centerX, centerY, Xx, Xy);
    g.drawLine(centerX, centerY, Yx, Yy);

    double shearfactor = 0.5;

    int xpoints[] = { 400, 400, 600, 600 };
    int ypoints[] = { 600, 400, 400, 600 };

    int numberofpoints = 4;

    g.setColor(Color.GREEN);

    g.drawPolygon(xpoints, ypoints, numberofpoints);

    int[] rxpoints = new int[xpoints.length];

    for (int i = 0; i < xpoints.length; i++) {
      rxpoints[i] = xpoints[i];
      

    }

    int[] rypoints = new int[ypoints.length];

    for (int i = 0; i < ypoints.length; i++) {
      rypoints[i] = (int) (ypoints[i] + (xpoints[i] * shearfactor));

    }

    g.setColor(Color.PINK);

    g.drawPolygon(rxpoints, rypoints, numberofpoints);

    try {
      Thread.sleep(delay);
    } catch (InterruptedException e) {

    }
  }

  public static void main(String[] args) {
    shearingY panel = new shearingY();
    JFrame application = new JFrame();

    application.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
    application.add(panel);
    application.setSize(800, 600);
    application.setVisible(true);
  }

}