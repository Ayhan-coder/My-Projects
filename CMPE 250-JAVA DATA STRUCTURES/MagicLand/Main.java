import java.io.*;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.Objects;

/**
 * An implementation of a Set using a hash set.
 * This class provides basic operations such as adding, removing, and checking
 * for an element's existence, along with utility methods to get the size and
 * retrieve all elements.
 * @param <T> The type of elements to be stored in the set.
 */
class MySet<T> {
    private final MyHashSet<T> items;
    public MySet() {items = new MyHashSet<>();// Initialize the hash set
    }
    public void add(T item) {
        items.add(item);// Add item to the set
    }
    public void remove(T item) {
        items.remove(item);// Remove item from the set
    }
    public boolean contains(T item) {return items.contains(item); // Check if the set contains the item
    }
}
/**
 * An implementation of a hash set that provides basic set operations
 * such as addition, removal, and containment checks. The hash set is implemented
 * using a hash table with linear probing to resolve collisions.
 * @param <T> the type of items to be stored in the set
 */
class MyHashSet<T> {
    private static final int INITIAL_CAPACITY = 1024;// Initial capacity of the hash table
    private static final double LOAD_FACTOR = 0.90;// Load factor for resizing
    private Object[] table;
    private int size;
    public MyHashSet() {table = new Object[INITIAL_CAPACITY];// Initialize the table with a fixed size
        size = 0;
    }
    // Hash function to get the index of an item
    private int hash(T item) { return Math.abs(item.hashCode() % table.length);
    }// Add an item to the hash set
    public boolean add(T item) {
        if (size >=LOAD_FACTOR * table.length) {resize();
        }// Resize if the table is too full
        int index =hash(item);
        while (table[index] != null) {
            if (table[index] == item) {
                return false; // Item already exists
            }
            index= (index + 1) % table.length; // Linear probing
        }
        table[index] =item;
        size++;
        return true;
    }
    // Remove an item from the hash set
    public boolean remove(T item) {
        int index = hash(item);
        while (table[index] !=null) {
            if (table[index] == item) {
                table[index] =null; // Remove the item
                size--;
                rehash(index);// Rehash the following items
                return true;
            }
            index = (index+ 1)% table.length;
        }
        return false; // Item not found
    }// Check if the set contains an item
    public boolean contains(T item) {
        int index =hash(item);
        while (table[index]!= null) {
            if (table[index] == item) {
                return true; // Item found
            }
            index =(index + 1) % table.length;
        }
        return false; // Item not found
    }

    // Resize the table and rehash the items
    private void resize() {
        Object[] oldTable = table;
        table= new Object[oldTable.length * 2];// double the table size
        size = 0;
        for (Object obj: oldTable) {
            if (obj !=null) {
                add((T) obj);// Rehash each item
            }
        }
    }
    // Rehash an item in the table if it's deleted or moved
    private void rehash(int start) {
        int index =(start + 1) % table.length;
        while (table[index] != null) {
            T item = (T)table[index];
            table[index] = null;
            size--;add(item);// Rehash the item
            index =(index + 1) % table.length;
        }
    }
}
/**
 * An implementation of a hash map that associates keys with values. Based on separate chaining for collision handling.
 * This implementation provides constant-time performance for basic operations like get and put in the average case.
 * @param <K> the type of keys
 * @param <V> the type of mapped values
 */
class MyHashMap<K, V> {
    private static class Entry<K, V> {//inner class for entry object
        K key;
        V value;
        Entry<K, V> next;
        Entry(K key, V value) {
            this.key = key;
            this.value = value;
            this.next = null;
        }
    }

    private ArrayList<Entry<K, V>> table;// ArrayList for separate chaining
    private int size;
    private int capacity;
    private static final double LOAD_FACTOR = 0.75;

    public MyHashMap() {
        capacity = 16; // initial capacity
        table = new ArrayList<>(capacity);
        for (int i = 0; i < capacity; i++) {
            table.add(null);// Initialize all to null
        }
        size = 0;
    }

    private int hash(K key) {
        int h = key.hashCode();
        h = h ^ (h >>> 16);// Spread bits to reduce collisions
        return h & (capacity - 1);// Ensure index within bounds
    }

