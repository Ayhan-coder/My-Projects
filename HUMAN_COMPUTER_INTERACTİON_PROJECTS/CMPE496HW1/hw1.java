// Simple Object-Oriented Drawing Editor in Java
// This application demonstrates OOP principles with interactive graphics using Swing
/* * @file hw1.java
 * @author Ali Ayhan Gunder - 2021400219
 * @date 2025-14-07
 */
import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.awt.geom.Line2D;
import java.awt.geom.Rectangle2D;

/**
 * @brief Abstract base class for all drawable shapes.
 *
 * Demonstrates inheritance and polymorphism.
 */
abstract class Shape {
    /** X coordinate of the shape center. */
    protected int x;
    /** Y coordinate of the shape center. */
    protected int y;
    /** Color of the shape. */
    protected Color color;
    /** Whether the shape is currently selected. */
    protected boolean selected;

    /**
     * @brief Constructor to initialize position and color.
     * @param x X coordinate
     * @param y Y coordinate
     * @param color Shape color
     */
    public Shape(int x, int y, Color color) {
        this.x = x;
        this.y = y;
        this.color = color;
        this.selected = false;
    }

    /**
     * @brief Get X coordinate.
     * @return X coordinate
     */
    public int getX() { return x; }
    /**
     * @brief Set X coordinate.
     * @param x New X coordinate
     */
    public void setX(int x) { this.x = x; }
    /**
     * @brief Get Y coordinate.
     * @return Y coordinate
     */
    public int getY() { return y; }
    /**
     * @brief Set Y coordinate.
     * @param y New Y coordinate
     */
    public void setY(int y) { this.y = y; }
    /**
     * @brief Get shape color.
     * @return Color
     */
    public Color getColor() { return color; }
    /**
     * @brief Set shape color.
     * @param color New color
     */
    public void setColor(Color color) { this.color = color; }
    /**
     * @brief Check if shape is selected.
     * @return True if selected
     */
    public boolean isSelected() { return selected; }
    /**
     * @brief Set selection state.
     * @param selected True if selected
     */
    public void setSelected(boolean selected) { this.selected = selected; }

    /**
     * @brief Draw the shape.
     * @param g2d Graphics2D context
     */
    public abstract void draw(Graphics2D g2d);
    /**
     * @brief Check if a point is on the shape (for eraser/select).
     * @param x X coordinate
     * @param y Y coordinate
     * @return True if point is on the shape
     */
    public abstract boolean contains(int x, int y);
    /**
     * @brief Move the shape by delta values.
     * @param deltaX Change in X
     * @param deltaY Change in Y
     */
    public abstract void move(int deltaX, int deltaY);
}

/**
 * @brief Circle class inheriting from Shape.
 */
class Circle extends Shape {
    /** Radius of the circle. */
    private int radius;
    /** Margin for border hit-testing. */
    private static final int BORDER_MARGIN = 4;

    /**
     * @brief Constructor for Circle.
     * @param x Center X
     * @param y Center Y
     * @param radius Circle radius
     * @param color Circle color
     */
    public Circle(int x, int y, int radius, Color color) {
        super(x, y, color);
        this.radius = radius;
    }

    /**
     * @brief Get radius.
     * @return Radius
     */
    public int getRadius() { return radius; }
    /**
     * @brief Set radius.
     * @param radius New radius
     */
    public void setRadius(int radius) { this.radius = radius; }
    /**
     * @brief Draw the circle.
     * @param g2d Graphics2D context
     */
    @Override
    public void draw(Graphics2D g2d) {
        // Draw filled circle
        g2d.setColor(color);
        g2d.fillOval(x - radius, y - radius, radius * 2, radius * 2);
        
        // Draw border (thicker if selected)
        if (selected) {
            g2d.setColor(Color.RED);
            g2d.setStroke(new BasicStroke(4));
        } else {
            g2d.setColor(Color.BLACK);
            g2d.setStroke(new BasicStroke(2));
        }
        g2d.drawOval(x - radius, y - radius, radius * 2, radius * 2);
    }

