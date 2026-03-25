import javax.swing.*; 
import java.awt.*; 
 
public class PointDrawer extends JPanel { 
    private Point point; 
 
    public PointDrawer(Point point) { 
        this.point = point; 
    } 
 
    @Override 
protected void paintComponent(Graphics g) { 
    super.paintComponent(g); 
    int pointSize = 5; 
    int drawX = (int) Math.round(point.getX()) - pointSize / 2; 
    int drawY = getHeight() - (int) Math.round(point.getY()) - pointSize / 2;  
    g.setColor(Color.RED); 
    g.fillOval(drawX, drawY, pointSize, pointSize); 
} 
    public static void main(String[] args) { 
        Point point = new Point(100, 300); 
        JFrame frame = new JFrame("Point Drawer"); 
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE); 
        frame.setSize(400, 400); 
        PointDrawer pointDrawer = new PointDrawer(point); 
        frame.add(pointDrawer); 
        frame.setVisible(true); 
    } 
} 
 
 
 
