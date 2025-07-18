import java.io.BufferedReader;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;

class AVLTree<K extends Comparable<K>, V> {// AVL Tree implementation that can store key-value pairs
    private AvlNode<K, V> root;//
    private static class AvlNode<K, V> {
        K key;// The key part of the pair
        V value;// The value part of the pair
        AvlNode<K, V> left; // Left child node
        AvlNode<K, V> right; // Right child node
        int height; // Height of the node in the tree

        AvlNode(K key, V value) {
            this(key, value, null, null);// Constructor for a new node without children
        }
        AvlNode(K key, V value, AvlNode<K, V> left, AvlNode<K, V> right) {// Constructor for a new node with specified children
            this.key = key;
            this.value = value;
            this.left = left;
            this.right = right;
            this.height = 0;// New nodes start with height 0
        }
    }

    public AVLTree() {
        root = null;// Create an empty AVL tree
    }
    public void insert(K key, V value) {
        root = insert(key, value, root);// Add a key-value pair to the tree
    }

    private AvlNode<K, V> insert(K key, V value, AvlNode<K, V> node) {    // Helper method to add a key-value pair and keep the tree balanced

        if (node == null) {// If there's no node here, create a new one
            return new AvlNode<>(key, value);
        }
        int compareResult = key.compareTo(node.key);
        if (compareResult < 0) {   // If the key is smaller, go to the left child
            node.left = insert(key, value, node.left);// If the key is larger, go to the right child
        } else if (compareResult > 0) {
            node.right = insert(key, value, node.right);// If the key is the same, update the value
        } else {
            node.value = value; // Update existing key with new value
        }

        return balance(node);// Make sure the tree is still balanced
    }

    public void remove(K key) {
        root = remove(key, root);// Remove a key from the tree
    }
    private AvlNode<K, V> remove(K key, AvlNode<K, V> node) {
        // Helper method to remove a key and keep the tree balanced
        if (node == null) {return node;// If the key isn't found, do nothing
        }

        int compareResult = key.compareTo(node.key);
        if (compareResult < 0) {// If the key is smaller, go to the left child
            node.left = remove(key, node.left);
        } else if (compareResult > 0) {// If the key is larger, go to the right child
            node.right = remove(key, node.right);
        } else if (node.left != null && node.right != null) {
            // If the node has two children, find the smallest key in the right subtree
            AvlNode<K, V> minNode = findMin(node.right);
            node.key = minNode.key; // Replace current key with the smallest key
            node.value = minNode.value; // Replace current value with the smallest value
            node.right = remove(node.key, node.right); // Remove the smallest node
        } else {
            node = (node.left != null) ? node.left : node.right;
            // If the node has one or no children, replace it with its child
        }

        return balance(node);
    }

    private AvlNode<K, V> findMin(AvlNode<K, V> node) {
        if (node == null) {// Find the node with the smallest key
            return null;
        } else if (node.left == null) {
            return node;
        }
        return findMin(node.left);
    }

    public V get(K key) {// Get the value associated with a key
        return get(root, key);
    }
    // Helper method to find a value by key
    private V get(AvlNode<K, V> node, K key) {
        if (node == null) return null;
        int cmp = key.compareTo(node.key);
        if (cmp < 0) {
            return get(node.left, key);// Look in the left subtree
        } else if (cmp > 0) {
            return get(node.right, key);// Look in the right subtree
        } else {
            return node.value;
        }
    }

    // Method to find the next lower key
    public K findNextLower(K key) {
        return findNextLower(root, key, null);
    }
    // Helper method to find the next smaller key
    private K findNextLower(AvlNode<K, V> node, K key, K bestFit) {
        if (node == null) return bestFit;
        int cmp = key.compareTo(node.key);
        if (cmp > 0) {
            bestFit = node.key;// Current key is a possible fit
            return findNextLower(node.right, key, bestFit);// Look in the right subtree
        } else {
            return findNextLower(node.left, key, bestFit);// Look in the left subtree
        }
    }

    // Method to find the next higher key
    public K higherKey(K key) {
        return findNextHigher(root, key, null);
    }
    // Helper method to find the next larger key
    private K findNextHigher(AvlNode<K, V> node, K key, K bestFit) {
        if (node == null) return bestFit;
        int cmp = key.compareTo(node.key);
        if (cmp < 0) {
            bestFit = node.key;
            return findNextHigher(node.left, key, bestFit);
        } else {
            return findNextHigher(node.right, key, bestFit);
        }
    }