    /**
     * @brief Check if point is on the border of the circle (for eraser).
     * @param x X coordinate
     * @param y Y coordinate
     * @return True if near border
     */
    @Override
    public boolean contains(int x, int y) {
        double distance = Math.sqrt(Math.pow(x - this.x, 2) + Math.pow(y - this.y, 2));
        // Only detect near the border (within 4px band)
        return distance >= radius - BORDER_MARGIN && distance <= radius + BORDER_MARGIN;
    }

    /**
     * @brief Move the circle.
     * @param deltaX Change in X
     * @param deltaY Change in Y
     */
    @Override
    public void move(int deltaX, int deltaY) {
        this.x += deltaX;
        this.y += deltaY;
    }
}

/**
 * @brief Square class inheriting from Shape.
 */
class Square extends Shape {
    /** Size (side length) of the square. */
    private int size;
    /** Margin for border hit-testing. */
    private static final int BORDER_MARGIN = 4;

    /**
     * @brief Constructor for Square.
     * @param x Center X
     * @param y Center Y
     * @param size Side length
     * @param color Square color
     */
    public Square(int x, int y, int size, Color color) {
        super(x, y, color);
        this.size = size;
    }

    /**
     * @brief Get size (side length).
     * @return Size
     */
    public int getSize() { return size; }
    /**
     * @brief Set size (side length).
     * @param size New size
     */
    public void setSize(int size) { this.size = size; }
    /**
     * @brief Draw the square.
     * @param g2d Graphics2D context
     */
    @Override
    public void draw(Graphics2D g2d) {
        // Draw filled square
        g2d.setColor(color);
        g2d.fillRect(x - size / 2, y - size / 2, size, size);
        
        // Draw border (thicker if selected)
        if (selected) {
            g2d.setColor(Color.RED);
            g2d.setStroke(new BasicStroke(4));
        } else {
            g2d.setColor(Color.BLACK);
            g2d.setStroke(new BasicStroke(2));
        }
        g2d.drawRect(x - size / 2, y - size / 2, size, size);
    }

    /**
     * @brief Check if point is on the border of the square (for eraser).
     * @param x X coordinate
     * @param y Y coordinate
     * @return True if near border
     */
    @Override
    public boolean contains(int x, int y) {
        int left = this.x - size / 2;
        int right = this.x + size / 2;
        int top = this.y - size / 2;
        int bottom = this.y + size / 2;
        int border = BORDER_MARGIN;
        boolean onLeft = Math.abs(x - left) <= border && y >= top && y <= bottom;
        boolean onRight = Math.abs(x - right) <= border && y >= top && y <= bottom;
        boolean onTop = Math.abs(y - top) <= border && x >= left && x <= right;
        boolean onBottom = Math.abs(y - bottom) <= border && x >= left && x <= right;
        return onLeft || onRight || onTop || onBottom;
    }

    /**
     * @brief Move the square.
     * @param deltaX Change in X
     * @param deltaY Change in Y
     */
    @Override
    public void move(int deltaX, int deltaY) {
        this.x += deltaX;
        this.y += deltaY;
    }
}

/**
 * @brief Line class inheriting from Shape.
 */
class Line extends Shape {
    /** X coordinate of line end. */
    private int x2;
    /** Y coordinate of line end. */
    private int y2;
    /** Stroke width of the line. */
    private int strokeWidth;
    /** Margin for line hit-testing. */
    private static final int LINE_MARGIN = 5;

    /**
     * @brief Constructor for Line.
     * @param x1 Start X
     * @param y1 Start Y
     * @param x2 End X
     * @param y2 End Y
     * @param color Line color
     * @param strokeWidth Line thickness
     */
    public Line(int x1, int y1, int x2, int y2, Color color, int strokeWidth) {
        super(x1, y1, color);
        this.x2 = x2;
        this.y2 = y2;
        this.strokeWidth = strokeWidth;
    }

    /**
     * @brief Get X2 (end X).
     * @return X2
     */
    public int getX2() { return x2; }
    /**
     * @brief Set X2 (end X).
     * @param x2 New X2
     */
    public void setX2(int x2) { this.x2 = x2; }
    /**
     * @brief Get Y2 (end Y).
     * @return Y2
     */
    public int getY2() { return y2; }
    /**
     * @brief Set Y2 (end Y).
     * @param y2 New Y2
     */
    public void setY2(int y2) { this.y2 = y2; }
    /**
     * @brief Draw the line.
     * @param g2d Graphics2D context
     */
    @Override
    public void draw(Graphics2D g2d) {
        if (selected) {
            g2d.setColor(Color.RED);
            g2d.setStroke(new BasicStroke(strokeWidth + 2));
        } else {
            g2d.setColor(color);
            g2d.setStroke(new BasicStroke(strokeWidth));
        }
        g2d.drawLine(x, y, x2, y2);
    }

