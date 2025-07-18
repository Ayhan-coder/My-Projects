import java.io.BufferedWriter;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Comparator;

class MySet<T> {
    private final MyHashSet<T> items;
    public MySet() {items = new MyHashSet<>();
    }
    public boolean add(T item) {return items.add(item); // Add to the set, returns false if the item already exists
    }
    public boolean remove(T item) {return items.remove(item); // Remove from the set, returns true if the item was present
    }
    public boolean contains(T item) {return items.contains(item); // Check if the set contains the item
    }
    public int size() {return items.size(); // Return the number of elements in the set
    }
    public ArrayList<T> getItems() {
        return new ArrayList<>(items.getAllItems()); // Return all items as a list
    }
}
class MyHashSet<T> {
    private static final int INITIAL_CAPACITY = 128;
    private static final double LOAD_FACTOR = 0.5;
    private Object[] table;
    private int size;
    public MyHashSet() {table = new Object[INITIAL_CAPACITY];size = 0;
    }
    private int hash(T item) {return Math.abs(item.hashCode() % table.length);
    }
    public boolean add(T item) {
        if (size >= LOAD_FACTOR * table.length) {resize();
        }
        int index = hash(item);
        while (table[index] != null) {
            if (table[index].equals(item)) {
                return false; // Item already exists
            }
            index = (index + 1) % table.length; // Linear probing
        }
        table[index] = item;
        size++;
        return true;
    }
    public boolean remove(T item) {
        int index = hash(item);
        while (table[index] != null) {
            if (table[index].equals(item)) {
                table[index] = null; // Remove the item
                size--;
                rehash(index);
                return true;
            }
            index = (index + 1) % table.length;
        }
        return false; // Item not found
    }
    public boolean contains(T item) {
        int index = hash(item);
        while (table[index] != null) {
            if (table[index].equals(item)) {
                return true; // Item found
            }
            index = (index + 1) % table.length;
        }
        return false; // Item not found
    }
    public int size() {return size;
    }
    public ArrayList<T> getAllItems() {
        ArrayList<T> items = new ArrayList<>();
        for (Object obj : table) {
            if (obj != null) {
                items.add((T) obj);
            }
        }
        return items;
    }
    private void resize() {
        Object[] oldTable = table;
        table = new Object[oldTable.length * 3];
        size = 0;
        for (Object obj : oldTable) {
            if (obj != null) {
                add((T) obj);
            }
        }
    }
    private void rehash(int start) {
        int index = (start + 1) % table.length;
        while (table[index] != null) {
            T item = (T) table[index];
            table[index] = null;
            size--;
            add(item);
            index = (index + 1) % table.length;
        }
    }
}
class MyHashMap<K, V> {
    private static final int INITIAL_CAPACITY = 128; // Initial size of the hash table
    private static final double LOAD_FACTOR = 0.50; // Maximum load factor before resizing
    private int size; // Number of key-value pairs in the map
    private Entry<K, V>[] table; // Hash table array
    private static class Entry<K, V> {
        K key;
        V value;
        boolean isDeleted; // Marks if an entry has been logically deleted
        Entry(K key, V value) {
            this.key = key;
            this.value = value;
            this.isDeleted = false;
        }
    }
    public MyHashMap() {
        table = new Entry[INITIAL_CAPACITY];
        size = 0;
    }