    public void put(K key, V value) {
        if (size >= capacity * LOAD_FACTOR) {
            resize();// Resize if load factor exceeded
        }
        int index = hash(key);// Compute hash index
        Entry<K, V> head = table.get(index);
        Entry<K, V> current = head;
        while (current != null) {// Traverse the chain to find if key exists
            if (current.key == key) {
                current.value = value;
                return;
            }
            current = current.next;
        }

        Entry<K, V> newEntry = new Entry<>(key, value);// Insert new entry at the beginning of the chain
        newEntry.next = head;
        table.set(index, newEntry);
        size++;
    }
    public V get(K key) {
        int index = hash(key);
        Entry<K, V> current = table.get(index);
        while (current != null) {// Traverse the chain to find the key
            if (current.key == key) {
                return current.value;
            }
            current = current.next;
        }
        return null;
    }
    public V getOrDefault(K key, V defaultValue) {//Retrieves the value associated with a key or returns a default value
        V value = get(key);
        return value != null ? value : defaultValue;
    }
    private void resize() {//Resizes the hash table when load factor is exceeded
        ArrayList<Entry<K, V>> oldTable = table;
        int oldCapacity = capacity;
        capacity = capacity * 2;
        table = new ArrayList<>(capacity);
        for (int i = 0; i < capacity; i++) {
            table.add(null);
        }
        size = 0;
        for (int i = 0; i < oldCapacity; i++) {
            Entry<K, V> current = oldTable.get(i);
            while (current != null) {
                put(current.key, current.value);
                current = current.next;
            }
        }
    }
}
/**
 * A priority queue implementation using a binary heap.
 * This class allows elements to be added, retrieved, and removed in priority order
 * based on a provided comparator. It ensures efficient addition and removal
 * operations.
 * @param <T> the type of elements in this priority queue
 */
class MyPriorityQueue<T> {
    private final ArrayList<T> heap; // ArrayList to store heap elements
    private final Comparator<T> comparator;
    public MyPriorityQueue(Comparator<T> comparator) {
        this.heap = new ArrayList<>();// Initialize the heap
        this.comparator = comparator;
    }
    public void add(T element) {
        heap.add(element);
        bubbleUp(heap.size() - 1);
    }
    public T poll() {//Removes and returns the highest priority element from the queue
        if (heap.isEmpty()) return null;
        T result = heap.get(0);
        T last = heap.remove(heap.size() - 1);
        if (!heap.isEmpty()) {
            heap.set(0, last);
            bubbleDown(0);
        }
        return result;
    }

    public boolean isEmpty() {
        return heap.isEmpty();
    }//Checks if the priority queue is empty.

    private void bubbleUp(int index) {//Restores heap property by bubbling up the element
        while (index > 0) {
            int parentIndex = (index - 1) / 2;
            if (comparator.compare(heap.get(index), heap.get(parentIndex)) >= 0) {
                break;
            }
            swap(index, parentIndex);
            index = parentIndex;
        }
    }

    private void bubbleDown(int index) {//Restores heap property by bubbling down the element
        int size = heap.size();
        while (true) {
            int leftChild = 2 * index + 1;
            int rightChild = 2 * index + 2;
            int smallest = index;

            if (leftChild < size && comparator.compare(heap.get(leftChild), heap.get(smallest)) < 0) {
                smallest = leftChild;// Compare with left child
            }
            if (rightChild < size && comparator.compare(heap.get(rightChild), heap.get(smallest)) < 0) {
                smallest = rightChild;// Compare with right child
            }

            if (smallest == index) {break;// Heap property satisfied
            }
            swap(index, smallest);
            index = smallest;
        }
    }//Swaps two elements in the heap
    private void swap(int i, int j) {
        T temp = heap.get(i);
        heap.set(i, heap.get(j));
        heap.set(j, temp);
    }
}
/**
 * Represents a node in a grid based map with position, type, visibility, and connected edges.
 * A node can store information about its pass ability, whether it's visible,
 * and its connections to neighboring nodes via edges.
 */
