// Circle packing driven by an image mask (dark pixels become candidate spawn points).
// Put your image at: data/apple.jpg (or change IMAGE_NAME below).

ArrayList<PVector> spots = new ArrayList<PVector>();
ArrayList<Circle> circles = new ArrayList<Circle>();

PImage img;

final String IMAGE_NAME = "apple.jpg";
final int CANVAS_SIZE = 626;

// How many new circles to try per frame
final int NEW_PER_FRAME = 5;
// Stop if we can't place NEW_PER_FRAME circles after this many attempts
final int MAX_ATTEMPTS_PER_FRAME = 30;

// Mask rule: pick spawn pixels with brightness <= this threshold
final float SPOT_BRIGHTNESS_MAX = 10;

void settings() {
  size(CANVAS_SIZE, CANVAS_SIZE);
  smooth(8);
}

void setup() {
  img = loadImage(IMAGE_NAME);
  if (img == null) {
    println("Missing image: data/" + IMAGE_NAME);
    println("Add it next to this sketch in a data/ folder.");
    noLoop();
    return;
  }

  img.resize(width, height);
  img.loadPixels();

  spots.clear();
  for (int y = 0; y < img.height; y++) {
    for (int x = 0; x < img.width; x++) {
      int index = x + y * img.width;
      color c = img.pixels[index];
      float b = brightness(c);
      if (b <= SPOT_BRIGHTNESS_MAX) {
        spots.add(new PVector(x, y));
      }
    }
  }

  println("spots: " + spots.size());
  background(0);
}

void draw() {
  background(0);
  frameRate(60);

  int count = 0;
  int attempts = 0;

  while (count < NEW_PER_FRAME) {
    Circle newC = newCircle();
    if (newC != null) {
      circles.add(newC);
      count++;
    }
    attempts++;
    if (attempts > MAX_ATTEMPTS_PER_FRAME) {
      noLoop();
      println("finished");
      break;
    }
  }

  for (int i = 0; i < circles.size(); i++) {
    Circle c = circles.get(i);

    if (c.growing) {
      if (c.edges()) {
        c.growing = false;
      } else {
        for (int j = 0; j < circles.size(); j++) {
          Circle other = circles.get(j);
          if (c != other) {
            float d = dist(c.x, c.y, other.x, other.y);
            float distance = c.r + other.r;
            if (d - 2 < distance) {
              c.growing = false;
              break;
            }
          }
        }
      }
    }

    c.show();
    c.grow();
  }
}

Circle newCircle() {
  if (spots.size() == 0) return null;

  int r = int(random(spots.size()));
  PVector spot = spots.get(r);
  float x = spot.x;
  float y = spot.y;

  boolean valid = true;
  for (int i = 0; i < circles.size(); i++) {
    Circle c = circles.get(i);
    float d = dist(x, y, c.x, c.y);
    if (d < c.r + 1) {
      valid = false;
      break;
    }
  }

  if (valid) {
    return new Circle(x, y);
  }

  return null;
}

class Circle {
  float x;
  float y;
  float r;
  boolean growing;

  Circle(float x, float y) {
    this.x = x;
    this.y = y;
    this.r = 1;
    this.growing = true;
  }

  void grow() {
    if (growing) r += 0.5;
  }

  boolean edges() {
    return (x + r >= width || x - r <= 0 || y + r >= height || y - r <= 0);
  }

  void show() {
    noFill();
    stroke(255);
    strokeWeight(1);
    ellipse(x, y, r * 2, r * 2);
  }
}
