import java.awt.*;
import java.awt.event.KeyEvent;
/*
 * @author Ali Ayhan Gunder
 * @since 20.03.2024
 * The main class for the Angry Bullet game.
 * This class manages the game loop, initializes game objects and variables,
 * and handles user input to control the cannon and bullet.
 */
/*
 * The main method of the application.
 * This method sets up the game environment, initializes variables,
 * and starts the main game loop.
 */
public class AliAyhanGunder {
    public static void main(String[] args) {
        int width = 1600; //Canvas width
        int height = 800;// Canvas height
        double gravity = 9.8;// Gravitational acceleration
        int pauseDuration = 10;
        double x0 = 120.0;// Bullet's shooting X_position
        double y0 = 120.0; // Bullet's shooting Y_position
        double bulletVelocity = 180;// Variable bullet velocity
        int status = 0;// if win 1, if lose -1 else 0.
        final double initialBulletVelocity = 180; // Initial bullet velocity
        int bullet_size = 3;
        double bulletAngle = 45.0; //Cannons tangent
        final double initialBulletAngle = 45.0;// Initial constant to reset
        double startTime; // First time = 0, when bullet fired
        int keyboardPauseDuration = 20;// Pause duration for keyboard
        double cannonLength = 60;// Variable cannon length
        double initialCannonLength = 60;// Initial cannon length
        double[][] obstacleArray = { // ... obstacle data ...
                {1200, 0, 60, 220},
                {1000, 0, 60, 160},
                {600, 0, 60, 80},
                {600, 180, 60, 160},
                {220, 0, 120, 180}
                //My obstacle arrays
                /*{1200, 0, 60, 220},
                {1000, 0, 60, 160},
                {600, 0, 60, 80},
                {220, 0, 120, 180},
                {800, 300, 100, 50},
                {275, 400, 80, 120},
                {1300, 200, 50, 100},
                {900, 500, 150, 40},
                {500, 100, 40, 200},
                {1100, 100, 40, 200}*/
        };
        double[][] targetArray = { // ... target data ...
                {1160, 0, 30, 30},
                {730, 0, 30, 30},
                {150, 0, 20, 20},
                {1480, 0, 60, 60},
                {340, 80, 60, 30},
                {1500, 600, 60, 60}
                //My target arrays
                /*{900, 0, 30, 30},
                {850, 0, 30, 30},
                {1480, 0, 60, 60},
                {340, 200, 60, 30},
                {1500, 600, 60, 60},
                {550, 700, 50, 50},
                {1150, 150, 50, 50},
                {850, 350, 25, 25},
                {450, 450, 30, 30},
                {970, 480, 20, 20}*/
        };
        boolean isBulletFired = false; // Checks is bullet fired
        StdDraw.setCanvasSize(width, height);
        StdDraw.setXscale(0, 1600);// Sets X scale
        StdDraw.setYscale(0, 800);// Sets Y scale
        StdDraw.clear(Color.white);// Paints background white
        StdDraw.enableDoubleBuffering();// EnableDoubleBuffering for faster animations
        /*
         * Fires the bullet and simulates its movement.
         * @param x0 initial x-coordinate of the bullet
         * @param y0 initial y-coordinate of the bullet
         * @param gravity gravitational acceleration
         * @param vx initial x-velocity of the bullet
         * @param vy initial y-velocity of the bullet
         * @param bullet_size size of the bullet
         * @param pauseDuration time between each frame update
         * @param startTime starting time of the bullet's movement
         * @param cannonX x-coordinate of the cannon
         * @param cannonY y-coordinate of the cannon
         * @param targetArray array containing target data
         * @param obstacleArray array containing obstacle data
         * @return game status (0: ongoing, 1: win, -1: hit obstacle, -2: hit ground, -3: max X reached)
         */
        while (true) { //Main while loop
            if (isBulletFired){// Checks is bullet fired
                startTime = System.currentTimeMillis() / 200.0;// Sets starting time when bullet fired
                double vx = bulletVelocity/1.72 * Math.cos(bulletAngle/180*Math.PI);// Calculates the horizontal velocity, I added scaling for more appropriate result
                double vy = bulletVelocity/1.72 * Math.sin(bulletAngle/180*Math.PI);// Calculates the vertical velocity
                status = fireBullet( x0,  y0, gravity, vx,  vy ,  bullet_size,  pauseDuration, startTime,x0,y0, targetArray,obstacleArray);// Equals status to returned value from method
                isBulletFired = false;// Checks is bullet fired
            }
            if (status == 0){// If game in initial state
                double cannonEndX = x0 + (cannonLength * Math.cos(bulletAngle/180*Math.PI));// Calculates the end point of cannon as x-coordinates
                double cannonEndY = y0 + (cannonLength * Math.sin(bulletAngle/180*Math.PI));// Calculates the end point of cannon as y-coordinates
                StdDraw.clear(StdDraw.WHITE);// Clears past frames , when bullet is not fired.
                drawObstacles(obstacleArray);// Method that draws all obstacles
                drawTargets(targetArray);// Method that draws all target
                drawCannon(x0, y0, cannonEndX, cannonEndY);// Method that draws cannon's different directions
                StdDraw.setPenColor(Color.white);
                drawInfo(bulletVelocity,bulletAngle);// Method that draws velocity and cannon angle
            }
            if (status == 1){// If you win the game
                StdDraw.setPenColor(Color.black);
                StdDraw.setFont(new Font("Helvetica", Font.BOLD,18));// Sets text font
                StdDraw.text(160,775,"Congratulations: You hit the target!");// Draws the message
            } else {
                if (status == -1) {// If you hit the obstacle
                    StdDraw.setPenColor(Color.black);
                    StdDraw.setFont(new Font("Helvetica", Font.BOLD,18));// Sets text font
                    StdDraw.text(200, 775, "Hit an obstacle. Press 'r' to shoot again.");// Draws the message
                }
                if (status == -2) {//If you hit the ground
                    StdDraw.setPenColor(Color.black);
                    StdDraw.setFont(new Font("Helvetica", Font.BOLD,18));// Sets text font
                    StdDraw.text(200, 775, "Hit the ground. Press 'r' to shoot again.");// Draws the message
                }
                if (status == -3) {//If you exceed max X distance
                    StdDraw.setPenColor(Color.black);
                    StdDraw.setFont(new Font("Helvetica", Font.BOLD,18));// Sets text font
                    StdDraw.text(200, 775, "Max X reached. Press 'r' to shoot again.");// Draws the message
                }
            }
            /*
             * Handles key presses for controlling the cannon and bullet.
             */
            if (StdDraw.isKeyPressed(KeyEvent.VK_LEFT) && status == 0) {// When left key pressed
                StdDraw.pause(keyboardPauseDuration);
                cannonLength --;// Decreases cannon length
                bulletVelocity --;// Decreases bullet velocity
            }
            if (StdDraw.isKeyPressed(KeyEvent.VK_RIGHT) && status == 0) {// When right key pressed
                StdDraw.pause(keyboardPauseDuration);
                cannonLength ++;// Increases cannon length
                bulletVelocity ++;// Increases cannon length
            }
            if (StdDraw.isKeyPressed(KeyEvent.VK_UP) && status == 0) {// When up key pressed
                StdDraw.pause(keyboardPauseDuration);
                bulletAngle ++;// Increases bullet angle
            }
            if (StdDraw.isKeyPressed(KeyEvent.VK_DOWN) && status == 0) {// When down key pressed
                StdDraw.pause(keyboardPauseDuration);
                bulletAngle --;// Decreases bullet angle
            }
            if (StdDraw.isKeyPressed(KeyEvent.VK_R)) {// When key R pressed
                StdDraw.pause(keyboardPauseDuration);
                isBulletFired = false;// Resets isBulletFired
                StdDraw.clear(Color.white);// Clears screen
                cannonLength = initialCannonLength;// Resets cannon length
                bulletVelocity = initialBulletVelocity;// Resets bullet velocity
                bulletAngle = initialBulletAngle;// Resets cannon and bullet angle
                status = 0;// Sets status its initial condition
            }
            if (StdDraw.isKeyPressed(KeyEvent.VK_SPACE)) {// When space key pressed
                StdDraw.pause(keyboardPauseDuration);
                isBulletFired = true;// Fires bullet
            }
            StdDraw.show();// Draws events
            StdDraw.pause(pauseDuration);// Pauses Screen
        }
    }
    /*
     * Draws information about bullet velocity and angle on the screen.
     * @param bulletVelocity current bullet velocity
     * @param bulletAngle current bullet angle
     */
    public static void drawInfo(double bulletVelocity, double bulletAngle){
        StdDraw.setPenColor(StdDraw.WHITE);
        StdDraw.setFont(new Font("Helvetica", Font.BOLD,18));
        String bulletVelocityText = String.format("v: %.1f",bulletVelocity);
        String bulletAngleText = String.format("a: %.1f",bulletAngle);
        StdDraw.text(56,60,bulletAngleText);// Draws bullet angle info
        StdDraw.text(60,40,bulletVelocityText);// Draws bullet velocity info
    }
    /**
     * Draws all obstacles on the game canvas.
     * @param obstacleArray array containing obstacle data
     */
    public static void drawObstacles(double[][] obstacleArray) {
        for (double[] obstacle : obstacleArray) {
            double x = obstacle[0];
            double y = obstacle[1];
            double w = obstacle[2];
            double h = obstacle[3];
            StdDraw.setPenColor(StdDraw.DARK_GRAY);
            StdDraw.filledRectangle(x + w / 2, y + h / 2, w / 2, h / 2);
        }
        StdDraw.setPenColor(StdDraw.BLACK);
        StdDraw.filledSquare(60, 60, 60);
        StdDraw.setPenColor(StdDraw.BLACK);
    }
    /**
     * Draws all targets on the game canvas.
     * @param targetArray array containing target data
     */
    public static void drawTargets(double[][] targetArray) {
        for (double[] target : targetArray) {
            double x = target[0];
            double y = target[1];
            double w = target[2];
            double h = target[3];
            StdDraw.setPenColor(StdDraw.PRINCETON_ORANGE);
            StdDraw.filledRectangle(x + w / 2, y + h / 2, w / 2, h / 2);
        }
    }
    /**
     * Draws the cannon in its current position and direction.
     */
    public static void drawCannon(double startX, double startY, double endX, double endY) {
        StdDraw.setPenColor(StdDraw.BLACK);
        StdDraw.setPenRadius(0.008);
        StdDraw.line(startX, startY, endX, endY);
    }
    /*
     * Simulates the bullet's movement and checks for collisions.
     * @param startX initial x-coordinate of the bullet
     * @param startY initial y-coordinate of the bullet
     * @param gravity gravitational acceleration
     * @param vx initial x-velocity of the bullet
     * @param vy initial y-velocity of the bullet
     * @param bullet_size size of the bullet
     * @param pauseDuration time between each frame update
     * @param startTime starting time of the bullet's movement
     * @param x current x-coordinate of the cannon (used for line drawing)
     * @param y current y-coordinate of the cannon (used for line drawing)
     * @param targetArray array containing target data
     * @param obstacleArray array containing obstacle data
     * @return game status (0: ongoing, 1: hit target, -1: hit obstacle, -2: hit ground, -3: max X reached)
     */
    public static int fireBullet(double startX, double startY, double gravity, double vx, double vy , int bullet_size, int pauseDuration, double startTime, double x, double y, double[][] targetArray, double[][] obstacleArray) {
        int status = 0;// Sets status to its initial condition
        boolean collision = false;// Checks bullets collision status
        while (!collision) {// Loop continues until bullet collide obstacle or target or exceed maximum distance
            if (StdDraw.isKeyPressed(KeyEvent.VK_R)){// Breaks the loop when R key pressed
                break;
            }
            double oldX = x;// Stores the previous x value
            double oldY = y;// Stores the prevıous y value
            double time = System.currentTimeMillis() / 200.0 - startTime;// Calculates time
            x = startX + (vx * time); // Calculates x position
            y = startY + (vy * time) - ((gravity * time * time) / 2.0);// Calculates y position
            StdDraw.setPenColor(StdDraw.BLACK);
            StdDraw.filledCircle(x, y, bullet_size);// Draws the bullet
            if (x != startX && y != startY) {// Prevents drawing line in first position
                StdDraw.setPenRadius(0.003);// Sets thickness of line
                StdDraw.line(oldX,oldY,x,y);// Draws the line
            }
            for (double[] target : targetArray) {// Checks if bullet hit to target
                double tx = target[0];
                double ty = target[1];
                double tw = (target[2]);
                double th= (target[3]);
                if ( tx <= x && x <= ( tx + tw ) && ty  <= y && y <= ( ty + th )){
                    collision = true;
                    status = 1;
                }
            }
            if ( y < 0 || x > 1600 || status != 0) {// Checks if bullet exceed maximum x distance or hit to ground
                if (y<0) {
                    status = -2;
                    collision = true;
                } else if (x > 1600) {
                    status = -3;
                    collision =true;
                }
            }
            for (double[] obstacle : obstacleArray) {// Checks if bullet hit to obstacle
                double ox = obstacle[0];
                double oy = obstacle[1];
                double ow = (obstacle[2]);
                double oh = (obstacle[3]);
                if ( ox  <= x && x <= (ox + ow ) && oy  <= y && y <= (oy + oh )){
                    collision = true;
                    status = -1;
                }
            }
            StdDraw.show();
            StdDraw.pause(pauseDuration);
        }
        return status;
    }
}
