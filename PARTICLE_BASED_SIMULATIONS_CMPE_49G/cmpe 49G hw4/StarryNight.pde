// ============================================================
// "Starry Night" — Van Gogh tarzı Perlin Noise Flow Field
// CmpE49G Project 3 — Visual 1
// ============================================================
// Teknik: Her grid hücresindeki Perlin noise değeri bir açıya
// dönüştürülür. Binlerce parçacık bu açıya göre akar.
// Bias: Tuvalin üst yarısında spiral, alt yarısında yatay akış.
// ============================================================

int NUM_PARTICLES = 4000;
float NOISE_SCALE = 0.004;
float PARTICLE_SPEED = 2.2;
int MAX_STEPS = 80;

Particle[] particles;
float zoff = 0;

void setup() {
  size(1200, 750);
  background(10, 12, 35);           // Gece mavisi arka plan
  colorMode(HSB, 360, 100, 100, 100);
  smooth();
  
  particles = new Particle[NUM_PARTICLES];
  for (int i = 0; i < NUM_PARTICLES; i++) {
    particles[i] = new Particle();
  }
}

void draw() {
  // Çok hafif karartma — iz efekti için
  fill(0, 0, 4, 18);
  noStroke();
  rect(0, 0, width, height);
  
  for (Particle p : particles) {
    p.update();
    p.show();
    if (p.isDead()) p.reset();
  }
  
  zoff += 0.0008;  // Zamanla hafifçe değişen alan
  
  // 300 frame sonra kaydet
  if (frameCount == 300) {
    saveFrame("StarryNight.png");
    println("Kaydedildi!");
  }
}

// ---- Akış yönü hesaplama ----
float getAngle(float x, float y) {
  float n = noise(x * NOISE_SCALE, y * NOISE_SCALE, zoff);
  
  // Bias: Üstte daha fazla spiral (2π×2), altta daha az (2π×0.8)
  float biasStrength = map(y, 0, height, 2.0, 0.8);
  float angle = n * TWO_PI * biasStrength;
  
  // Merkeze yakın bölgede güçlü spiral bias
  float cx = width / 2.0, cy = height * 0.35;
  float d = dist(x, y, cx, cy);
  if (d < 200) {
    float toward = atan2(y - cy, x - cx) + HALF_PI;
    angle = lerp(toward, angle, d / 200.0);
  }
  return angle;
}

// ---- Parçacık Sınıfı ----
class Particle {
  float x, y;
  float px, py;
  float speed;
  int steps;
  color col;
  float alpha;
  float sw;    // stroke weight
  
  Particle() { reset(); }
  
  void reset() {
    x  = random(width);
    y  = random(height);
    px = x;
    py = y;
    steps = 0;
    speed = random(PARTICLE_SPEED * 0.6, PARTICLE_SPEED * 1.4);
    
    // Van Gogh paleti: mavi, sarı, beyaz-altın
    float r = random(1);
    if (r < 0.45) {
      // Koyu mavi — derin gece
      col = color(random(200, 230), random(65, 90), random(55, 85), random(55, 80));
    } else if (r < 0.75) {
      // Açık mavi — gökyüzü
      col = color(random(180, 210), random(40, 70), random(80, 100), random(45, 75));
    } else if (r < 0.90) {
      // Altın sarı — yıldızlar
      col = color(random(40, 58), random(80, 100), random(90, 100), random(60, 90));
    } else {
      // Parlak beyaz-krem — ay/ışıklar
      col = color(random(35, 55), random(20, 45), random(92, 100), random(50, 80));
    }
    sw    = random(0.4, 1.8);
    alpha = random(45, 90);
  }
  
  void update() {
    float angle = getAngle(x, y);
    px = x;
    py = y;
    x += cos(angle) * speed;
    y += sin(angle) * speed;
    steps++;
  }
  
  void show() {
    strokeWeight(sw);
    stroke(hue(col), saturation(col), brightness(col), alpha);
    line(px, py, x, y);
  }
  
  boolean isDead() {
    return (x < 0 || x > width || y < 0 || y > height || steps > MAX_STEPS);
  }
}
