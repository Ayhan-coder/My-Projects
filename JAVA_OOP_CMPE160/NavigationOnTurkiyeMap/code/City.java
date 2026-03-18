import java.util.ArrayList;
/**
 * This class represents cities and stores each cities values.
 * It stores the city's name, its location coordinates (x and y),
 * and a list of connecting cities.
 */
public class City {
    private String cityName;//The name of the city.
    private int x;//The X-coordinate of the city's location on a map.
    private int y;//The Y-coordinate of the city's location on a map.
    public ArrayList<String> connectionsList = new ArrayList<>();//ArrayList containing the names of cities that this city connects to.
    public City(String cityName, int x, int y) {// Constructor for a City object.
        this.cityName = cityName;
        this.x = x;
        this.y = y;
        this.connectionsList = new ArrayList<>();
    }

    public City() {// Empty Constructor for a City object.
        this.cityName = "";
        this.x = 0;
        this.y = 0;
        this.connectionsList = new ArrayList<>();//ArrayList containing the names of cities that this city connects to.
    }

    /**
     * Sets the city's name.
     * @param cityName The new name for the city.
     */
    public void setCityName(String cityName) {
    this.cityName = cityName;
}
    /**
     * Sets the city's X-coordinate.
     * @param x The new X-coordinate for the city.
     */
    public void setX(int x) {
    this.x = x;
}
    /**
     * Sets the city's Y-coordinate.
     * @param y The new Y-coordinate for the city.
     */
    public void setY(int y) {
    this.y = y;
}
    /**
     * Returns an ArrayList containing the names of connecting cities.
     * @return An ArrayList of connecting city names.
     */

    public ArrayList<String> getConnectionsList() {
    return connectionsList;
}
    /**
     * Gets the city's name.
     * @return The city's name.
     */
    public String getCityName() {return cityName;}
    /**
     * Gets the city's X-coordinate.
     * @return The city's X-coordinate.
     */
    public int getX() {return x;}
    /**
     * Gets the city's Y-coordinate.
     * @return The city's Y-coordinate.
     */
    public int getY() {return y;}
    /**
     * Finds a city in an array of cities by its name.
     * @param cities An array of cities.
     * @param cityName The name of the city to find.
     * @return The city with the given name, or null if no city with that name is found.
     */
    public static City findCityByName(City[] cities, String cityName) {
        for (City city : cities) {
            if (city.getCityName().equals(cityName)) {
                return city;
            }
        }
        return null;
    }
}
