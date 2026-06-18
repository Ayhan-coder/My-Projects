// ============================================================
// "Cosmos Breath" — Dairesel Bias + Perlin Noise Diffusion
// CmpE49G Project 3 — Visual 2
// ============================================================
// Teknik: Parçacıklar merkezden dışa yayılır. Perlin noise
// açıyı bozar, organik kıvrımlar oluşturur.
// Bias: Merkeze olan mesafe → yayılma gücünü belirler.
// Renk: Mesafeye göre mor→cyan→yeşil gradyanı.
// ============================================================

int   NUM_PARTICLES = 5000;
float NOISE_SCALE   = 0.003;
float SPEED_BASE    = 1.8;
int   MAX_STEPS     = 120;

CParticle[] particles;

void setup() {
  size(1200, 750);
  background(6, 5, 18);
  colorMode(HSB, 360, 100, 100, 100);
  smooth();
  
  particles = new CParticle[NUM_PARTICLES];
  for (int i = 0; i < NUM_PARTICLES; i++) {
    particles[i] = new CParticle();
  }
}

void draw() {
  fill(0, 0, 7, 14);
  noStroke();
  rect(0, 0, width, height);
  
  for (CParticle p : particles) {
    p.update();
    p.show();
    if (p.isDead()) p.reset();
  }
  
  if (frameCount == 350) {
    saveFrame("CosmoBreath.png");
    println("Kaydedildi!");
  }
}

class CParticle {
  float x, y, px, py;
  float speed;
  int   steps;
  float baseAngle;   // Merkezden dışa temel açı
  float hueVal;
  float sw;
  
  CParticle() { reset(); }
  
  void reset() {
    // Merkez etrafında küçük daire içinde doğ
    float cx = width / 2.0, cy = height / 2.0;
    float r  = random(5, 60);
    float a  = random(TWO_PI);
    x  = cx + cos(a) * r;
    y  = cy + sin(a) * r;
    px = x;
    py = y;
    
    baseAngle = atan2(y - cy, x - cx);
    speed     = random(SPEED_BASE * 0.5, SPEED_BASE * 1.5);
    steps     = 0;
    sw        = random(0.3, 1.4);
    
    // Renk: rastgele ama belirli hue bantları
    float rr = random(1);
    if      (rr < 0.35) hueVal = random(260, 300); // Mor-menekşe
    else if (rr < 0.60) hueVal = random(175, 210); // Cyan-mavi
    else if (rr < 0.80) hueVal = random(130, 165); // Yeşil
    else                hueVal = random( 30,  55);  // Altın
  }
  
  void update() {
    float cx = width / 2.0, cy = height / 2.0;
    float d  = dist(x, y, cx, cy);
    
    // Perlin noise bileşeni
    float n = noise(x * NOISE_SCALE, y * NOISE_SCALE, frameCount * 0.0005);
    float noiseAngle = n * TWO_PI * 3;
    
    // Bias: Merkezden uzaklaştıkça noise daha az etkili
    float biasWeight = constrain(map(d, 0, width * 0.5, 0.85, 0.15), 0.1, 0.95);
    float angle = lerp(noiseAngle, baseAngle, biasWeight);
    
    // Mesafeye göre hız: Uzaklaştıkça biraz yavaşla
    float spd = speed * map(d, 0, width * 0.6, 1.2, 0.5);
    
    px = x; py = y;
    x += cos(angle) * spd;
    y += sin(angle) * spd;
    steps++;
    
    // Mesafe arttıkça hue hafif kayma
    hueVal = (hueVal + 0.08) % 360;
  }
  
  void show() {
    float d   = dist(x, y, width/2.0, height/2.0);
    float sat = map(d, 0, width * 0.5, 50, 90);
    float bri = map(d, 0, width * 0.5, 85, 65);
    float alp = map(steps, 0, MAX_STEPS, 75, 20);
    
    strokeWeight(sw);
    stroke(hueVal, sat, bri, alp);
    line(px, py, x, y);
  }
  
  boolean isDead() {
    return (x < -10 || x > width + 10 || y < -10 || y > height + 10 || steps > MAX_STEPS);
  }
}
