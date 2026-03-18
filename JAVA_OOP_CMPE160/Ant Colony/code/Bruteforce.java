import java.awt.*;
import java.io.File;
import java.io.FileNotFoundException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Scanner;
/**
 * Class implementing a brute force approach to solve the Migros Delivery problem.
 * This class computes the shortest route by evaluating all permutations of locations.
 */
public class Bruteforce {
    private static final double INFINITE = Double.MAX_VALUE;// Represents an infinite distance.
    private static double minDistance = INFINITE;// Store the minimum distance found.
    private static Integer[] shortestRoute = null;// Store the shortest route found.
    /**
     * Constructs a BruteForce instance, processes locations, and finds the shortest path.
     * @param file The file containing locations data.
     * @throws FileNotFoundException If the file cannot be found.
     */
    public Bruteforce(File file) throws FileNotFoundException {
        double startTime = System.currentTimeMillis();
        List<Location> locations = loadLocations(file);
        if (locations.size() <= 1) {return;}
        Integer[] initialRoute = new Integer[locations.size()];
        for (int i = 0; i < locations.size(); i++) {
            initialRoute[i] = i;
        }
        permuteAndEvaluate(initialRoute, 1, (ArrayList<Location>) locations);
        if (shortestRoute != null) {
            printResult(shortestRoute);
            visualizeRoute((ArrayList<Location>) locations, shortestRoute,minDistance, locations.getFirst());
        }
        double endTime = System.currentTimeMillis();
        double duration = (endTime - startTime)/1000;
        System.out.println("Time it takes to find shortest path: " + duration + " seconds");
    }
    /**
     * Loads location data from a file.
     * @param file The file to read.
     * @return A list of Location objects.
     * @throws FileNotFoundException If the file is not found.
     */
    private static List<Location> loadLocations(File file) throws FileNotFoundException {
        List<Location> locations = new ArrayList<>();
        Scanner scanner = new Scanner(file);
        int id = 1;
        while (scanner.hasNextLine()) {
            String line = scanner.nextLine();
            String[] parts = line.split(",");
            double x = Double.parseDouble(parts[0]);
            double y = Double.parseDouble(parts[1]);
            locations.add(new Location(id++, x, y));
        }
        scanner.close();
        return locations;
    }
    /**
     * Recursively generates permutations of route indices and evaluates each route.
     * @param arr Array of indices representing locations.
     * @param k The starting index of permutations.
     * @param locations List of locations corresponding to indices.
     */
    private static void permuteAndEvaluate(Integer[] arr, int k, ArrayList<Location> locations) {
        if (k == arr.length - 1) {
            evaluateRoute(arr, locations);
        } else {
            for (int i = k; i < arr.length; i++) {
                swap(arr, k, i);
                permuteAndEvaluate(arr, k + 1, locations);
                swap(arr, k, i);
            }
        }
    }
    /**
     * Evaluates the distance of a given route configuration.
     * @param route Array of indices representing a route.
     * @param locations List of locations corresponding to indices.
     */
    private static void evaluateRoute(Integer[] route, List<Location> locations) {
        double distance = calculateRouteDistance(route, locations);
        if (distance < minDistance) {
            minDistance = distance;
            shortestRoute = new Integer[route.length + 1];
            System.arraycopy(route, 0, shortestRoute, 0, route.length);
            shortestRoute[route.length] = route[0];
        }
    }
    /**
     * Calculates the total distance of a route.
     * @param route Array of indices representing a route.
     * @param locations List of locations.
     * @return The total distance of the route.
     */
    private static double calculateRouteDistance(Integer[] route, List<Location> locations) {
        double distance = 0;
        int prevIdx = route[0];
        for (int i = 1; i < route.length; i++) {
            distance += calculatePointDistance(locations.get(prevIdx), locations.get(route[i]));
            prevIdx = route[i];
        }
        distance += calculatePointDistance(locations.get(prevIdx), locations.get(route[0]));
        return distance;
    }
    /**
     * Calculates the Euclidean distance between two points.
     * @param point1 The first location.
     * @param point2 The second location.
     * @return The distance between the two points.
     */
    private static double calculatePointDistance(Location point1, Location point2) {
        return Math.sqrt(Math.pow(point2.X_Coordinate() - point1.X_Coordinate(), 2) +
                Math.pow(point2.Y_Coordinate() - point1.Y_Coordinate(), 2));
    }
    /**
     * Swaps two elements in an array.
     * @param arr The array containing elements to swap.
     * @param a The index of the first element.
     * @param b The index of the second element.
     */
    private static void swap(Integer[] arr, int a, int b) {
        int temp = arr[a];
        arr[a] = arr[b];
        arr[b] = temp;
    }
    /**
     * Prints the results of the brute force calculation.
     * @param bestRoute The best route found.
     */
    private static void printResult( Integer[] bestRoute) {
        System.out.println("Method: Brute-force Method");
        System.out.println("Shortest Distance: " + String.format("%.5f", minDistance));
        System.out.println("Shortest Path: " + Arrays.toString(Arrays.stream(bestRoute).map(i -> i + 1).toArray()));
    }
    /**
     * Visualizes the shortest route using StdDraw.
     * @param locations List of all locations.
     * @param bestRoute Array of indices representing the best route.
     * @param minDistance The minimum distance of the best route.
     * @param firstLocation The starting location of the route for visualization purposes.
     */
    private static void visualizeRoute(ArrayList<Location> locations, Integer[] bestRoute, double minDistance, Location firstLocation) {
        int canvasWidth = 800;
        int canvasHeight = 800;
        StdDraw.setCanvasSize(canvasWidth, canvasHeight);
        StdDraw.setXscale(0, 1);
        StdDraw.setYscale(0, 1);
        double circleRadius = 0.02;
        StdDraw.clear(StdDraw.WHITE);
        StdDraw.setPenColor(StdDraw.BLACK);
        StdDraw.setFont(new Font("Serif", Font.BOLD, 14));
        StdDraw.setPenColor(StdDraw.BLACK);
        StdDraw.setPenRadius(0.005);
        double locationX = firstLocation.X_Coordinate();
        double locationY = firstLocation.Y_Coordinate();
        for (int idx : bestRoute) {
            Location nextLocation = locations.get(idx);
            double nextLocationX = nextLocation.X_Coordinate();
            double nextLocationY = nextLocation.Y_Coordinate();
            StdDraw.line(locationX, locationY, nextLocationX, nextLocationY);
            locationX = nextLocationX;
            locationY = nextLocationY;
        }
        StdDraw.line(locationX, locationY, firstLocation.X_Coordinate(), firstLocation.Y_Coordinate());
        for (int i = 0; i < locations.size(); i++) {
            Location location = locations.get(i);
            if (i == 0) {
                StdDraw.setPenColor(StdDraw.PRINCETON_ORANGE);
            } else {
                StdDraw.setPenColor(StdDraw.LIGHT_GRAY);
            }
            StdDraw.filledCircle(location.X_Coordinate(), location.Y_Coordinate(), circleRadius);
            StdDraw.setPenColor(StdDraw.BLACK);
            StdDraw.text(location.X_Coordinate(), location.Y_Coordinate(), Integer.toString(location.ID()));
        }
        StdDraw.show();
    }
}