class Node {
    int x, y, type;
    boolean visible;
    ArrayList<Edge> edges = new ArrayList<>();// Connected edges
    public Node(int x, int y, int type) {
        this.x = x;
        this.y = y;
        this.type = type;
        this.visible = (type == 0);// Initialize visibility based on type
    }
    public boolean isPassable() {
        if (type == 0) return true; // Passable node
        if (type == 1) return false; // impassable node
        return !visible; // For types >= 2, not visible
    }
    public void addEdge(Node neighbor, double travelTime) {
        edges.add(new Edge(neighbor, travelTime));//Adds an edge connecting this node to a neighbor
    }
    public boolean equals(Object o) {//Overrides equals to compare nodes based on coordinates
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Node node = (Node) o;
        return x == node.x && y == node.y;
    }
    public int hashCode() {return Objects.hash(x, y);
    }//Overrides hashCode to generate hash based on coordinates
}
/**
 * Represents an edge in a graph, which connects to a specific node
 * and includes a travel time or weight associated with traversing the edge.
 */
class Edge {
    Node end; // Destination node
    double travelTime;// Time to traverse the edge
    public Edge(Node end, double travelTime) {
        this.end = end;
        this.travelTime = travelTime;
    }
}
/**
 * Represents a grid-based map that consists of nodes. This class provides functionality
 * to load nodes and edges from files, nodes at specific coordinates, update node
 * properties, and adjust visibility based on a given radius.
 */
class LocationMap {
    int width, height;//Dimensions of map
    public Node[][] grid;//2D array for map
    public void loadNodes(String filePath) throws IOException {//Loads nodes from a file and initializes the grid
        try (BufferedReader br = new BufferedReader(new FileReader(filePath))) {
            String[] dimensions = br.readLine().trim().split("\\s+");
            this.width = Integer.parseInt(dimensions[0]);
            this.height = Integer.parseInt(dimensions[1]);
            this.grid = new Node[width][height];
            String line;
            while ((line = br.readLine()) != null) {
                String[] parts = line.trim().split("\\s+");
                int x = Integer.parseInt(parts[0]);
                int y = Integer.parseInt(parts[1]);
                int type = Integer.parseInt(parts[2]);
                grid[x][y] = new Node(x, y, type);
            }
        }
    }//Loads edges from a file and connects nodes accordingly
    public void loadEdges(String filePath) throws IOException {
        try (BufferedReader br = new BufferedReader(new FileReader(filePath))) {
            String line;
            while ((line = br.readLine()) != null) {
                String[] parts = line.trim().split("\\s+");
                String[] nodePair = parts[0].split(",");
                String[] node1Coordinates = nodePair[0].split("-");
                String[] node2Coordinates = nodePair[1].split("-");
                int x1 = Integer.parseInt(node1Coordinates[0]);
                int y1 = Integer.parseInt(node1Coordinates[1]);
                int x2 = Integer.parseInt(node2Coordinates[0]);
                int y2 = Integer.parseInt(node2Coordinates[1]);
                double travelTime = Double.parseDouble(parts[1]);
                Node node1 = grid[x1][y1];
                Node node2 = grid[x2][y2];
                node1.addEdge(node2, travelTime);
                node2.addEdge(node1, travelTime); // Assuming undirected edges
            }
        }
    }//Retrieves the node at specified coordinates
    public Node getNode(int x, int y) {return (x >= 0 && x < width && y >= 0 && y < height) ? grid[x][y] : null;
    }//Applies a wizard's choice by changing all nodes of a specified type to type 0
    public void applyWizardChoice(int option) {
        // Change all nodes of the specified type to type 0
        for (int x = 0; x < width; x++) {
            for (int y = 0; y < height; y++) {
                Node node = grid[x][y];
                if (node.type == option) {
                    node.type = 0; // Change type to 0 (passable)
                    node.visible = true;} // Make sure it's visible
            }
        }
    }//Updates the visibility of nodes within a given radius from the current node
    public void updateVisibility(Node currentNode, double radius) {
        int startX = currentNode.x;
        int startY = currentNode.y;
        int radiusSquared = (int) Math.ceil(radius * radius); // Use squared radius to avoid sqrt

        for (int dx = (int) -radius; dx <= radius; dx++) {
            for (int dy = (int) -radius; dy <= radius; dy++) {
                int x = startX + dx;
                int y = startY + dy;
                if (x >= 0 && x < width && y >= 0 && y < height) {
                    if (dx * dx + dy * dy <= radiusSquared) {
                        Node node = grid[x][y];
                        if (node != null) node.visible = true;}}}
        }
    }
}
/**
 * The PathfinderForWizard class is responsible for determining the travel time
 * between two nodes in a grid-based map using a modified Dijkstra's algorithm.
 * It ensures terrain pass ability based on specific rules and constraints
 * imposed by the wizard's choices.
 */