    /**
     * @brief Check if point is near the line (for eraser/select).
     * @param x X coordinate
     * @param y Y coordinate
     * @return True if near line
     */
    @Override
    public boolean contains(int x, int y) {
        int margin = Math.max(LINE_MARGIN, strokeWidth / 2 + 2);
        double dist = Line2D.ptSegDist(this.x, this.y, x2, y2, x, y);
        return dist <= margin;
    }

    /**
     * @brief Move the line.
     * @param deltaX Change in X
     * @param deltaY Change in Y
     */
    @Override
    public void move(int deltaX, int deltaY) {
        this.x += deltaX;
        this.y += deltaY;
        this.x2 += deltaX;
        this.y2 += deltaY;
    }
}

/**
 * @brief Custom JPanel for drawing area.
 */
class DrawingPanel extends JPanel {
    /** List of shapes in the drawing. */
    private List<Shape> shapes;
    /** Reference to parent frame. */
    private hw1 parent;

    /**
     * @brief Constructor for DrawingPanel.
     * @param parent Reference to main application
     */
    public DrawingPanel(hw1 parent) {
        this.parent = parent;
        this.shapes = new ArrayList<>();
        setBackground(Color.WHITE);
        // setPreferredSize(new Dimension(800, 500)); // Let layout manager handle size
        
        // Set custom cursor (pen-like, using crosshair as placeholder)
        setCursor(Cursor.getPredefinedCursor(Cursor.CROSSHAIR_CURSOR));
        
        // Add mouse listeners
        addMouseListener(new MouseAdapter() {
            @Override
            public void mousePressed(MouseEvent e) {
                parent.handleMousePressed(e);
            }
            
            @Override
            public void mouseReleased(MouseEvent e) {
                parent.handleMouseReleased(e);
            }
            
            @Override
            public void mouseEntered(MouseEvent e) {
                // Set pen cursor when mouse enters drawing area
                setCursor(Cursor.getPredefinedCursor(Cursor.CROSSHAIR_CURSOR));
            }
            
            @Override
            public void mouseExited(MouseEvent e) {
                // Revert to default cursor when mouse leaves drawing area
                setCursor(Cursor.getDefaultCursor());
            }
        });
        
        addMouseMotionListener(new MouseMotionAdapter() {
            @Override
            public void mouseDragged(MouseEvent e) {
                parent.handleMouseDragged(e);
            }
            @Override
            public void mouseMoved(MouseEvent e) {
                if (parent.currentTool.equals("Erase")) {
                    repaint();
                }
            }
        });
    }

    /**
     * @brief Add shape to the drawing.
     * @param shape Shape to add
     */
    public void addShape(Shape shape) {
        shapes.add(shape);
        repaint();
    }

    /**
     * @brief Remove shape from the drawing.
     * @param shape Shape to remove
     */
    public void removeShape(Shape shape) {
        shapes.remove(shape);
        repaint();
    }

    /**
     * @brief Get all shapes in the drawing.
     * @return List of shapes
     */
    public List<Shape> getShapes() {
        return shapes;
    }

    /**
     * @brief Find shape at specified coordinates.
     * @param x X coordinate
     * @param y Y coordinate
     * @return Shape at position or null
     */
    public Shape findShapeAt(int x, int y) {
        // Search from top to bottom (last drawn first)
        for (int i = shapes.size() - 1; i >= 0; i--) {
            if (shapes.get(i).contains(x, y)) {
                return shapes.get(i);
            }
        }
        return null;
    }

    /**
     * @brief Paint component - draws all shapes using polymorphism.
     * @param g Graphics context
     */
    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        Graphics2D g2d = (Graphics2D) g;
        
        // Enable anti-aliasing for smoother graphics
        g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
        
        // Draw all shapes using polymorphism
        for (Shape shape : shapes) {
            shape.draw(g2d);
        }
        