    // Tail map method
    public MyHashMap<K, V> tailMap(K key, boolean inclusive) {
        MyHashMap<K, V> map = new MyHashMap<>();
        tailMap(root, key, map, inclusive);
        return map;
    }

    private void tailMap(AvlNode<K, V> node, K key, MyHashMap<K, V> map, boolean inclusive) {
        if (node == null) return;
        int cmp = key.compareTo(node.key);
        if (cmp < 0) {
            tailMap(node.left, key, map, inclusive);
            map.put(node.key, node.value);
            tailMap(node.right, key, map, inclusive);
        } else if (cmp == 0 && inclusive) {
            map.put(node.key, node.value);
            tailMap(node.right, key, map, inclusive);
        } else {
            tailMap(node.right, key, map, inclusive);
        }
    }
    // Get the height of a node
    private int height(AvlNode<K, V> node) {
        return node == null ? -1 : node.height;
    }
    // Balance the tree at a given node
    private AvlNode<K, V> balance(AvlNode<K, V> node) {
        if (node == null) {
            return node;
        }

        if (height(node.left) - height(node.right) > 1) {// Check if the left side is too heavy
            if (height(node.left.left) >= height(node.left.right)) {
                node = rotateWithLeftChild(node);
            } else {
                node = doubleWithLeftChild(node);
            }
        } else if (height(node.right) - height(node.left) > 1) {// Check if the right side is too heavy
            if (height(node.right.right) >= height(node.right.left)) {node = rotateWithRightChild(node);
            } else {node = doubleWithRightChild(node);
            }
        }
        node.height = Math.max(height(node.left), height(node.right)) + 1;
        return node;// Update the height of this node
    }
    // Rotate the tree to the right with the left child
    private AvlNode<K, V> rotateWithLeftChild(AvlNode<K, V> k2) {
        AvlNode<K, V> k1 = k2.left;
        k2.left = k1.right;
        k1.right = k2;
        k2.height = Math.max(height(k2.left), height(k2.right)) + 1;
        k1.height = Math.max(height(k1.left), k2.height) + 1;
        return k1;
    }
    // Rotate the tree to the left with the right child
    private AvlNode<K, V> rotateWithRightChild(AvlNode<K, V> k1) {
        AvlNode<K, V> k2 = k1.right;
        k1.right = k2.left;
        k2.left = k1;
        k1.height = Math.max(height(k1.left), height(k1.right)) + 1;
        k2.height = Math.max(height(k2.right), k1.height) + 1;
        return k2;
    }
    // Perform a double rotation: first right, then left
    private AvlNode<K, V> doubleWithLeftChild(AvlNode<K, V> k3) {
        k3.left = rotateWithRightChild(k3.left);
        return rotateWithLeftChild(k3);
    }

    private AvlNode<K, V> doubleWithRightChild(AvlNode<K, V> k1) {
        k1.right = rotateWithLeftChild(k1.right);
        return rotateWithRightChild(k1);
    }
}

// Queue implementation
class MyQueue<T> {
    private T[] theArray;// Array to store queue elements
    private int front;
    private int back;
    private int currentSize;
    private static final int DEFAULT_CAPACITY = 10;

    // Constructor to initialize the queue with default capacity
    public MyQueue() {
        theArray = (T[]) new Object[DEFAULT_CAPACITY];
        front = 0;
        back = -1;
        currentSize = 0;
    }
    // Constructor to initialize the queue with a specified capacity

    // Method to add an element to the back of the queue
    public void enqueue(T data) {
        if (isFull()) {
            throw new RuntimeException("full");
        }
        back = (back + 1) % theArray.length;
        theArray[back] = data;
        currentSize++;
    }
    // Method to remove and return the front element of the queue
    public T dequeue() {
        if (isEmpty()) {
            throw new RuntimeException("empty");
        }
        T frontItem = theArray[front];
        front = (front + 1) % theArray.length;
        currentSize--;
        return frontItem;
    }
    // Method to check if the queue is full
    public boolean isFull() {
        return currentSize == theArray.length;
    }
    // Method to check if the queue is empty
    public boolean isEmpty() {
        return currentSize == 0;
    }
    // Method to get the current size of the queue
    public int size() {
        return currentSize;
    }
}
// A simple hashmap
class MyHashMap<K, V> {
    private static final int INITIAL_CAPACITY = 16;
    private static final float LOAD_FACTOR = 0.75f;
    private Entry<K, V>[] table;
    private int size;
    // Each entry has a key, a value, and a link to the next entry in the same bucket
    private static class Entry<K, V> {
        K key;
        V value;
        Entry<K, V> next;