class PathfinderForWizard {
    private final LocationMap locationMap;
    public PathfinderForWizard(LocationMap locationMap) {
        this.locationMap = locationMap;
    }
        // Finds the minimum travel time from start to end node considering passable types
    public double findTravelTime(Node start, Node end, MySet<Integer> passableTypes) {
        MyHashMap<Node, Double> distances = new MyHashMap<>();// Maps nodes to their current shortest distance
        MyPriorityQueue<NodeDistance> queue = new MyPriorityQueue<>(Comparator.comparingDouble(nd -> nd.distance));

        // Initialize distances
        distances.put(start, 0.0);
        queue.add(new NodeDistance(start, 0.0));

        while (!queue.isEmpty()) {
            NodeDistance currentDistance = queue.poll();// Get node with smallest distance
            Node current = currentDistance.node;

            if (current.x == end.x && current.y == end.y) {
                return currentDistance.distance; // Return total travel time
            }
            // Check if destination is reached
            for (Edge edge : current.edges) {
                Node neighbor = edge.end;

                //  check if the neighbor is passable
                if (neighbor.type == 0 || passableTypes.contains(neighbor.type) || neighbor.isPassable()) {
                    double newDistance = distances.get(current) + edge.travelTime;
                    // If a shorter path to neighbor is found
                    if (newDistance < distances.getOrDefault(neighbor, Double.MAX_VALUE)) {
                        distances.put(neighbor, newDistance);
                        queue.add(new NodeDistance(neighbor, newDistance));
                    }
                }
            }
        }
        return Double.MAX_VALUE; // No valid path found
    }//Helper class to associate nodes with their current distance for the priority queue
    private static class NodeDistance {
        Node node;
        double distance;

        NodeDistance(Node node, double distance) {
            this.node = node;
            this.distance = distance;
        }
    }
}
/**
 * The PathfinderForTraveller class is responsible for finding the shortest path between two nodes
 * within a grid map using a variation of Dijkstra's algorithm. It considers edge travel times
 * and node pass-ability to determine the optimal path. If no path exists between the start
 * and end nodes, it returns null.
 */
class PathfinderForTraveller {
    public final LocationMap locationMap;

    public PathfinderForTraveller(LocationMap locationMap) {
        this.locationMap = locationMap;
    }
    // Finds the shortest path from start to end node
    public ArrayList<Node> findShortestPath(Node start, Node end) {
        MyHashMap<Node, ArrayList<Node>> paths = new MyHashMap<>(); // Store full paths for each node
        MyHashMap<Node, Double> distances = new MyHashMap<>();
        MyPriorityQueue<NodeDistance> queue = new MyPriorityQueue<>(Comparator.comparingDouble(nd -> nd.distance));

        // Initialize distances and paths
        for (int x = 0; x < locationMap.width; x++) {
            for (int y = 0; y < locationMap.height; y++) {
                Node node = locationMap.getNode(x, y);
                if (node != null) {
                    distances.put(node, Double.MAX_VALUE);
                }
            }
        }
        distances.put(start, 0.0);// Set distance for start node and initialize path
        ArrayList<Node> initialPath = new ArrayList<>();
        initialPath.add(start);
        paths.put(start, initialPath);
        queue.add(new NodeDistance(start, 0.0));
        while (!queue.isEmpty()) {
            NodeDistance currentDistance = queue.poll();
            Node current = currentDistance.node;
            // Stop if we reach the destination
            if (current.x == end.x && current.y == end.y) {
                return paths.get(current); // Return the path directly
            }
            for (Edge edge : current.edges) {
                Node neighbor = edge.end;
                if (!neighbor.isPassable()) {continue;
                }
                double newDistance = distances.get(current) + edge.travelTime;
                if (newDistance < distances.getOrDefault(neighbor, Double.MAX_VALUE)) {// If a shorter path to neighbor is found
                    distances.put(neighbor, newDistance);
                    // Update the path for the neighbor
                    ArrayList<Node> newPath = new ArrayList<>(paths.get(current));
                    newPath.add(neighbor);
                    paths.put(neighbor, newPath);
                    queue.add(new NodeDistance(neighbor, newDistance));
                }
            }
        }
        return null;// If no path is found, return null
    }//Helper class to associate nodes with their current distance for the priority queue
    public static class NodeDistance {
        Node node;
        double distance;

