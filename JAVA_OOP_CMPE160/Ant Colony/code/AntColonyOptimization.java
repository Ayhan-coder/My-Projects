import java.awt.*;
import java.io.File;
import java.io.FileNotFoundException;
import java.util.List;
import java.util.*;
/**
 * Class implementing an Ant Colony Optimization algorithm for solving the Migros Delivery Problem.
 */
public class AntColonyOptimization {
    // Hyperparameters used in the Ant Colony Optimization algorithm
    private static final int ITERATION = 100; // Number of iterations to run the algorithm
    private static final int NUM_ANTS = 50;// Number of ants used per iteration
    private static final double DECAY_RATE = 0.5;// Rate at which pheromones decay each iteration
    private static final double ALPHA = 0.8;// Exponent for pheromone importance
    private static final double BETA = 1.5;// Exponent for heuristic distance
    private static final double INITIAL_PHEROMONE_INTENSITY = 0.01;// Initial pheromone level on paths
    private static final double Q_VALUE = 0.0001;// Pheromone deposit factor
    private final ArrayList<int[]> shortestRoutes = new ArrayList<>();// Stores the shortest routes found during each iteration.
    private final List<Location> locations;// List of locations that ants need to visit.
    private double[][] distances;// Matrix representing the distances between each pair of locations.
    private double[][] pheromones;// Matrix holding the amount of pheromone on each path between locations.
    private final boolean VISUALIZE_ONLY_SHORTEST_DISTANCE = false;// Switch for visualizing best routes in each iteration (False) or only shortest route after all iterations (True).
    /**
     * Reads location data from a file into a List of Location objects.
     * @param file The file containing locations data.
     * @return A List of Location objects.
     * @throws FileNotFoundException If the file cannot be found.
     */
    private static List<Location> readLocations(File file) throws FileNotFoundException {
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
     * Constructor for AntColonyOptimization. Initializes pheromones and simulates ant movement.
     * @param file The file to read locations from.
     * @throws FileNotFoundException If the file is not found.
     */
    public AntColonyOptimization(File file) throws FileNotFoundException {
        this.locations = readLocations(file);
        if (locations.size() <= 1) {return;}
        initializePheromones();
        simulateAnts();
    }
    /**
     * Initializes the pheromone matrix and distances between locations.
     */
    private void initializePheromones() {
        int numLocations = locations.size();
        pheromones = new double[numLocations][numLocations];
        distances = new double[numLocations][numLocations];
        for (int i = 0; i < numLocations; i++) {
            for (int j = 0; j < numLocations; j++) {
                distances[i][j] = calculateDistance(locations.get(i), locations.get(j));
                pheromones[i][j] = INITIAL_PHEROMONE_INTENSITY;
            }
        }
    }
    /**
     * Simulates the movement of ants to find the shortest routes.
     */
    private void simulateAnts() {
        double bestDistance = Double.MAX_VALUE;
        int[] bestRoute = null;
        double startTime = System.currentTimeMillis();
        for (int iteration = 0; iteration < ITERATION; iteration++) {
            for (int ant = 0; ant < NUM_ANTS; ant++) {
                int[] route = buildRoute();
                double distance = calculateRouteDistance(route);
                if (distance < bestDistance) {
                    bestDistance = distance;
                    bestRoute = route.clone();
                }
                updatePheromones(route, distance);
            }
            decayPheromones();
            shortestRoutes.add(bestRoute);
        }
        if (VISUALIZE_ONLY_SHORTEST_DISTANCE) {
            if (bestRoute != null) {
                visualizeOnlyBestRoute(locations, bestRoute);
            }
        } else {
            visualizeRoute(locations);
        }
        double endTime = System.currentTimeMillis();
        double duration = (endTime - startTime)/1000;
        printResults(bestDistance, bestRoute, duration);
    }
    /**
     * Constructs a route for an ant based on the pheromone and distance matrices.
     * @return An array of integers representing the route taken.
     */
    private int[] buildRoute() {
        int numLocations = locations.size();
        int[] route = new int[numLocations + 1];
        List<Integer> remainingLocations = new ArrayList<>();
        for (int i = 0; i < numLocations; i++) {
            remainingLocations.add(i);
        }
        route[0] = 0;
        remainingLocations.remove(Integer.valueOf(0));
        int currentIndex = 1;
        while (!remainingLocations.isEmpty()) {
            int currentLocation = route[currentIndex - 1];
            double[] probabilities = new double[numLocations];
            double totalProbability = 0;
            for (int nextLocation : remainingLocations) {
                double pheromone = pheromones[currentLocation][nextLocation];
                double edgeValue = Math.pow(pheromone, ALPHA) * Math.pow(1.0 / distances[currentLocation][nextLocation], BETA);
                probabilities[nextLocation] = edgeValue;
                totalProbability += edgeValue;
            }
            double r = Math.random() * totalProbability;
            double cumulativeProbability = 0;
            for (int nextLocation : remainingLocations) {
                cumulativeProbability += probabilities[nextLocation];
                if (cumulativeProbability >= r) {
                    route[currentIndex] = nextLocation;
                    remainingLocations.remove(Integer.valueOf(nextLocation));
                    currentIndex++;
                    break;
                }
            }
        }
        route[numLocations] = 0;
        return route;
    }
    /**
     * Updates the pheromone levels along a given route based on the distance of the route.
     * @param route The route taken by the ant.
     * @param totalCycleDistance The total distance of the route.
     */
    private void updatePheromones(int[] route, double totalCycleDistance) {
        double delta = Q_VALUE / totalCycleDistance;
        for (int i = 0; i < route.length - 1; i++) {
            int start = route[i];
            int end = route[i + 1];
            pheromones[start][end] += delta;
            pheromones[end][start] += delta;
        }
    }
    /**
     * Applies decay to the pheromone levels across all paths.
     */
    private void decayPheromones() {
        for (int i = 0; i < pheromones.length; i++) {
            for (int j = 0; j < pheromones[i].length; j++) {
                pheromones[i][j] *= DECAY_RATE;
            }
        }
    }
    /**
     * Calculates the total distance of a given route.
     * @param route The route to measure.
     * @return The total distance of the route.
     */
    private double calculateRouteDistance(int[] route) {
        double totalDistance = 0;
        for (int i = 0; i < route.length - 1; i++) {
            totalDistance += distances[route[i]][route[i + 1]];
        }
        return totalDistance;
    }
    /**
     * Calculates the Euclidean distance between two points.
     * @param point1 The first location.
     * @param point2 The second location.
     * @return The distance between the two points.
     */
    private static double calculateDistance(Location point1, Location point2) {
        double dx = point2.X_Coordinate() - point1.X_Coordinate();
        double dy = point2.Y_Coordinate() - point1.Y_Coordinate();
        return Math.sqrt(dx * dx + dy * dy);
    }
    /**
     * Converts a route array into a readable string format.
     * @param route The route to convert.
     * @return A string representation of the route.
     */
    private String routeToString(int[] route) {
        return Arrays.toString(Arrays.stream(route).map(i -> i + 1).toArray());
    }
    /**
     * Prints the results of the ant colony optimization.
     * @param shortestDistance The shortest distance found.
     * @param bestRoute The best route found.
     * @param duration The duration of the simulation.
     */
    private void printResults(double shortestDistance, int[] bestRoute, double duration) {
        System.out.println("Method: Ant Colony Algorithm");
        System.out.println("Shortest Distance: " + String.format("%.5f",shortestDistance));
        System.out.println("Shortest Path: " + routeToString(bestRoute));
        System.out.println("Time it takes to find the shortest path: " + duration + " seconds");
    }
    /**
     * Visualizes all routes found by the algorithm.
     * @param locations The locations involved in the routes.
     */
    private void visualizeRoute(List<Location> locations) {
        int canvasWidth = 800;
        int canvasHeight = 800;
        StdDraw.setCanvasSize(canvasWidth, canvasHeight);
        StdDraw.setXscale(0, 1);
        StdDraw.setYscale(0, 1);
        double circleRadius = 0.02;
        StdDraw.clear(StdDraw.WHITE);
        StdDraw.setPenColor(StdDraw.BLACK);
        StdDraw.setFont(new Font("Serif", Font.BOLD, 14));
        for (int i = 0; i < shortestRoutes.size(); i++) {
            int[] bestRoute = shortestRoutes.get(i);
            double thickness = 0.0001 * (i + 1);
            StdDraw.setPenRadius(thickness);
            for (int j = 0; j < bestRoute.length - 1; j++) {
                Location currentLocation = locations.get(bestRoute[j]);
                Location nextLocation = locations.get(bestRoute[j + 1]);
                StdDraw.line(currentLocation.X_Coordinate(), currentLocation.Y_Coordinate(), nextLocation.X_Coordinate(), nextLocation.Y_Coordinate());
            }
        }
        for (Location location : locations) {
            StdDraw.setPenColor(StdDraw.LIGHT_GRAY);
            StdDraw.filledCircle(location.X_Coordinate(), location.Y_Coordinate(), circleRadius);
            StdDraw.setPenColor(StdDraw.BLACK);
            StdDraw.text(location.X_Coordinate(), location.Y_Coordinate(), Integer.toString(location.ID()));
        }
        StdDraw.show();
    }
    /**
     * Visualizes only the shortest route found by the algorithm.
     * @param locations The locations involved in the route.
     * @param bestRoute The best route found.
     */
    private void visualizeOnlyBestRoute(List<Location> locations, int[] bestRoute) {
        StdDraw.setCanvasSize(800, 800);
        StdDraw.setXscale(0, 1);
        StdDraw.setYscale(0, 1);
        StdDraw.clear(StdDraw.WHITE);
        StdDraw.setPenColor(StdDraw.BLACK);
        StdDraw.setFont(new Font("Serif", Font.BOLD, 14));
        StdDraw.setPenRadius(0.005);
        for (int i = 0; i < bestRoute.length - 1; i++) {
            Location start = locations.get(bestRoute[i]);
            Location end = locations.get(bestRoute[i + 1]);
            StdDraw.line(start.X_Coordinate(), start.Y_Coordinate(), end.X_Coordinate(), end.Y_Coordinate());
        }
        for (Location location : locations) {
            StdDraw.setPenColor(StdDraw.LIGHT_GRAY);
            StdDraw.filledCircle(location.X_Coordinate(), location.Y_Coordinate(), 0.02);
            StdDraw.setPenColor(StdDraw.BLACK);
            StdDraw.text(location.X_Coordinate(), location.Y_Coordinate(), String.valueOf(location.ID()));
        }
        StdDraw.show();
    }
}