        // Draw eraser area if in erase mode
        if (parent.currentTool.equals("Erase")) {
            PointerInfo pi = MouseInfo.getPointerInfo();
            if (pi != null) {
                Point mp = pi.getLocation();
                SwingUtilities.convertPointFromScreen(mp, this);
                int half = parent.shapeSize / 2;
                g2d.setColor(new Color(255, 0, 0, 80));
                g2d.fillRect(mp.x - half, mp.y - half, parent.shapeSize, parent.shapeSize);
                g2d.setColor(Color.RED);
                g2d.setStroke(new BasicStroke(2));
                g2d.drawRect(mp.x - half, mp.y - half, parent.shapeSize, parent.shapeSize);
            }
        }
    }
}

/**
 * @brief Main application class for the drawing editor.
 */
public class hw1 extends JFrame {
    // UI Components
    /** Button for Circle tool. */
    private JButton btnCircle;
    /** Button for Square tool. */
    private JButton btnSquare;
    /** Button for Line tool. */
    private JButton btnLine;
    /** Button for Erase tool. */
    private JButton btnErase;
    /** Button for Clean All. */
    private JButton btnCleanAll;
    /** Button for Stylus tool. */
    private JButton btnStylus;
    /** Label for instructions. */
    private JLabel lblInstructions;
    /** Drawing area panel. */
    private DrawingPanel drawingPanel;
    /** Color selection dropdown. */
    private JComboBox<String> colorComboBox;
    /** Slider for shape size. */
    private JSlider sizeSlider;
    /** Current shape size. */
    public int shapeSize = 30;
    /** Current selected tool. */
    public String currentTool = "Circle";
    /** Line drawing state. */
    private boolean isDrawingLine = false;
    /** Line start X. */
    private int lineStartX;
    /** Line start Y. */
    private int lineStartY;
    /** Currently selected shape. */
    private Shape selectedShape = null;
    /** Dragging state. */
    private boolean isDragging = false;
    /** Drag start X. */
    private int dragStartX;
    /** Drag start Y. */
    private int dragStartY;
    /** Stylus drawing state. */
    private boolean isDrawingStylus = false;
    /** Current stylus path. */
    private StylusPath currentStylusPath = null;
    /** Color names for dropdown. */
    private final String[] COLOR_NAMES = {"Red", "Blue", "Green", "Orange", "Magenta", "Cyan", "Purple"};
    /** Color map for names. */
    private final Map<String, Color> COLOR_MAP = Map.of(
        "Red", Color.RED,
        "Blue", Color.BLUE,
        "Green", Color.GREEN,
        "Orange", Color.ORANGE,
        "Magenta", Color.MAGENTA,
        "Cyan", Color.CYAN,
        "Purple", new Color(128, 0, 128)
    );
    /** Currently selected color. */
    private Color selectedColor = Color.RED; // Default color
    // --- Magic Number Constants ---
    /** Margin for border detection in Circle/Square. */
    private static final int BORDER_MARGIN = 4;
    /** Margin for line hit-testing. */
    private static final int LINE_MARGIN = 5;
    /** Margin for stylus path hit-testing. */
    private static final int STYLUS_MARGIN = 5;
    private boolean isErasing = false;
    private EraserPath currentEraserPath = null;

    /**
     * @brief Constructor - sets up the GUI.
     */
    public hw1() {
        initializeComponents();
        setupLayout();
        setupEventHandlers();
        
        // Set frame properties
        setTitle("Object-Oriented Drawing Editor in Java");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(1000,800); // No need, will maximize
        setResizable(true); 
        setExtendedState(JFrame.MAXIMIZED_BOTH); // Start maximized
        pack();
        setLocationRelativeTo(null); // Center on screen
    }