        NodeDistance(Node node, double distance) {
            this.node = node;
            this.distance = distance;
        }
    }
}
/**
 * The Wizard class represents a decision making entity in a grid-based map,
 * capable of evaluating multiple options and determining the best route
 * based on specific criteria such as travel time.
 */
class Wizard {
    public ArrayList<Integer> offeredOptions;// List of options offered to the wizard
    public Integer chosenOption;// The option chosen by the wizard
    public void offerOptions(ArrayList<Integer> options) {
        this.offeredOptions = options;
    }
    //Chooses the best option based on the minimum travel time to the next objective
    public Integer chooseBestOption(Node current, Node nextObjective, LocationMap locationMap) {
        double minTravelTime = Double.MAX_VALUE;
        Integer bestOption = null;
        MySet<Integer> passableTypes = new MySet<>();
        // Evaluate each offered option //
        for (Integer option : offeredOptions) {
            passableTypes.add(option);
            PathfinderForWizard pathfinder = new PathfinderForWizard(locationMap);
            double travelTime = pathfinder.findTravelTime(current, nextObjective, passableTypes);
            // Determine if this option provides a better travel time
            if (travelTime < minTravelTime || (travelTime == minTravelTime && (bestOption == null || option < bestOption))) {
                minTravelTime = travelTime;
                bestOption = option;// Update best option
            }
            passableTypes.remove(option); // Remove option for next iteration
        }
        this.chosenOption = bestOption;
        return bestOption;
    }
}
/**
 * Represents an objective with in the simulation.
 * Each objective is associated with a specific location (x, y) and an optional list of choices or actions.
 */
class Objective {
    int x, y;
    ArrayList<Integer> options; // Null if no wizard help
    public Objective(int x, int y, ArrayList<Integer> options) {
        this.x = x;
        this.y = y;
        this.options = options;
    }
}
/**
 * The Objective Manager class is responsible for managing objectives within a scenario,
 * including loading objectives from a file, tracking their locations, and providing
 * access to the list of objectives, starting node, and reveal radius.
 */
class ObjectiveManager {
    public ArrayList<Objective> objectives;
    public Node startNode;
    public double revealRadius;
    //Loads objectives from a file, including reveal radius and starting node
    public void loadObjectives(String filePath) throws IOException {
        objectives = new ArrayList<>();
        try (BufferedReader br = new BufferedReader(new FileReader(filePath))) {
            String radiusLine = br.readLine();
            revealRadius = Double.parseDouble(radiusLine.trim());
            String startLine = br.readLine();
            String[] startParts = startLine.trim().split("\\s+");
            int startX = Integer.parseInt(startParts[0]);
            int startY = Integer.parseInt(startParts[1]);
            startNode = new Node(startX, startY, 0);
            String line;
            while ((line = br.readLine()) != null) {
                String[] parts = line.trim().split("\\s+");
                int x = Integer.parseInt(parts[0]);
                int y = Integer.parseInt(parts[1]);
                ArrayList<Integer> options = null;
                if (parts.length > 2) {
                    options = new ArrayList<>();
                    for (int i = 2; i < parts.length; i++) {
                        options.add(Integer.parseInt(parts[i]));
                    }
                }
                objectives.add(new Objective(x, y, options));
            }
        }
    }
    public ArrayList<Objective> getObjectives() {return objectives;
    }
    public Node getStartNode() {return startNode;
    }
    public double getRevealRadius() {return revealRadius;
    }
}
/**
 * The Simulator class is the central control system for managing the execution of the simulation.
 * It handles the initialization and execution of a simulated environment, including grid loading, pathfinding,
 * objectives management, and visibility updates. The simulation revolves around achieving sequential objectives
 * within a defined map, using visibility constraints and pathfinding strategies to navigate the map.
 */