        Entry(K key, V value, Entry<K, V> next) {
            this.key = key;
            this.value = value;
            this.next = next;
        }
    }
    public MyHashMap() {
        table = new Entry[INITIAL_CAPACITY];
        size = 0;
    }
    // Calculate the index in the array for a given key
    private int hash(K key) {
        return (key == null) ? 0 : Math.abs(key.hashCode() % table.length);
    }

    public void put(K key, V value) {// Add or update a key-value pair in the map
        int index = hash(key);
        Entry<K, V> current = table[index];

        while (current != null) {// Look for the key in the bucket
            if ((key == null && current.key == null) || (key != null && key.equals(current.key))) {
                current.value = value;
                return;
            }
            current = current.next;
        }
// If key not found, add a new entry at the beginning of the bucket
        table[index] = new Entry<>(key, value, table[index]);
        size++;

        if (size >= LOAD_FACTOR * table.length) {
            rehash();
        }
    }

    public V get(K key) {// Get the value associated with a key
        int index = hash(key);
        Entry<K, V> current = table[index];

        while (current != null) {
            if ((key == null && current.key == null) || (key != null && key.equals(current.key))) {
                return current.value;
            }
            current = current.next;
        }
        return null;
    }

    public boolean remove(K key) {// Remove a key-value pair from the map
        int index = hash(key);
        Entry<K, V> current = table[index];
        Entry<K, V> previous = null;

        while (current != null) {
            if ((key == null && current.key == null) || (key != null && key.equals(current.key))) {
                if (previous == null) {
                    table[index] = current.next;
                } else {
                    previous.next = current.next;
                }
                size--;
                return true;
            }
            previous = current;
            current = current.next;
        }
        return false;
    }
    // Make the array bigger and reinsert all the entries
    @SuppressWarnings("unchecked")
    private void rehash() {
        Entry<K, V>[] oldTable = table;
        table = new Entry[oldTable.length * 2];
        size = 0;

        for (Entry<K, V> entry : oldTable) { // Go through each entry in the old array
            while (entry != null) {
                put(entry.key, entry.value);
                entry = entry.next;
            }
        }
    }
    // Remove all entries from the map
    public void clear() {
        table = new Entry[INITIAL_CAPACITY];
        size = 0;
    }
    // Get all the values stored in the map as a list
    public ArrayList<V> values() {
        ArrayList<V> valuesList = new ArrayList<>();
        for (Entry<K, V> entry : table) {
            while (entry != null) {
                valuesList.add(entry.value);
                entry = entry.next;
            }
        }
        return valuesList;
    }
}

// A class representing a Truck with an ID and capacity
class Truck {
    private final int id, capacity;

    public Truck(int id, int capacity) {
        this.id = id;
        this.capacity = capacity;
    }

    public int getId() {
        return id;
    }