    private int primaryHash(K key) {
        int hash = key.hashCode();
        return Math.abs((hash ^ (hash >>> 16)) % table.length); // Mix bits to reduce collisions
    }
    private int probeIndex(K key, int i) {
        return Math.abs((primaryHash(key) + i * secondaryHash(key)) % table.length);
    }
    private int secondaryHash(K key) {
        return 7 - Math.abs(key.hashCode() % 7);
    }
    public void put(K key, V value) {
        if (size >= LOAD_FACTOR * table.length) {
            resize();
        }
        int i = 0;
        int index;
        while (true) {
            index = probeIndex(key, i);
            Entry<K, V> entry = table[index];
            // Insert if the slot is empty or logically deleted
            if (entry == null || entry.isDeleted) {
                table[index] = new Entry<>(key, value);
                size++;
                return;
            }
            // Update value if key already exists
            if (entry.key.equals(key)) {
                table[index].value = value;
                return;
            }
            i++;
        }
    }
    public V get(K key) {
        int i = 0;
        int index;
        while (i < table.length) {
            index = probeIndex(key, i);
            Entry<K, V> entry = table[index];
            if (entry == null) {
                return null; // Key not found
            }
            if (!entry.isDeleted && entry.key.equals(key)) {
                return entry.value; // Return value if key matches
            }
            i++;
        }
        return null; // Key not found after probing
    }
    public boolean containsKey(K key) {return get(key) != null;
    }
    private void resize() {
        Entry<K, V>[] oldTable = table;
        table = new Entry[oldTable.length * 3];
        size = 0;

        for (Entry<K, V> entry : oldTable) {
            if (entry != null && !entry.isDeleted) {
                put(entry.key, entry.value); // Rehash and insert into new table
            }
        }
    }
}
class MyPriorityQueue<T> {
    private ArrayList<T> heap;
    private Comparator<T> comparator;
    public MyPriorityQueue(Comparator<T> comparator) {
        heap = new ArrayList<>();
        this.comparator = comparator;
    }

    public void add(T item) {
        heap.add(item);
        int current = heap.size() - 1;
        while (current > 0) {
            int parent = (current - 1) / 2;
            if (comparator.compare(heap.get(current), heap.get(parent)) >= 0) break;
            swap(current, parent);
            current = parent;
        }
    }

    public T poll() {
        if (heap.isEmpty()) return null;
        T top = heap.get(0);
        T last = heap.remove(heap.size() - 1);
        if (!heap.isEmpty()) {
            heap.set(0, last);
            heapBalance(0);
        }
        return top;
    }

    private void heapBalance(int index) {
        int left = 2 * index + 1;
        int right = 2 * index + 2;
        int smallest = index;

        if (left < heap.size() && comparator.compare(heap.get(left), heap.get(smallest)) < 0) {
            smallest = left;
        }
        if (right < heap.size() && comparator.compare(heap.get(right), heap.get(smallest)) < 0) {
            smallest = right;
        }
        if (smallest != index) {
            swap(index, smallest);
            heapBalance(smallest);
        }
    }

    private void swap(int i, int j) {
        T temp = heap.get(i);
        heap.set(i, heap.get(j));
        heap.set(j, temp);
    }

    public boolean isEmpty() {
        return heap.isEmpty();
    }
}
class PostComparator implements Comparator<Post> {
    @Override
    public int compare(Post a, Post b) {
        if (a.getLikes() != b.getLikes()) {// Compare likes in descending order
            return b.getLikes() - a.getLikes();
        }
        return b.getPostId().compareTo(a.getPostId());// Then compare postId in reverse order
    }
}

class User {
    private final String userId;
    private final ArrayList<String> posts; // Stores post IDs created by this user
    private final MySet<String> followers; // Users following this user
    private final MySet<String> following; // Users this user is following
    private final MySet<String> seenPosts; // Posts seen by this user
    public User(String userId) {
        this.userId = userId;
        this.posts = new ArrayList<>();
        this.followers = new MySet<>();
        this.following = new MySet<>();
        this.seenPosts = new MySet<>();
    }
    public ArrayList<String> getPosts() {
        return posts;
    }
    public MySet<String> getFollowing() {
        return following;
    }
    public MySet<String> getSeenPosts() {
        return seenPosts;
    }
    public boolean follow(String userToFollow) {
        return following.add(userToFollow);
    }
    public boolean unfollow(String userToUnfollow) {
        return following.remove(userToUnfollow);
    }
    public boolean addFollower(String followerId) {
        return followers.add(followerId);
    }
    public boolean removeFollower(String followerId) {
        return followers.remove(followerId);
    }
    public boolean createPost(String postId) {
        if (posts.contains(postId)) {
            return false; // Duplicate post ID
        }
        posts.add(postId);
        return true;
    }
    public boolean seePost(String postId) {
        return seenPosts.add(postId); // Adds postId to seenPosts, returns false if already seen
    }
}
class Post {
    private final String postId; // Unique identifier for the post
    private final String authorId; // User ID of the post's creator
    private final String content; // Content of the post
    private int likes; // Number of likes on the post
    private final MySet<String> likedBy; // Set of user IDs who liked the post
    public Post(String postId, String authorId, String content) {
        this.postId = postId;
        this.authorId = authorId;
        this.content = content;
        this.likes = 0;
        this.likedBy = new MySet<>();
    }
    public String getPostId() {
        return postId;
    }
    public String getAuthorId() {
        return authorId;
    }
    public int getLikes() {
        return likes;
    }
    public MySet<String> getLikedBy() {
        return likedBy;
    }
    public void addLike(String userId) {
        if (likedBy.contains(userId)) {
            return; // User has already liked this post
        }
        likedBy.add(userId);
        likes++;
    }
    public void removeLike(String userId) {
        if (!likedBy.contains(userId)) {
            return; // User hasn't liked this post
        }
        likedBy.remove(userId);
        likes--;
    }
    public String getContent() {
        return content;
    }
}