    /**
     * @brief Initialize GUI components.
     */
    private void initializeComponents() {
        // Create toolbar buttons
        btnCircle = new JButton("Circle");
        btnSquare = new JButton("Square");
        btnLine = new JButton("Line");
        btnStylus = new JButton("Stylus");
        btnErase = new JButton("Erase");
        btnCleanAll = new JButton("Clean All");
        
        // Create color dropdown
        colorComboBox = new JComboBox<>(COLOR_NAMES);
        colorComboBox.setSelectedItem("Red");
        colorComboBox.addActionListener(e -> {
            String colorName = (String) colorComboBox.getSelectedItem();
            selectedColor = COLOR_MAP.getOrDefault(colorName, Color.RED);
        });
        
        // Create shape size slider
        sizeSlider = new JSlider(1, 100, 30);
        sizeSlider.setMajorTickSpacing(25);
        sizeSlider.setMinorTickSpacing(5);
        sizeSlider.setPaintTicks(true);
        sizeSlider.setPaintLabels(true);
        sizeSlider.addChangeListener(e -> {
            shapeSize = sizeSlider.getValue();
        });
        
        // Create instruction label
        lblInstructions = new JLabel("Select a tool and click to draw. Click on shapes to select/move them.");
        
        // Create drawing panel
        drawingPanel = new DrawingPanel(this);
        
        // Set initial button states
        updateButtonStyles();
    }

    /**
     * @brief Setup the layout of components.
     */
    private void setupLayout() {
        setLayout(new BorderLayout());
        
        // Create toolbar panel
        JPanel toolbar = new JPanel(new FlowLayout(FlowLayout.LEFT));
        toolbar.add(btnCircle);
        toolbar.add(btnSquare);
        toolbar.add(btnLine);
        toolbar.add(btnStylus);
        toolbar.add(btnErase);
        toolbar.add(btnCleanAll);
        toolbar.add(new JLabel("Color:")); // Label for color
        toolbar.add(colorComboBox); // Add color dropdown
        toolbar.add(new JLabel("Size:"));
        toolbar.add(sizeSlider);
        toolbar.add(Box.createHorizontalStrut(20)); // Add some space
        toolbar.add(lblInstructions);
        
        // Add components to frame
        add(toolbar, BorderLayout.NORTH);
        add(drawingPanel, BorderLayout.CENTER);
    }

    /**
     * @brief Setup event handlers for buttons.
     */
    private void setupEventHandlers() {
        btnCircle.addActionListener(e -> {
            currentTool = "Circle";
            resetDrawingState();
            updateButtonStyles();
            // Set default circle size to 30
            if (shapeSize != 30) {
                shapeSize = 30;
                sizeSlider.setValue(30);
            }
            lblInstructions.setText("Circle tool: Click to create a circle. Click and drag a shape to move it.");
        });
        
        btnSquare.addActionListener(e -> {
            currentTool = "Square";
            resetDrawingState();
            updateButtonStyles();
            // Set default square size to 30
            if (shapeSize != 30) {
                shapeSize = 30;
                sizeSlider.setValue(30);
            }
            lblInstructions.setText("Square tool: Click to create a square. Click and drag a shape to move it.");
        });
        
        btnLine.addActionListener(e -> {
            currentTool = "Line";
            resetDrawingState();
            updateButtonStyles();
            // Set default line size to 5
            if (shapeSize != 5) {
                shapeSize = 5;
                sizeSlider.setValue(5);
            }
            lblInstructions.setText("Line tool: Click to start, click again to finish the line.");
        });
        
        btnStylus.addActionListener(e -> {
            currentTool = "Stylus";
            resetDrawingState();
            updateButtonStyles();
            // Set default stylus size to 5
            if (shapeSize != 5) {
                shapeSize = 5;
                sizeSlider.setValue(5);
            }
            lblInstructions.setText("Stylus tool: Click and drag to draw freehand lines.");
        });
        
        btnErase.addActionListener(e -> {
            currentTool = "Erase";
            resetDrawingState();
            updateButtonStyles();
            // Set default eraser size to 75
            if (shapeSize != 75) {
                shapeSize = 75;
                sizeSlider.setValue(75);
            }
            lblInstructions.setText("Eraser tool: Move the mouse to position the eraser, click to erase shapes.");
        });
        
        btnCleanAll.addActionListener(e -> {
            drawingPanel.getShapes().clear();
            drawingPanel.repaint();
            deselectAllShapes();
            lblInstructions.setText("All shapes cleared. Select a tool to start drawing.");
        });
    }

    /**
     * @brief Reset drawing state when switching tools.
     */
    private void resetDrawingState() {
        isDrawingLine = false;
        deselectAllShapes();
        lblInstructions.setText("Select a tool and click to draw. Click on shapes to select/move them.");
    }

