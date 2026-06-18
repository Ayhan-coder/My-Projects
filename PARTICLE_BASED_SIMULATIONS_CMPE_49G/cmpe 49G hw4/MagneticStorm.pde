// ============================================================
// "Magnetic Storm" — İki Kutuplu Manyetik Alan Bias
// CmpE49G Project 3 — Visual 4
// ============================================================
// Teknik: İki sanal "kutup" tanımlanır. Her noktadaki akış
// yönü; iki kutuptan gelen manyetik vektörlerin toplamına
// Perlin noise eklenerek hesaplanır.
// Bias: Sol negatif kutup (çekme), sağ pozitif kutup (itme).
// Renk: Mor, pembe, elektrik mavi paleti.
// ============================================================

int   NUM_PARTICLES = 5500;
float NOISE_SCALE   = 0.003;
float SPEED         = 2.0;
int   MAX_STEPS     = 100;

// Kutup konumları
PVector poleA, poleB;
float   poleStrength = 18000;

MParticle[] particles;

void setup() {
  size(1200, 750);
  background(8, 4, 22);
  colorMode(HSB, 360, 100, 100, 100);
  smooth();
  
  // Sol ve sağ kutuplar
  poleA = new PVector(width * 0.28, height * 0.5);
  poleB = new PVector(width * 0.72, height * 0.5);
  
  particles = new MParticle[NUM_PARTICLES];
  for (int i = 0; i < NUM_PARTICLES; i++) {
    particles[i] = new MParticle();
  }
}

void draw() {
  fill(0, 0, 9, 16);
  noStroke();
  rect(0, 0, width, height);
  
  for (MParticle p : particles) {
    p.update();
    p.show();
    if (p.isDead()) p.reset();
  }
  
  // Kutupları ince halo ile göster
  drawPoles();
  
  if (frameCount == 320) {
    saveFrame("MagneticStorm.png");
    println("Kaydedildi!");
  }
}

void drawPoles() {
  noFill();
  // Kutup A — mor
  for (int r = 4; r < 22; r += 5) {
    stroke(280, 70, 80, map(r, 4, 22, 50, 10));
    strokeWeight(0.8);
    ellipse(poleA.x, poleA.y, r * 2, r * 2);
  }
  // Kutup B — cyan
  for (int r = 4; r < 22; r += 5) {
    stroke(190, 70, 85, map(r, 4, 22, 50, 10));
    strokeWeight(0.8);
    ellipse(poleB.x, poleB.y, r * 2, r * 2);
  }
}

// ---- Alan yönü hesaplama ----
PVector getField(float x, float y) {
  // Kutup A'dan vektör (çekici — negatif kutup)
  PVector da = PVector.sub(new PVector(x, y), poleA);
  float dA   = da.magSq() + 1;
  da.normalize();
  da.mult(-poleStrength / dA);  // Doğruca kutba çeker
  
  // Kutup B'den vektör (iterici — pozitif kutup)
  PVector db = PVector.sub(new PVector(x, y), poleB);
  float dB   = db.magSq() + 1;
  db.normalize();
  db.mult(poleStrength / dB);   // Uzaklaştırır
  
  // Toplam manyetik vektör
  PVector mag = PVector.add(da, db);
  
  // Perlin noise pertürbasyonu
  float n = noise(x * NOISE_SCALE, y * NOISE_SCALE, frameCount * 0.001);
  float noiseAngle = n * TWO_PI * 2.5;
  PVector noiseVec = new PVector(cos(noiseAngle), sin(noiseAngle));
  noiseVec.mult(0.6);
  
  mag.add(noiseVec);
  mag.normalize();
  return mag;
}

class MParticle {
  float x, y, px, py;
  int   steps;
  float speed;
  float hueVal;
  float sw;
  float lifeAlpha;
  
  MParticle() { reset(); }
  
  void reset() {
    x  = random(width);
    y  = random(height);
    px = x; py = y;
    steps = 0;
    speed = random(SPEED * 0.5, SPEED * 1.5);
    sw    = random(0.3, 1.6);
    lifeAlpha = random(50, 90);
    
    // Manyetik palet: mor (270-300), pembe (310-340), elektrik mavi (190-220)
    float rr = random(1);
    if      (rr < 0.40) hueVal = random(270, 300);  // Mor
    else if (rr < 0.70) hueVal = random(310, 340);  // Pembe-fuşya
    else if (rr < 0.88) hueVal = random(190, 220);  // Elektrik mavi
    else                hueVal = random(  5,  25);  // Kırmızı-turuncu aksan
  }
  
  void update() {
    PVector dir = getField(x, y);
    px = x; py = y;
    x += dir.x * speed;
    y += dir.y * speed;
    steps++;
  }
  
  void show() {
    float dA  = dist(x, y, poleA.x, poleA.y);
    float dB  = dist(x, y, poleB.x, poleB.y);
    float sat = map(min(dA, dB), 0, 300, 60, 95);
    float bri = map(steps, 0, MAX_STEPS, 90, 55);
    float alp = map(steps, 0, MAX_STEPS, lifeAlpha, 15);
    
    strokeWeight(sw);
    stroke(hueVal, sat, bri, alp);
    line(px, py, x, y);
  }
  
  boolean isDead() {
    return (x < -5 || x > width + 5 || y < -5 || y > height + 5 || steps > MAX_STEPS);
  }
}
