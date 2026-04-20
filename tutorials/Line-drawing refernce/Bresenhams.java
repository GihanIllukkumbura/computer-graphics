import java.awt.*; 
import javax.swing.JFrame; 
import java.applet.*; 
 
public class Bresenhams extends Applet { 
    private int x1, y1, x2, y2; 
 
    public Bresenhams(int x1, int y1, int x2, int y2) { 
        this.x1 = x1; 
        this.y1 = y1; 
        this.x2 = x2; 
        this.y2 = y2; 
    } 
 
    public void paint(Graphics g) { 
        g.drawString("Bresenham algorithm", 30, 40); 
 
        int x, y, k; 
        double dx, dy, p; 
 
        dx = Math.abs(x2 - x1); 
        dy = Math.abs(y2 - y1); 
 
        x = x1; 
        y = y1; 
 
        p = 2 * dy - dx; 
 
        g.fillOval(x1, y1, 1, 1); 
 
        for (k = 0; k < dx; k++) { 
            if (p < 0) { 
                g.fillOval(x++, y, 1, 1); // plot point 
                p = (p + (2 * dy)); 
            } else { 
                g.fillOval(x++, y++, 1, 1); // plot point 
                p = (p + (2 * (dy - dx))); 
            } 
        } 
    } 
 
    public static void main(String[] args) { 
      int MaxX = 1200, MaxY = 1000; // jframe size 
      JFrame window = new JFrame(); 
      window.setBounds(30, 30, MaxX, MaxY); 
   
      // starting and ending coordinates for the line 
      Bresenhams bresenham = new Bresenhams(100, 100, 800, 200); 
       
      window.getContentPane().add(bresenham); 
      window.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE); 
      window.setVisible(true); // visibility of the JFrame 
  } 
} 