class Simulator {
    public  String outputFilePath;
    public LocationMap locationMap;
    public PathfinderForTraveller pathfinder;
    public  ObjectiveManager objectiveManager;
    public  Wizard wizard;
    public Simulator(String outputFilePath) {
        this.outputFilePath = outputFilePath;
        this.objectiveManager = new ObjectiveManager();
        this.wizard = new Wizard();
    }//Initializes the simulation by loading nodes, edges, and objectives
    public void initialize(String nodesFile, String edgesFile, String objectivesFile) throws IOException {
        locationMap = new LocationMap();
        locationMap.loadNodes(nodesFile);
        locationMap.loadEdges(edgesFile);
        objectiveManager.loadObjectives(objectivesFile);
        pathfinder = new PathfinderForTraveller(locationMap);
    }//Runs the simulation, navigating through objectives and writing output
    public void run() throws IOException {
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(outputFilePath))) {
            Node currentNode = locationMap.getNode(objectiveManager.getStartNode().x, objectiveManager.getStartNode().y);
            locationMap.updateVisibility(currentNode, objectiveManager.getRevealRadius()); // Update visibility at the start
            int objectiveNumber = 1;
            ArrayList<Objective> objectives = objectiveManager.getObjectives();
            while (objectiveNumber <= objectives.size()) {
                Objective objective = objectives.get(objectiveNumber - 1);// Get current objective
                Node endNode = locationMap.getNode(objective.x, objective.y);// Get destination node
                ArrayList<Node> path = pathfinder.findShortestPath(currentNode, endNode);// Find path to objective
                if (path == null) {
                    writer.write("Path is impassable!\n");
                    return;
                }
                int i = 0;
                while (i < path.size() - 1) {
                    Node nextNode = path.get(++i);// Move to next node in path
                    writer.write("Moving to " + nextNode.x + "-" + nextNode.y + "\n");
                    currentNode = nextNode;
                    locationMap.updateVisibility(currentNode, objectiveManager.getRevealRadius());
                    // Check for impassable nodes
                    boolean pathBlocked = false;
                    for (int j = i + 1; j < path.size(); j++) {
                        if (!path.get(j).isPassable()) {
                            writer.write("Path is impassable!\n");
                            pathBlocked = true;
                            break;
                        }
                    }
                    if (pathBlocked) {// If path is blocked, attempt to find a new path
                        path = pathfinder.findShortestPath(currentNode, endNode);
                        if (path == null) {
                            writer.write("Path is impassable!\n");
                            return;
                        }
                        i = 0;
                    }
                }
                writer.write("Objective " + objectiveNumber + " reached!\n");
                if (objective.options != null) {// If objective has wizard options
                    int index = objectiveManager.objectives.indexOf(objective);
                    Objective nextobjective = objectiveManager.getObjectives().get(index+1);
                    wizard.offerOptions(objective.options); // Offer options to wizard
                    Integer choice = wizard.chooseBestOption(currentNode, locationMap.getNode(nextobjective.x,nextobjective.y), locationMap);
                    if (choice != null) {// If an option is chosen
                        writer.write("Number " + choice + " is chosen!\n");
                        locationMap.applyWizardChoice(choice);
                    }
                }
                objectiveNumber++;}}// Move to next objective
    }
}
/**
 * The Main class is the entry point for the simulation application.
 * It initializes the required files, sets up the simulation environment,
 * and executes the simulation.
 */
class Main {
    public static void main(String[] args) {
        //String nodesFile = args[0];
        //String edgesFile = args[1];
        //String objectivesFile = args[2];
        //String outputFile = args[3];
        String nodesFile = "C:\\Users\\gunde\\IdeaProjects\\Magical Map\\src\\nodes-500-500.txt";
        String edgesFile = "C:\\Users\\gunde\\IdeaProjects\\Magical Map\\src\\edges-500-500.txt";
        String objectivesFile = "C:\\Users\\gunde\\IdeaProjects\\Magical Map\\src\\obj-500-500.txt";
        String outputFile = "C:\\Users\\gunde\\IdeaProjects\\Magical Map\\src\\output.txt";
        try {
            //long startTime = System.nanoTime(); // Start measuring time
            Simulator simulator = new Simulator(outputFile);
            simulator.initialize(nodesFile, edgesFile, objectivesFile);
            simulator.run();
            //long endTime = System.nanoTime(); // End measuring time
            //double elapsedTimeInSeconds = (endTime - startTime) / 1_000_000_000.0;
            //System.out.printf("Simulation completed in %.3f seconds.%n", elapsedTimeInSeconds);
        } catch (IOException e) {
            System.out.println("Error occurred during simulation: " + e.getMessage());
        }
    }
}