    /**
     * @brief Update button styles to show current selection.
     */
    private void updateButtonStyles() {
        // Reset all buttons to default
        btnCircle.setBackground(null);
        btnSquare.setBackground(null);
        btnLine.setBackground(null);
        btnStylus.setBackground(null);
        btnErase.setBackground(null);
        
        // Highlight current tool
        switch (currentTool) {
            case "Circle":
                btnCircle.setBackground(Color.LIGHT_GRAY);
                break;
            case "Square":
                btnSquare.setBackground(Color.LIGHT_GRAY);
                break;
            case "Line":
                btnLine.setBackground(Color.LIGHT_GRAY);
                break;
            case "Stylus":
                btnStylus.setBackground(Color.LIGHT_GRAY);
                break;
            case "Erase":
                btnErase.setBackground(Color.PINK);
                break;
        }
    }

    /**
     * @brief Handle mouse pressed events.
     * @param e MouseEvent
     */
    public void handleMousePressed(MouseEvent e) {
        if (currentTool.equals("Erase")) {
            // Start erasing with left mouse button (like drawing)
            if (SwingUtilities.isLeftMouseButton(e)) {
                isErasing = true;
                currentEraserPath = new EraserPath(shapeSize);
                currentEraserPath.addPoint(e.getX(), e.getY());
                drawingPanel.addShape(currentEraserPath);
                lblInstructions.setText("Eraser tool: Drag to erase with circular brush. Release to stop erasing.");
            }
        } else if (currentTool.equals("Line")) {
            // Handle line drawing (two-click process)
            handleLineDrawing(e.getX(), e.getY());
        } else if (currentTool.equals("Stylus")) {
            // Start a new stylus path
            isDrawingStylus = true;
            currentStylusPath = new StylusPath(selectedColor, shapeSize);
            currentStylusPath.addPoint(e.getX(), e.getY());
            drawingPanel.addShape(currentStylusPath);
            lblInstructions.setText("Stylus tool: Drag to draw freehand. Release to finish.");
        } else {
            // Check if clicking on existing shape for selection/movement
            Shape clickedShape = drawingPanel.findShapeAt(e.getX(), e.getY());
            
            if (clickedShape != null) {
                // Select shape and prepare for dragging
                selectShape(clickedShape);
                isDragging = true;
                dragStartX = e.getX();
                dragStartY = e.getY();
                lblInstructions.setText("Shape selected: Drag to move. Click elsewhere to deselect.");
            } else {
                // Create new shape
                createShape(e.getX(), e.getY());
                lblInstructions.setText(currentTool + " created. Click and drag to move shapes, or select another tool.");
            }
        }
        drawingPanel.repaint();
    }

    /**
     * @brief Handle mouse dragged events.
     * @param e MouseEvent
     */
    public void handleMouseDragged(MouseEvent e) {
        if (isDragging && selectedShape != null) {
            int deltaX = e.getX() - dragStartX;
            int deltaY = e.getY() - dragStartY;
            selectedShape.move(deltaX, deltaY);
            dragStartX = e.getX();
            dragStartY = e.getY();
            drawingPanel.repaint();
        } else if (currentTool.equals("Stylus") && isDrawingStylus && currentStylusPath != null) {
            currentStylusPath.addPoint(e.getX(), e.getY());
            drawingPanel.repaint();
        } else if (currentTool.equals("Erase") && isErasing && currentEraserPath != null && SwingUtilities.isLeftMouseButton(e)) {
            currentEraserPath.addPoint(e.getX(), e.getY());
            drawingPanel.repaint();
        }
    }

    /**
     * @brief Handle mouse released events.
     * @param e MouseEvent
     */
    public void handleMouseReleased(MouseEvent e) {
        isDragging = false;
        if (currentTool.equals("Stylus")) {
            isDrawingStylus = false;
            currentStylusPath = null;
        } else if (currentTool.equals("Erase")) {
            isErasing = false;
            currentEraserPath = null;
        }
    }

    /**
     * @brief Create a new shape at the specified position.
     * @param x X coordinate
     * @param y Y coordinate
     */
    private void createShape(int x, int y) {
        Color color = selectedColor;
        Shape newShape = null;
        switch (currentTool) {
            case "Circle":
                newShape = new Circle(x, y, shapeSize / 2, color);
                break;
            case "Square":
                newShape = new Square(x, y, shapeSize, color);
                break;
        }
        
        if (newShape != null) {
            drawingPanel.addShape(newShape);
        }
    }