class Operations_Handler {
    private final MyHashMap<String, User> users; // Stores users by their userId
    private final MyHashMap<String, Post> posts; // Stores posts by their postId
    private final StringBuilder log; // Accumulates logs for output
    public Operations_Handler() {
        this.users = new MyHashMap<>();
        this.posts = new MyHashMap<>();
        this.log = new StringBuilder();
    }
    // Method to create a new user
    public void createUser(String userId) {
        if (users.containsKey(userId)) {
            log.append("Some error occurred in create_user.\n");
            return;
        }
        users.put(userId, new User(userId));
        log.append("Created user with Id ").append(userId).append(".\n");
    }
    public void followUser(String followerId, String followeeId) {
        // Check if followerId and followeeId are the same
        if (followerId.equals(followeeId)) {
            log.append("Some error occurred in follow_user.\n");
            return;
        }
        User follower = users.get(followerId);
        User followee = users.get(followeeId);
        if (follower == null || followee == null || !follower.follow(followeeId)) {
            log.append("Some error occurred in follow_user.\n");
            return;
        }
        followee.addFollower(followerId);
        log.append(followerId).append(" followed ").append(followeeId).append(".\n");
    }

    public void unfollowUser(String followerId, String followeeId) {
        User follower = users.get(followerId);
        User followee = users.get(followeeId);

        if (follower == null || followee == null || !follower.unfollow(followeeId)) {
            log.append("Some error occurred in unfollow_user.\n");
            return;
        }
        followee.removeFollower(followerId);
        log.append(followerId).append(" unfollowed ").append(followeeId).append(".\n");
    }

    public void createPost(String userId, String postId, String content) {
        User user = users.get(userId);

        if (user == null || posts.containsKey(postId)) {
            log.append("Some error occurred in create_post.\n");
            return;
        }
        Post post = new Post(postId, userId, content);
        posts.put(postId, post);
        user.createPost(postId);
        log.append(userId).append(" created a post with Id ").append(postId).append(".\n");
    }