    public int getCapacity() {
        return capacity;
    }
}
// A class representing a Parking Lot that can hold trucks
class ParkingLot {
    private final int capacity;
    private final int truckLimit;
    private final MyHashMap<Integer, Truck> truckIndex = new MyHashMap<>();
    private MyQueue<Truck> waitingQueue = new MyQueue<>();
    private MyQueue<Truck> readyQueue = new MyQueue<>();
    private int totalTrucks;
    // Create a new parking lot with a certain capacity and truck limit
    public ParkingLot(int capacity, int truckLimit) {
        this.capacity = capacity;
        this.truckLimit = truckLimit;
        this.totalTrucks = 0;
    }
    public int getCapacity() {return capacity;
    }
    public boolean isNotFull() {return totalTrucks < truckLimit;
    }
    // Add a truck to the waiting queue and index it
    public void addTruck(Truck truck) {
        if (isNotFull()) {
            waitingQueue.enqueue(truck);
            truckIndex.put(truck.getId(), truck);
            totalTrucks++;
        }
    }
    // Move a truck from waiting to ready queue
    public Truck moveTruckToReady() {
        if (!waitingQueue.isEmpty()) {
            Truck truck = waitingQueue.dequeue();
            readyQueue.enqueue(truck);
            return truck;
        }
        return null;
    }
    // Get the ready queue
    public MyQueue<Truck> getReadyQueue() {
        return readyQueue;
    }
    // Decrease the total number of trucks
    public void decreaseTotalTrucks() {
        totalTrucks--;
    }
    // Get the total number of trucks
    public int getTotalTrucks() {return totalTrucks;
    }
    // Remove all trucks from the parking lot
    public void clearAllTrucks() {
        waitingQueue = new MyQueue<>();
        readyQueue = new MyQueue<>();
        truckIndex.clear();
        totalTrucks = 0;
    }
}

// A class to manage multiple parking lots and truck operations
class FleetManager {
    private final MyHashMap<Integer, ParkingLot> parkingLots = new MyHashMap<>();
    // Map of parking lots by capacity
    private AVLTree<Integer, ParkingLot> sortedParkingLots;
    // Tree to keep parking lots sorted by capacity
    public FleetManager() {
        this.sortedParkingLots = new AVLTree<>();
    }// Create a new FleetManager with an empty AVL tree