    /**
     * @brief Handle line drawing (two-click process).
     * @param x X coordinate
     * @param y Y coordinate
     */
    private void handleLineDrawing(int x, int y) {
        if (!isDrawingLine) {
            // First click - start line
            lineStartX = x;
            lineStartY = y;
            isDrawingLine = true;
            lblInstructions.setText("Click again to finish the line");
        } else {
            // Second click - finish line
            Color color = selectedColor;
            Line line = new Line(lineStartX, lineStartY, x, y, color, shapeSize);
            drawingPanel.addShape(line);
            isDrawingLine = false;
            lblInstructions.setText("Select a tool and click to draw. Click on shapes to select/move them.");
        }
    }

    /**
     * @brief Select a shape (deselect others).
     * @param shape Shape to select
     */
    private void selectShape(Shape shape) {
        deselectAllShapes();
        shape.setSelected(true);
        selectedShape = shape;
    }

    /**
     * @brief Deselect all shapes.
     */
    private void deselectAllShapes() {
        for (Shape shape : drawingPanel.getShapes()) {
            shape.setSelected(false);
        }
        selectedShape = null;
    }

    /**
     * @brief Erase shape at specified coordinates.
     * @param x X coordinate
     * @param y Y coordinate
     */
    private void eraseShapeAt(int x, int y) {
        // Erase any shape that intersects the eraser area using geometric intersection
        java.util.List<Shape> toRemove = new java.util.ArrayList<>();
        int half = shapeSize / 2;
        Rectangle2D eraserRect = new Rectangle2D.Double(x - half, y - half, shapeSize, shapeSize);
        for (Shape shape : new java.util.ArrayList<>(drawingPanel.getShapes())) {
            boolean hit = false;
            if (shape instanceof Line) {
                Line line = (Line) shape;
                if (eraserRect.intersectsLine(line.getX(), line.getY(), line.getX2(), line.getY2())) {
                    hit = true;
                }
            } else if (shape instanceof StylusPath) {
                StylusPath path = (StylusPath) shape;
                java.util.List<Point> pts = path.getPoints();
                for (int i = 1; i < pts.size(); i++) {
                    Point p1 = pts.get(i - 1);
                    Point p2 = pts.get(i);
                    if (eraserRect.intersectsLine(p1.x, p1.y, p2.x, p2.y)) {
                        hit = true;
                        break;
                    }
                }
            } else if (shape instanceof Circle) {
                Circle circle = (Circle) shape;
                // Check 8 points on the border of the circle for intersection
                int cx = circle.getX();
                int cy = circle.getY();
                int r = circle.getRadius();
                for (int i = 0; i < 8; i++) {
                    double angle = Math.PI * 2 * i / 8;
                    int px = (int) (cx + r * Math.cos(angle));
                    int py = (int) (cy + r * Math.sin(angle));
                    if (eraserRect.contains(px, py)) {
                        hit = true;
                        break;
                    }
                }
            } else if (shape instanceof Square) {
                Square square = (Square) shape;
                int left = square.getX() - square.getSize() / 2;
                int right = square.getX() + square.getSize() / 2;
                int top = square.getY() - square.getSize() / 2;
                int bottom = square.getY() + square.getSize() / 2;
                // Check 4 sides as lines
                if (eraserRect.intersectsLine(left, top, right, top) ||
                    eraserRect.intersectsLine(right, top, right, bottom) ||
                    eraserRect.intersectsLine(right, bottom, left, bottom) ||
                    eraserRect.intersectsLine(left, bottom, left, top)) {
                    hit = true;
                }
            }
            if (hit) toRemove.add(shape);
        }
        for (Shape s : toRemove) {
            drawingPanel.removeShape(s);
            if (selectedShape == s) selectedShape = null;
        }
    }

    /**
     * @brief Main method - program entry point.
     * @param args Command-line arguments
     */
    public static void main(String[] args) {
        // Set system look and feel
        try {
            UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
        } catch (Exception e) {
            e.printStackTrace();
        }
        
        // Create and show the application on the Event Dispatch Thread
        SwingUtilities.invokeLater(() -> {
            new hw1().setVisible(true);
        });
    }
}

