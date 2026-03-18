import java.io.File;
import java.io.FileNotFoundException;

/**
 * Main class for running the Migros Delivery Problem.
 */
public class AliAyhanGunder {
    /**
     * Entry point for the application.
     * This method initializes and runs the chosen algorithm for solving the Migros Delivery Problem based on the input file.
     * @throws FileNotFoundException If the specified file does not exist.
     */
    public static void main(String[] args) throws FileNotFoundException {
        // This variable allows selecting the method.
        byte chosenMethod = 2; // Set 2 for using Ant Colony Optimization, set 1 for using Brute Force.

        // Path to the input file containing location data.
        File file = new File("C:\\Users\\gunde\\IdeaProjects\\Homework 3\\src\\input05.txt");

        // Use a switch statement to choose the algorithm.
        switch (chosenMethod) {
            case 1 -> new Bruteforce(file); // If chosenMethod is 1, use the brute force method.
            case 2 -> new AntColonyOptimization(file); // If chosenMethod is 2, use the ant colony optimization method.
        }
    }
}