    public void createParkingLot(int capacity, int truckLimit) {
        // Create a new parking lot with given capacity and truck limit
        if (parkingLots.get(capacity) == null) {
            ParkingLot parkingLot = new ParkingLot(capacity, truckLimit);
            parkingLots.put(capacity, parkingLot);
            sortedParkingLots.insert(capacity, parkingLot);
        }
    }
    // Delete a parking lot by its capacity
    public void deleteParkingLot(int capacity) {
        ParkingLot parkingLot = parkingLots.get(capacity);
        if (parkingLot != null) {
            parkingLot.clearAllTrucks();
            parkingLots.remove(capacity);
            sortedParkingLots.remove(capacity);
        }
    }
    // Add a truck to the best available parking lot
    public String addTruck(int truckId, int capacity) {
        ParkingLot parkingLot = sortedParkingLots.get(capacity);
        if (parkingLot != null && parkingLot.isNotFull()) {
            parkingLot.addTruck(new Truck(truckId, capacity));
            return String.valueOf(parkingLot.getCapacity());
        }
        // Find the next smaller parking lot that can fit the truck
        Integer bestFitKey = sortedParkingLots.findNextLower(capacity);
        while (bestFitKey != null) {
            ParkingLot suitableLot = sortedParkingLots.get(bestFitKey);
            if (suitableLot.isNotFull()) {
                suitableLot.addTruck(new Truck(truckId, capacity));
                return String.valueOf(suitableLot.getCapacity());
            }
            bestFitKey = sortedParkingLots.findNextLower(bestFitKey);
        }
        return "-1";
    }
    // Move a truck to ready from a specific lot or the next larger lot
    public String readyTruck(int capacity) {
        ParkingLot parkingLot = sortedParkingLots.get(capacity);
        if (parkingLot != null) {
            Truck movedTruck = parkingLot.moveTruckToReady();
            if (movedTruck != null) {
                return movedTruck.getId() + " " + parkingLot.getCapacity();
            }
        }// If no truck moved, try the next larger parking lots
        Integer nextCapacity = sortedParkingLots.higherKey(capacity);
        while (nextCapacity != null) {
            ParkingLot nextLot = sortedParkingLots.get(nextCapacity);
            Truck movedTruck = nextLot.moveTruckToReady();
            if (movedTruck != null) {
                return movedTruck.getId() + " " + nextLot.getCapacity();
            }
            nextCapacity = sortedParkingLots.higherKey(nextCapacity);
        }
        return "-1";
    }
    // Load trucks up to a certain load amount from a specific lot and larger lots
    public String loadTrucks(int capacity, int loadAmount) {
        StringBuilder result = new StringBuilder();
        int remainingLoad = loadAmount;
        ParkingLot parkingLot = sortedParkingLots.get(capacity);
        if (parkingLot != null) {
            remainingLoad = processLoad(parkingLot, remainingLoad, result);
        }
        if (remainingLoad > 0) { // If we still need to load, move to larger lots
            Integer nextCapacity = sortedParkingLots.higherKey(capacity);
            while (nextCapacity != null && remainingLoad > 0) {
                ParkingLot nextLot = sortedParkingLots.get(nextCapacity);
                // Load from this lot
                remainingLoad = processLoad(nextLot, remainingLoad, result);
                // Check next larger lot
                nextCapacity = sortedParkingLots.higherKey(nextCapacity);
            }
        }// Remove the last " - " if any and return the result
        return result.length() == 0 ? "-1" : result.substring(0, result.length() - 3);
    }// Helper method to load trucks from a parking lot
    private int processLoad(ParkingLot parkingLot, int remainingLoad, StringBuilder result) {
        MyQueue<Truck> readyQueue = parkingLot.getReadyQueue();
        int initialSize = readyQueue.size();
        for (int i = 0; i < initialSize && remainingLoad > 0; i++) {// Take a truck from ready
            Truck truck = readyQueue.dequeue();
            int loadable = Math.min(truck.getCapacity(), remainingLoad);// Determine how much to load
            remainingLoad -= loadable;// Reduce the remaining load
            if (truck.getCapacity() != 0){
            result.append(truck.getId()).append(" ").append(parkingLot.getCapacity()).append(" - ");}
            else {
                result.append(truck.getId()).append(" ").append("-1").append(" - ");
            }
            parkingLot.decreaseTotalTrucks();// Decrease the truck count
        }
        return remainingLoad;
    }// Count the number of trucks in lots with capacity greater than a certain value
    public String countTrucks(int capacity) {
        MyHashMap<Integer, ParkingLot> tailMap = sortedParkingLots.tailMap(capacity, false);
        int count = countTrucksGreaterThan(tailMap);
        return String.valueOf(count);
    }
    // Helper method to count trucks from a set of parking lots
    private int countTrucksGreaterThan(MyHashMap<Integer, ParkingLot> parkingLotsMap) {
        int count = 0;
        ArrayList<ParkingLot> values = parkingLotsMap.values();
        // Get all parking lot
        for (ParkingLot lot : values) {count += lot.getTotalTrucks();// Add up the trucks in each lot
        }
        return count;
    }
}
// Main class of the program
public class Main {
    public static void main(String[] args) {
        String inputFilePath = args[0];
        String outputFilePath = args[1];
        FleetManager fleetManager = new FleetManager();
        // Create a FleetManager to handle operations
        try (BufferedReader reader = new BufferedReader(new FileReader(inputFilePath));
             FileWriter writer = new FileWriter(outputFilePath)) {
            String line;
            while ((line = reader.readLine()) != null) {
                String[] parts = line.split(" ");
                String command = parts[0];
                String result;
                int capacity, limit, truckId, truckCapacity, loadAmount;
                // Decide what to do based on the command
                switch (command) {
                    case "create_parking_lot":
                        capacity = Integer.parseInt(parts[1]);
                        limit = Integer.parseInt(parts[2]);
                        fleetManager.createParkingLot(capacity, limit);
                        break;
                    case "delete_parking_lot":
                        capacity = Integer.parseInt(parts[1]);
                        fleetManager.deleteParkingLot(capacity);
                        break;
                    case "add_truck":
                        truckId = Integer.parseInt(parts[1]);
                        truckCapacity = Integer.parseInt(parts[2]);
                        result = fleetManager.addTruck(truckId, truckCapacity);
                        writer.write(result + "\n");
                        break;
                    case "ready":
                        capacity = Integer.parseInt(parts[1]);
                        result = fleetManager.readyTruck(capacity);
                        writer.write(result + "\n");
                        break;
                    case "load":
                        capacity = Integer.parseInt(parts[1]);
                        loadAmount = Integer.parseInt(parts[2]);
                        result = fleetManager.loadTrucks(capacity, loadAmount);
                        writer.write(result + "\n");
                        break;
                    case "count":
                        capacity = Integer.parseInt(parts[1]);
                        result = fleetManager.countTrucks(capacity);
                        writer.write(result + "\n");
                        break;
                    default:// If the command is not recognized, do nothing
                        break;
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