/**
 * @brief StylusPath: freehand drawing shape.
 */
class StylusPath extends Shape {
    /** List of points in the path. */
    private java.util.List<Point> points;
    /** Stroke width for the path. */
    protected int strokeWidth;
    /** Margin for stylus path hit-testing. */
    private static final int STYLUS_MARGIN = 5;
    /**
     * @brief Get list of points in the path.
     * @return List of points
     */
    public java.util.List<Point> getPoints() { return points; }
    /**
     * @brief Constructor for StylusPath.
     * @param color Path color
     * @param strokeWidth Path thickness
     */
    public StylusPath(Color color, int strokeWidth) {
        super(0, 0, color);
        points = new java.util.ArrayList<>();
        this.strokeWidth = strokeWidth;
    }

    /**
     * @brief Add a point to the path.
     * @param x X coordinate
     * @param y Y coordinate
     */
    public void addPoint(int x, int y) {
        points.add(new Point(x, y));
    }

    /**
     * @brief Draw the stylus path.
     * @param g2d Graphics2D context
     */
    @Override
    public void draw(Graphics2D g2d) {
        if (points.size() < 2) return;
        g2d.setColor(color);
        g2d.setStroke(selected
            ? new BasicStroke(strokeWidth + 2, BasicStroke.CAP_ROUND, BasicStroke.JOIN_ROUND)
            : new BasicStroke(strokeWidth, BasicStroke.CAP_ROUND, BasicStroke.JOIN_ROUND));
        for (int i = 1; i < points.size(); i++) {
            Point p1 = points.get(i - 1);
            Point p2 = points.get(i);
            g2d.drawLine(p1.x, p1.y, p2.x, p2.y);
        }
    }

    /**
     * @brief Check if (x, y) is near any segment of the path.
     * @param x X coordinate
     * @param y Y coordinate
     * @return True if near any segment
     */
    @Override
    public boolean contains(int x, int y) {
        // Check if (x, y) is near any segment
        for (int i = 1; i < points.size(); i++) {
            Point p1 = points.get(i - 1);
            Point p2 = points.get(i);
            double dist = Line2D.ptSegDist(p1.x, p1.y, p2.x, p2.y, x, y);
            if (dist <= Math.max(STYLUS_MARGIN, strokeWidth / 2)) return true;
        }
        return false;
    }

    /**
     * @brief Helper for point-to-segment distance.
     * @param x1 Segment start X
     * @param y1 Segment start Y
     * @param x2 Segment end X
     * @param y2 Segment end Y
     * @param px Point X
     * @param py Point Y
     * @return Distance from point to segment
     */
    private double ptSegDist(int x1, int y1, int x2, int y2, int px, int py) {
        double dx = x2 - x1;
        double dy = y2 - y1;
        if (dx == 0 && dy == 0) {
            dx = px - x1;
            dy = py - y1;
            return Math.sqrt(dx * dx + dy * dy);
        }
        double t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy);
        t = Math.max(0, Math.min(1, t));
        double projX = x1 + t * dx;
        double projY = y1 + t * dy;
        dx = px - projX;
        dy = py - projY;
        return Math.sqrt(dx * dx + dy * dy);
    }

    /**
     * @brief Move the stylus path.
     * @param deltaX Change in X
     * @param deltaY Change in Y
     */
    @Override
    public void move(int deltaX, int deltaY) {
        for (Point p : points) {
            p.x += deltaX;
            p.y += deltaY;
        }
    }
}

/**
 * @brief EraserPath: freehand erasing shape (draws in background color, always circular stroke)
 */
class EraserPath extends StylusPath {
    public EraserPath(int strokeWidth) {
        // Always use white (background color)
        super(Color.WHITE, strokeWidth);
    }
    @Override
    public void draw(Graphics2D g2d) {
        if (getPoints().size() < 2) return;
        g2d.setColor(Color.WHITE);
        g2d.setStroke(new BasicStroke(super.strokeWidth, BasicStroke.CAP_ROUND, BasicStroke.JOIN_ROUND));
        for (int i = 1; i < getPoints().size(); i++) {
            Point p1 = getPoints().get(i - 1);
            Point p2 = getPoints().get(i);
            g2d.drawLine(p1.x, p1.y, p2.x, p2.y);
        }
    }
}