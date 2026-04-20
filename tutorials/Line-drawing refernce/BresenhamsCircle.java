import javax.swing.*; 
import java.awt.*; 
 
public class BresenhamsCircle extends JPanel { 
    private int xc, yc, r; 
 
    public BresenhamsCircle(int xc, int yc, int r) { 
        this.xc = xc; 
        this.yc = yc; 
        this.r = r; 
    } 
 
    public void paintComponent(Graphics g) { 
        super.paintComponent(g); 
 
        int x = 0; 
        int y = r; 
        int p = 3 - (2 * r); 
 
        do { 
            if (p < 0) { 
                p = p + (4 * x) + 6; 
            } else { 
                p = p + (4 * (x - y)) + 10; 
                y = y - 1; 
            } 
            x = x + 1; 
 
            plotCirclePoints(g, xc, yc, x, y); 
 
        } while (x <= y); 
    } 
 
    private void plotCirclePoints(Graphics g, int xc, int yc, int x, int y) { 
        g.drawLine(xc + x, yc + y, xc + x, yc + y); 
        g.drawLine(xc + x, yc - y, xc + x, yc - y); 
 
        g.drawLine(xc - x, yc + y, xc - x, yc + y); 
        g.drawLine(xc - x, yc - y, xc - x, yc - y); 
 
        g.drawLine(xc + y, yc + x, xc + y, yc + x); 
        g.drawLine(xc + y, yc - x, xc + y, yc - x); 
 
        g.drawLine(xc - y, yc + x, xc - y, yc + x); 
        g.drawLine(xc - y, yc - x, xc - y, yc - x); 
    } 
 
    public static void main(String[] args) { 
      int MaxX = 800, MaxY = 600;  
      JFrame window = new JFrame(); 
      window.setBounds(30, 30, MaxX, MaxY); 
      window.getContentPane().add(new BresenhamsCircle(300,300,200)); 
      window.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE); 
      window.setVisible(true); 
  } 
} 