    public void seePost(String userId, String postId) {
        User user = users.get(userId);
        Post post = posts.get(postId);
        if (user == null || post == null) {
            log.append("Some error occurred in see_post.\n");
            return;
        }
        user.seePost(postId);
        log.append(userId).append(" saw ").append(postId).append(".\n");
    }
    public void toggleLike(String userId, String postId) {
        User user = users.get(userId);
        Post post = posts.get(postId);
        if (user == null || post == null) {
            log.append("Some error occurred in toggle_like.\n");
            return;
        }
        if (post.getLikedBy().contains(userId)) {
            post.removeLike(userId);
            log.append(userId).append(" unliked ").append(postId).append(".\n");
        } else {
            post.addLike(userId);
            user.seePost(postId); // Liking a post also marks it as seen
            log.append(userId).append(" liked ").append(postId).append(".\n");
        }
    }
    public void seeAllPostsFromUser(String viewerId, String viewedId) {
        User viewer = users.get(viewerId);
        User viewed = users.get(viewedId);
        if (viewer == null || viewed == null) {
            log.append("Some error occurred in see_all_posts_from_user.\n");
            return;
        }
        for (String postId : viewed.getPosts()) {
            viewer.seePost(postId); // Mark each post as seen
        }
        log.append(viewerId).append(" saw all posts of ").append(viewedId).append(".\n");
    }
    public void generateFeed(String userId, int num) {
        User user = users.get(userId);
        if (user == null) {
            log.append("Some error occurred in generate_feed.\n");
            return;
        }
        Comparator<Post> postComparator = new PostComparator();
        MyPriorityQueue<Post> feedQueue = new MyPriorityQueue<>(postComparator);
        for (String followeeId : user.getFollowing().getItems()) {
            User followee = users.get(followeeId);
            if (followee == null) continue;
            for (String postId : followee.getPosts()) {
                Post post = posts.get(postId);
                // Exclude posts created by the user or already seen
                if (post == null || user.getSeenPosts().contains(postId) || post.getAuthorId().equals(userId)) {
                    continue;
                }
                feedQueue.add(post);
            }
        }
        log.append("Feed for ").append(userId).append(":\n");
        int count = 0;
        while (!feedQueue.isEmpty() && count < num) {
            Post post = feedQueue.poll();
            log.append("Post ID: ").append(post.getPostId()).append(", Author: ").append(post.getAuthorId()).append(", Likes: ").append(post.getLikes()).append("\n");
            count++;
        }
        if (count < num) {
            log.append("No more posts available for ").append(userId).append(".\n");
        }
    }
    public void scrollThroughFeed(String userId, int num, ArrayList<Integer> likeSequence) {
        User user = users.get(userId);
        if (user == null) {
            log.append("Some error occurred in scroll_through_feed.\n");
            return;
        }
        log.append(userId).append(" is scrolling through feed:\n");
        Comparator<Post> postComparator = new PostComparator();
        MyPriorityQueue<Post> feedQueue = new MyPriorityQueue<>(postComparator);
        for (String followeeId : user.getFollowing().getItems()) {
            User followee = users.get(followeeId);
            if (followee == null) continue;
            for (String postId : followee.getPosts()) {
                Post post = posts.get(postId);
                // Exclude posts created by the user or already seen
                if (post == null || user.getSeenPosts().contains(postId) || post.getAuthorId().equals(userId)) {
                    continue;
                }
                feedQueue.add(post);
            }
        }
        int count = 0;
        while (!feedQueue.isEmpty() && count < num) {
            Post post = feedQueue.poll();
            user.seePost(post.getPostId()); // Mark post as seen
            boolean liked = likeSequence.get(count) == 1;
            if (liked) {
                post.addLike(userId);
                log.append(userId).append(" saw ").append(post.getPostId())
                        .append(" while scrolling and clicked the like button.\n");
            } else {
                log.append(userId).append(" saw ").append(post.getPostId())
                        .append(" while scrolling.\n");
            }
            count++;
        }
        if (count < num) {
            log.append("No more posts in feed.\n");
        }
    }
    // Method to sort posts of a user
    public void sortPosts(String userId) {
        User user = users.get(userId);
        if (user == null) {
            log.append("Some error occurred in sort_posts.\n");
            return;
        }
        ArrayList<Post> userPosts = new ArrayList<>();
        for (String postId : user.getPosts()) {
            userPosts.add(posts.get(postId));
        }
        if (userPosts.isEmpty()) {
            log.append("No posts from ").append(userId).append(".\n");
            return;
        }
        log.append("Sorting ").append(userId).append("'s posts:\n");
        Comparator<Post> postComparator = new PostComparator();
        sortPostList(userPosts, postComparator);
        for (Post post : userPosts) {
            log.append(post.getPostId()).append(", Likes: ").append(post.getLikes()).append("\n");
        }
    }
    private void sortPostList(ArrayList<Post> posts, Comparator<Post> comparator) {
        if (posts == null || posts.size() <= 1) {
            return;
        }
        mergeSort(posts, 0, posts.size() - 1, comparator);
    }

