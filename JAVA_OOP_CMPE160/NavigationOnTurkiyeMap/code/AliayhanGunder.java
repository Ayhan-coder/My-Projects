import java.awt.*;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.util.ArrayList;
import java.util.Scanner;

/**
 * @author ali ayhan gunder
 * @since 2024-04-05
 * This class is the main class of the project.
 * It reads city data from text files and allows users to find a path between two cities.
 */
public class AliayhanGunder {
    public static void main(String[] args){
        int numberOfConnections = 0;//Stores the number of lines connections text
        int numberOfCities = 0;//Stores the number of lines coordinates text
        String startCity;//Stores the starting city entered by the user.
        String destinationCity;//Stores the destination city entered by the user.
        String cityCoordinatesTxt = "C:\\Users\\gunde\\IdeaProjects\\Homework 2\\src\\city_coordinates.txt";
        //File path for the text file containing city coordinates.
        String cityConnectionsTxt = "C:\\Users\\gunde\\IdeaProjects\\Homework 2\\src\\city_connections.txt";
        //File path for the text file containing city connections.
        ArrayList<String> bluePath;//An ArrayList stores the path between cities.
            File file1 = new File(cityCoordinatesTxt);//Read the cities information from the city coordinates file.
        Scanner scanner;// Initialize a scanner
        try {
            scanner = new Scanner(file1);
        } catch (FileNotFoundException e) {
            throw new RuntimeException(e);//Throws exception when scanner is null
        }
        int rowNumbers = 0;
            while (scanner.hasNextLine()){scanner.nextLine();rowNumbers ++;}
            numberOfCities += rowNumbers;//Counts cities from the file
            scanner.close();

            File file2 = new File(cityConnectionsTxt);//Read the connection information from the city coordinates file.
        Scanner scanner2;// Initialize a scanner
        try {
            scanner2 = new Scanner(file2);
        } catch (FileNotFoundException e) {
            throw new RuntimeException(e);//Throws exception when scanner is null
        }
        int rowNumbers2 = 0;
            while (scanner2.hasNextLine()){
                scanner2.nextLine();
                rowNumbers2 ++;
            }
            numberOfConnections += rowNumbers2;//Counts connections from the file
            scanner.close();

            City[] cities = new City[numberOfCities];
        Scanner scanner3;// Initialize a scanner
        try {
            scanner3 = new Scanner(new FileInputStream(cityCoordinatesTxt));//Reads city data from coordinates file
        } catch (FileNotFoundException e) {
            throw new RuntimeException(e); //Throws exception when scanner is null
        }
        for (int i =0; i < numberOfCities; i++){
                String line = scanner3.nextLine();// Read the current line from the city coordinates file
                String[] lineSplit = line.split(", ");//Split the line by commas to get an array of city names and coordinates
                cities[i] = new City();// Initialize a new city object
                cities[i].setCityName(lineSplit[0]);// Sets city name
                cities[i].setX(Integer.parseInt(lineSplit[1]));// Sets X-coordinates
                cities[i].setY(Integer.parseInt(lineSplit[2]));// Sets Y-coordinates
        }

        Scanner scanner4;// Initialize a scanner
        try {
            scanner4 = new Scanner(new FileInputStream(cityConnectionsTxt));//Reads connections data from connections file
        } catch (FileNotFoundException e) {
            throw new RuntimeException(e);// Throws exception when scanner is null
        }
        for (int i =0; i < numberOfConnections; i++){
                String line = scanner4.nextLine();// Read the current line from the city connection file
                String[] lineSplit = line.split(",");//Split the line by (",") to get an array of connections
                City currentCity = null;// Initialize a variable to store the current City object
                for (City city : cities) {
                    if (city.getCityName().equals(lineSplit[0])) {currentCity = city;break;}}// Check if the current city's name matches
                if (currentCity != null) {
                    for (int j = 1; j < lineSplit.length; j++) {
                        currentCity.getConnectionsList().add(lineSplit[j]);// Add the connection to the current city's connections list
                        City.findCityByName(cities, lineSplit[j]).getConnectionsList().add(lineSplit[0]); // Add the connection to the other city's connections list
                    }
                }
            }
        ArrayList<City> citiesList = new ArrayList<>();// Create an arrayList to store of City objects
        for (City city : cities) {
            citiesList.add(city);// Adds all city objects to citiesList
        }
        while (true) {
            Scanner input = new Scanner(System.in);// Initialize a scanner to get user input
            System.out.println("Enter starting city: ");
            /*
             * I made user input case sensitive.
             */
            startCity = input.next();
            startCity = startCity.toLowerCase();
            String s1 = String.valueOf(startCity.charAt(0)).toUpperCase();
            String startCityCapitalized = s1 + startCity.substring(1);
            startCity = startCityCapitalized;
            if (!citiesList.contains(City.findCityByName(cities, startCity))) {// Check if the starting city exists in the original cities array
                System.out.println("City named '" + startCity + "' not found. Please enter a valid city name.");
            } else {
                while (true) {
                    System.out.println("Enter the destination city: ");
                    /*
                     * I made user input case sensitive.
                     */
                    destinationCity = input.next();
                    destinationCity = destinationCity.toLowerCase();
                    String s2 = String.valueOf(destinationCity.charAt(0)).toUpperCase();
                    String endCityCapitalized = s2 + destinationCity.substring(1);
                    destinationCity = endCityCapitalized;
                    if (!citiesList.contains(City.findCityByName(cities, destinationCity))) {// Check if the destination city exists in the original cities array
                        System.out.println("City named '" + destinationCity + "' not found. Please enter a valid city name.");
                    } else {
                        input.close();
                        break;
                    }
                } break;
                }
            }

        bluePath = findShortestPath(citiesList, startCity, destinationCity);
        if (bluePath != null) { //Check if there is path between start and destination cities
            visualizeTurkeyMap(cities, bluePath, startCity, destinationCity);
        }
    }
    /**
     * Finds a City object in the given ArrayList based on its city name.
     * @param cities The ArrayList of City objects to search.
     * @param cityName The name of the city to find.
     * @return The City object with the matching name, or null if not found.
     */
    public static City findCityByName(ArrayList<City> cities, String cityName) {
        for (City city : cities) {
            if (city.getCityName().equals(cityName)) {
                return city;
            }
        }
        return null;
    }
    /**
     * Calculates the distance between two cities based on their coordinates.
     * @param city1 The first city.
     * @param city2 The second city.
     * @return The distance between the two cities.
     */
    public static double calculateDistance(City city1, City city2) {
        int x1 = city1.getX();
        int y1 = city1.getY();
        int x2 = city2.getX();
        int y2 = city2.getY();
        return  Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));// Apply the Euclidean distance formula
    }
    /**
     * Finds the shortest path between two cities by using Dijkstra's algorithm.
     * @param cities The ArrayList of City objects representing the city map.
     * @param startCityName The name of the starting city.
     * @param destinationCityName The name of the destination city.
     * @return An ArrayList containing the city names in the shortest path (from end to start), or null if no path exists.
     */
    public static ArrayList<String> findShortestPath(ArrayList<City> cities, String startCityName, String destinationCityName) {
        // Find the City objects for start and destination by name
        City startCity = findCityByName(cities, startCityName);
        City endCity = findCityByName(cities, destinationCityName);
        if (startCity == null || endCity == null) {// Check if either city is not found
            return null;
        }
        if (startCity == endCity) {//Handle the case where start and destination are the same city
            ArrayList<String> path = new ArrayList<>();
            path.add(startCity.getCityName());
            System.out.println("Total Distance: 0.00. Path: " + startCity.getCityName());
            return path;
        } else {
            // Initialize arrays for distances, previous cities visited, and visited flags
            double[] distances = new double[ cities.size() ];// Stores distances from start city to each city
            City[] previousCities = new City[ cities.size() ];// Stores the previous city in the shortest path
            boolean[] visited = new boolean[ cities.size() ];// Tracks visited cities
            // Initialize distances, 0 for start city, infinity for others
            for (int i = 0; i < cities.size(); i++) {
                if (cities.get(i) == startCity) {
                    distances[ i ] = 0.0;
                } else {
                    distances[ i ] = Double.MAX_VALUE;
                }
            }
            // Dijkstra's algorithm loop
            for (int i = 0; i < cities.size(); i++) {
                int currentCityIndex = -1;// Index of the unvisited city with the shortest temporary distance
                for (int j = 0; j < cities.size(); j++) {
                    // Finding the unvisited city with the shortest distance
                    if (!visited[ j ] && (currentCityIndex == -1 || distances[ j ] < distances[ currentCityIndex ])) {
                        currentCityIndex = j;
                    }
                }
                if (distances[ currentCityIndex ] == Double.MAX_VALUE) {
                    break;// If all remaining cities have infinite distance breaks loop
                }
                visited[ currentCityIndex ] = true;// Mark the current city as visited
                for (String connection : cities.get(currentCityIndex).getConnectionsList()) {// Reducing distances for connected cities when shorter path found
                    City connectedCity = findCityByName(cities, connection);
                    int connectedCityIndex = cities.indexOf(connectedCity);
                    double distance = 0;
                    if (connectedCity != null) {// Calculate distance if connected city is found
                        distance = distances[ currentCityIndex ] + calculateDistance(cities.get(currentCityIndex), connectedCity);
                    }
                    if (distance < distances[ connectedCityIndex ]) {// Update distance and previous city if a shorter path found
                        distances[ connectedCityIndex ] = distance;
                        previousCities[ connectedCityIndex ] = cities.get(currentCityIndex);
                    }
                }
            }
            if (previousCities[cities.indexOf(endCity)] == null) {// Check if no path exists from start to destination city
                System.out.println("No path could be found.");
                return null;
            }
            ArrayList<String> path = new ArrayList<>();
            // Construct the path in reverse order starting from the destination city
            for (City city = endCity; city != null; city = previousCities[ cities.indexOf(city) ]) {
                path.add(city.getCityName());// Add each city to the path
            }
            ArrayList<String> reversedPath = new ArrayList<>();
            for (int i = path.size() - 1; i >= 0; i--) {
                reversedPath.add(path.get(i));// Add cities from the original path in reverse order
            }
            path = reversedPath;//Replace the original path with the reversed one
            System.out.println("Total distance: " + String.format("%.2f", distances[ cities.indexOf(endCity) ]) + ". Path: " + String.join(" -> ", path));
            return path;// Return the shortest path as an ArrayList of city names
        }
    }
    /**
     * Visualizes the map of Turkey with cities and the shortest path.
     * @param cities City objects representing in the city map.
     * @param bluePath An arrayList of city names representing the shortest path
     * @param startcity The name of the starting city.
     * @param destinationcity The name of the destination city.
     */
    private static void  visualizeTurkeyMap(City[] cities , ArrayList<String> bluePath, String startcity, String destinationcity){
        int canvasSizeX = 2377;// Width of the canvas
        int canvasSizeY = 1055;// Height of the canvas
        String map_Png = "C:\\Users\\gunde\\IdeaProjects\\Homework 2\\src\\map.png";
        StdDraw.setCanvasSize(canvasSizeX/2,canvasSizeY/2);// Set the canvas size
        StdDraw.setXscale(0,canvasSizeX);// Set the X-axis scale
        StdDraw.setYscale(0,canvasSizeY);// Set the Y-axis scale
        StdDraw.clear(StdDraw.WHITE);// Clear the canvas with white color
        StdDraw.picture((double) canvasSizeX /2, (double) canvasSizeY /2,map_Png, canvasSizeX, canvasSizeY);// Draw the map image
        StdDraw.enableDoubleBuffering();// Enable double buffering for smooth animation
        for (City city : cities){
            StdDraw.setPenColor(StdDraw.GRAY);
            StdDraw.filledCircle(city.getX(),city.getY(),4.5);// Draw a circle for each city
            StdDraw.setFont(new Font("Arial", Font.BOLD, 12));// Set the font and size for the city name text
            StdDraw.text(city.getX(),city.getY() + 20 ,city.getCityName());// Draw the city name text
            if (!city.getConnectionsList().isEmpty()) {
                for (String connection : city.getConnectionsList()) {
                    City currentCity = null;
                    for (City city2 : cities) {
                        if (city2.getCityName().equals(connection)) {
                            currentCity = city2;// Find the city object with the matching name
                        }
                    }
                    if (currentCity != null) {
                        StdDraw.setPenColor(StdDraw.GRAY);
                        StdDraw.setPenRadius(0.002);
                        StdDraw.line(city.getX(), city.getY(), currentCity.getX(), currentCity.getY());// Draw connecting lines between cities
                    }
                    if (startcity.equals(destinationcity) && bluePath != null) {
                        StdDraw.setPenColor(StdDraw.BOOK_LIGHT_BLUE);
                        StdDraw.setPenRadius(0.005);
                        City startCity = City.findCityByName(cities, startcity);// Find the city object with the matching name
                        if (startCity != null) {
                            StdDraw.filledCircle(startCity.getX(), startCity.getY(), 4.5);// Draw a blue circle for the starting city
                        }
                        if (startCity != null) {
                            StdDraw.setFont(new Font("Arial", Font.BOLD, 12));
                            StdDraw.text(startCity.getX(), startCity.getY() + 20, startCity.getCityName());// Draw the city name text for the starting city
                        }
                    }
                    else if(bluePath != null){
                    for (int i = 0; i < bluePath.size() - 1; i++) {
                        City previousCity = City.findCityByName(cities, bluePath.get(i));// Find the city object with the matching name
                        City nextCity = City.findCityByName(cities, bluePath.get(i + 1));// Find the city object with the matching name
                        StdDraw.setPenColor(StdDraw.BOOK_LIGHT_BLUE);

                        StdDraw.setPenRadius(0.007);
                        if (previousCity != null) {
                            if (nextCity != null) {
                                StdDraw.line(previousCity.getX(), previousCity.getY(), nextCity.getX(), nextCity.getY());
                                // Draw a blue line between the previous city and the next city in the shortest path
                            }
                        }
                        if (i != bluePath.size() - 1) {
                            if (previousCity != null) {
                                StdDraw.filledCircle(previousCity.getX(), previousCity.getY(), 4.5);
                                StdDraw.setFont(new Font("Arial", Font.BOLD, 12));
                                StdDraw.text(previousCity.getX(), previousCity.getY() + 20, previousCity.getCityName());
                                // Draw a blue circle for the previous city in the shortest path and write the city name text for it.
                            }
                        }
                        if (i == bluePath.size() - 2) {
                            if (nextCity != null) {
                                StdDraw.filledCircle(nextCity.getX(), nextCity.getY(), 4.5);
                                StdDraw.setFont(new Font("Arial", Font.BOLD, 12));
                                StdDraw.text(nextCity.getX(), nextCity.getY() + 20, nextCity.getCityName());
                                // Draw a blue circle for the next city in the shortest path and write the city name text for it.
                            }
                        }
                    }
                    }
            }

            }

        }
        StdDraw.show();
    }
}