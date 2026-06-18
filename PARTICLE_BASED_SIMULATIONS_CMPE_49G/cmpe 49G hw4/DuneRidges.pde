// ============================================================
// "Dune Ridges" — Topografik Perlin Noise Kontur Haritası
// CmpE49G Project 3 — Visual 3
// ============================================================
// Teknik: 2D Perlin noise yüzeyi belirli eşik değerlerinde
// kesilir; her kesit bir kontur çizgisi oluşturur.
// Bias: Y ekseninde noise ölçeği değişir → alttan ince üstten
//       geniş konturlar (çöl kumulları efekti).
// Renk: Sıcak kum rengi paleti, altta koyu üstte açık.
// ============================================================

int   COLS = 400;
int   ROWS = 250;
int   LEVELS = 28;    // Kontur sayısı

float[][] field;

void setup() {
  size(1200, 750);
  background(18, 12, 8);
  noLoop();           // Tek seferlik render
}

void draw() {
  colorMode(HSB, 360, 100, 100, 100);
  
  float xScale = (float) width  / COLS;
  float yScale = (float) height / ROWS;
  
  // Noise alanını doldur
  field = new float[COLS + 1][ROWS + 1];
  
  float noiseBase = random(1000);
  for (int j = 0; j <= ROWS; j++) {
    for (int i = 0; i <= COLS; i++) {
      float xoff = i * 0.006;
      // Bias: Y'ye göre noise ölçeği farklılaştır
      float yBias = map(j, 0, ROWS, 0.003, 0.012);
      float yoff = j * yBias;
      field[i][j] = noise(noiseBase + xoff, noiseBase + yoff);
    }
  }
  
  // Her kontur seviyesini çiz
  for (int lv = 0; lv < LEVELS; lv++) {
    float threshold = map(lv, 0, LEVELS - 1, 0.22, 0.78);
    
    // Renk: Sıcak kum/çöl — alt koyudan üste açığa
    float hue = map(lv, 0, LEVELS - 1, 22, 42);
    float sat = map(lv, 0, LEVELS - 1, 75, 45);
    float bri = map(lv, 0, LEVELS - 1, 38, 88);
    float alp = map(lv, 0, LEVELS - 1, 60, 90);
    float sw  = map(lv, 0, LEVELS - 1, 0.4, 1.8);
    
    stroke(hue, sat, bri, alp);
    strokeWeight(sw);
    noFill();
    
    // Marching squares lite: her hücrenin 4 kenarını tara
    for (int j = 0; j < ROWS; j++) {
      for (int i = 0; i < COLS; i++) {
        float v00 = field[i][j];
        float v10 = field[i+1][j];
        float v01 = field[i][j+1];
        float v11 = field[i+1][j+1];
        
        float x0 = i * xScale, x1 = (i+1) * xScale;
        float y0 = j * yScale, y1 = (j+1) * yScale;
        
        // Sol kenar kesişimi
        PVector left  = edgePoint(v00, v01, threshold, x0, y0, x0, y1);
        // Sağ kenar kesişimi
        PVector right = edgePoint(v10, v11, threshold, x1, y0, x1, y1);
        // Üst kenar kesişimi
        PVector top   = edgePoint(v00, v10, threshold, x0, y0, x1, y0);
        // Alt kenar kesişimi
        PVector bot   = edgePoint(v01, v11, threshold, x0, y1, x1, y1);
        
        // Kaç nokta var?
        ArrayList<PVector> pts = new ArrayList<PVector>();
        if (left  != null) pts.add(left);
        if (right != null) pts.add(right);
        if (top   != null) pts.add(top);
        if (bot   != null) pts.add(bot);
        
        if (pts.size() == 2) {
          line(pts.get(0).x, pts.get(0).y, pts.get(1).x, pts.get(1).y);
        }
      }
    }
  }
  
  saveFrame("DuneRidges.png");
  println("Dune Ridges kaydedildi!");
}

// İki köşe arasındaki eşik kesişim noktası (lineer interpolasyon)
PVector edgePoint(float va, float vb, float threshold, 
                  float xa, float ya, float xb, float yb) {
  if ((va < threshold) == (vb < threshold)) return null;  // Kesişim yok
  float t = (threshold - va) / (vb - va);
  return new PVector(lerp(xa, xb, t), lerp(ya, yb, t));
}