    private void mergeSort(ArrayList<Post> posts, int left, int right, Comparator<Post> comparator) {
        if (left < right) {
            int mid = left + (right - left) / 2;
            // Recursively split and sort the left half
            mergeSort(posts, left, mid, comparator);
            // Recursively split and sort the right half
            mergeSort(posts, mid + 1, right, comparator);
            // Merge the sorted halves
            merge(posts, left, mid, right, comparator);
        }
    }
    private void merge(ArrayList<Post> posts, int left, int mid, int right, Comparator<Post> comparator) {
        int n1 = mid - left + 1;
        int n2 = right - mid;
        // Create temporary arrays to hold the split data
        ArrayList<Post> leftArray = new ArrayList<>(n1);
        ArrayList<Post> rightArray = new ArrayList<>(n2);
        // Copy data to temporary arrays
        for (int i = 0; i < n1; i++) {
            leftArray.add(posts.get(left + i));
        }
        for (int j = 0; j < n2; j++) {
            rightArray.add(posts.get(mid + 1 + j));
        }
        // Merge the temporary arrays back into the original list
        int i = 0, j = 0, k = left;
        while (i < n1 && j < n2) {
            if (comparator.compare(leftArray.get(i), rightArray.get(j)) <= 0) {posts.set(k, leftArray.get(i));i++;
            } else {posts.set(k, rightArray.get(j));j++;
            }
            k++;
        }
        // Copy remaining elements from leftArray if any
        while (i < n1) {posts.set(k, leftArray.get(i));i++;k++;
        }
        // Copy remaining elements from rightArray if any
        while (j < n2) {posts.set(k, rightArray.get(j));j++;k++;
        }
    }
    // Retrieve the accumulated log
    public String getLog() {return log.toString();
    }
}
class Main {
    public static void main(String[] args) {
        long startTime = System.nanoTime();
        String inputFile = "C:\\Users\\gunde\\IdeaProjects\\Instagram Project\\src\\type4_large.txt";
        String outputFile = "C:\\Users\\gunde\\IdeaProjects\\Instagram Project\\src\\output.txt";
        try {
            Operations_Handler handler = new Operations_Handler();
            processInstructions(inputFile, handler);
            writeOutput(outputFile, handler.getLog());
        } catch (IOException e) {
            System.err.println("Error during I/O operations: " + e.getMessage());
        }
        long endTime = System.nanoTime();
        long elapsedTime = endTime - startTime; // in nanoseconds
        System.out.println("Elapsed Time: " + elapsedTime / 1_000_000 + " ms");
    }
    private static void processInstructions(String inputFile, Operations_Handler handler) throws IOException {
        try (BufferedReader reader = new BufferedReader(new FileReader(inputFile))) {
            String line;
            while ((line = reader.readLine()) != null) {
                executeInstruction(line.trim(), handler);
            }
        }
    }
    private static void executeInstruction(String line, Operations_Handler handler) {
        String[] parts = line.split(" ");
        String command = parts[0];
        try {
            switch (command) {
                case "create_user":
                    handler.createUser(parts[1]);
                    break;
                case "follow_user":
                    handler.followUser(parts[1], parts[2]);
                    break;
                case "unfollow_user":
                    handler.unfollowUser(parts[1], parts[2]);
                    break;
                case "create_post":
                    String userId = parts[1];
                    String postId = parts[2];
                    StringBuilder contentBuilder = new StringBuilder();
                    for (int i = 3; i < parts.length; i++) {
                        if (i > 3) contentBuilder.append(" ");
                        contentBuilder.append(parts[i]);
                    }
                    String content = contentBuilder.toString();
                    handler.createPost(userId, postId, content);
                    break;
                case "see_post":
                    handler.seePost(parts[1], parts[2]);
                    break;
                case "generate_feed":
                    handler.generateFeed(parts[1], Integer.parseInt(parts[2]));
                    break;
                case "sort_posts":
                    handler.sortPosts(parts[1]);
                    break;
                case "toggle_like":
                    handler.toggleLike(parts[1], parts[2]);
                    break;
                case "scroll_through_feed":
                    int num = Integer.parseInt(parts[2]);
                    ArrayList<Integer> likeSequence = new ArrayList<>();
                    for (int i = 0; i < num; i++) {
                        likeSequence.add(Integer.parseInt(parts[3 + i]));
                    }
                    handler.scrollThroughFeed(parts[1], num, likeSequence);
                    break;
                case "see_all_posts_from_user":
                    handler.seeAllPostsFromUser(parts[1], parts[2]);
                    break;
                default:
                    System.out.println("Unknown command: " + command);
            }
        } catch (ArrayIndexOutOfBoundsException | NumberFormatException e) {
            System.out.println("Invalid instruction format: " + line);
        }
    }
    private static void writeOutput(String outputFile, String log) throws IOException {
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(outputFile))) {
            writer.write(log);
        }
    }
}
