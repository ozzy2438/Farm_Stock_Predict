# 🌾 Agricultural Risk Dashboard - Interactive Analytics Platform

## 📊 Overview

Bu proje, **agricultural_risk_analysis.xlsx** verisinden oluşturulmuş, son derece interaktif ve görsel olarak zenginleştirilmiş bir dashboard sistemidir. PyNarrative ve Altair kullanılarak oluşturulan dashboardlar, audience'ın dikkatini kritik alanlara yönlendirmek için özel annotations içerir.

## 🎯 Oluşturulan Dosyalar

### 📈 Interactive HTML Dashboards (Tarayıcıda Açın)

1. **[dashboard_1_trends_annotated.html](dashboard_1_trends_annotated.html)**
   - 📊 **İçerik**: Risk trendleri zaman serisi (2010-2024)
   - 🎯 **Annotations**:
     - 🔥 2012 Historic Drought - Kritik seviyeye ulaşan risk
     - 🦠 2020 COVID-19 Disruption - Supply chain etkileri
     - ⚠️ 2022 Supply Chain Crisis - Global aksaklıklar
     - ⚠️ CRITICAL THRESHOLD çizgisi (Risk Index 75)
   - ✨ **Features**: Interactive tooltips, commodity karşılaştırma, risk zone shading

2. **[dashboard_2_states_annotated.html](dashboard_2_states_annotated.html)**
   - 🗺️ **İçerik**: En riskli 20 eyalet analizi
   - 🎯 **Annotations**:
     - Top 5 priority states **bold border** ile vurgulanmış
     - Risk zone labels: ✅ Low, ⚡ Moderate, ⚠️ High, 🔥 Critical
     - Color gradient: Yeşil → Sarı → Kırmızı
   - ✨ **Features**: Hover tooltips, risk kategorileri, eyalet sıralaması

3. **[dashboard_3_commodities_annotated.html](dashboard_3_commodities_annotated.html)**
   - 📦 **İçerik**: Commodity bazında risk dağılımı
   - 🎯 **Annotations**:
     - Box plot ile quartile analizi
     - 💎 Diamond markers ile mean değerleri
     - İstatistiksel overlay'ler
   - ✨ **Features**: Outlier detection, median/mean gösterimi, distribution analysis

4. **[dashboard_4_drought_annotated.html](dashboard_4_drought_annotated.html)**
   - 💧 **İçerik**: Drought index vs Risk index korelasyonu
   - 🎯 **Annotations**:
     - 📈 Correlation coefficient gösterimi
     - Regression line (trend)
     - Risk kategorisi ile renklendirme
     - Bubble size = Crop yield
   - ✨ **Features**: Scatter plot, regression analysis, multi-dimensional visualization

### 🎬 Animated GIF

**[agricultural_dashboard_animated.gif](agricultural_dashboard_animated.gif)**
- 🎞️ **Süre**: 12 saniye (4 frame × 3 saniye)
- 💾 **Boyut**: ~140 KB
- 📊 **İçerik**: Tüm 4 dashboard'un sıralı gösterimi
- 🎯 **Kullanım**: Sunumlarda, raporlarda, hızlı paylaşımda

## 🎨 Görsel Özellikler

### Color Palette
- 🟢 **Green (#388e3c)**: Low risk (0-25)
- 🟡 **Yellow (#fbc02d)**: Moderate risk (25-50)
- 🟠 **Orange (#f57c00)**: High risk (50-75)
- 🔴 **Red (#d32f2f)**: Critical risk (75-100)
- 🔵 **Blue (#1976d2)**: Statistical elements

### Annotations Strategy
1. **Event Markers**: Kritik olayları vurgular (drought, COVID-19, etc.)
2. **Threshold Lines**: Risk eşiklerini gösterir
3. **Statistical Overlays**: Mean, median, quartile bilgileri
4. **Color Coding**: Instant risk recognition
5. **Bold Highlights**: Top priority items
6. **Interactive Tooltips**: Detailed information on hover

## 📈 Veri Özeti

```
📊 Total Records: 1,965
📅 Time Period: 2010-2025
🗺️ States: 50
🌾 Commodities: CORN, SOYBEANS, WHEAT
📈 Average Risk Index: ~50-55
🔥 Highest Risk: Varies by year (see Chart 2)
```

## 🚀 Kullanım

### Interactive Dashboards
```bash
# Herhangi bir HTML dosyasını tarayıcınızda açın
open dashboard_1_trends_annotated.html
open dashboard_2_states_annotated.html
open dashboard_3_commodities_annotated.html
open dashboard_4_drought_annotated.html
```

### GIF Preview
```bash
# GIF'i görüntüle
open agricultural_dashboard_animated.gif
```

### Script'leri Yeniden Çalıştırma
```bash
# Dashboardları yeniden oluştur
python interactive_dashboard_annotated.py

# GIF'i yeniden oluştur
python create_dashboard_gif.py
```

## 🛠️ Teknolojiler

- **Altair**: Declarative statistical visualization
- **PyNarrative**: Data storytelling ve annotations
- **Pandas**: Data manipulation
- **Selenium**: HTML screenshot capturing
- **Pillow**: GIF creation
- **Vega-Lite**: Altair backend

## 📊 Dashboard Detayları

### Chart 1: Trend Analysis
- **Amaç**: Zaman içinde risk değişimlerini izleme
- **Dikkat Noktaları**:
  - 2012 drought peak
  - 2020 COVID impact
  - 2022 supply chain crisis
- **Actionable Insight**: Historical patterns ile future risk prediction

### Chart 2: Geographic Analysis
- **Amaç**: En riskli bölgeleri belirleme
- **Dikkat Noktaları**:
  - Top 5 priority states
  - Regional patterns
  - Risk concentration
- **Actionable Insight**: Resource allocation, procurement strategy

### Chart 3: Commodity Comparison
- **Amaç**: Crop type bazında risk profilleme
- **Dikkat Noktaları**:
  - Commodity-specific patterns
  - Volatility comparison
  - Outlier identification
- **Actionable Insight**: Portfolio diversification

### Chart 4: Drought Impact
- **Amaç**: Drought-risk relationship analizi
- **Dikkat Noktaları**:
  - Strong correlation (~0.7-0.8)
  - Yield impact
  - Predictive power
- **Actionable Insight**: DSCI monitoring for early warning

## 💡 Best Practices

1. **Presentations**: GIF kullanın, hızlı overview için
2. **Deep Dive**: HTML dashboards ile interactive exploration
3. **Reports**: Screenshots alın ve highlight edin
4. **Decision Making**: Chart 2 (states) ve Chart 4 (drought) kombine edin
5. **Monitoring**: Chart 1'i düzenli güncelleyin

## 🎯 Key Insights

1. **🔥 Critical Events**: 2012, 2020, 2022 yılları major disruption periods
2. **📍 Geographic Risk**: Top 5 states consistent risk gösteriyor
3. **🌾 Commodity Variance**: Wheat > Corn > Soybeans risk volatility sıralaması
4. **💧 Drought Impact**: DSCI en güçlü risk predictor (correlation > 0.7)

## 📞 Kullanım Senaryoları

### 1. Executive Presentation
- GIF ile başla
- Chart 2 ile priority states göster
- Chart 4 ile drought strategy konuş

### 2. Risk Assessment Meeting
- Chart 1 ile historical trend
- Chart 3 ile commodity breakdown
- Chart 2 ile geographic focus

### 3. Procurement Planning
- Chart 2 → Top risk states
- Chart 4 → Current DSCI levels
- Chart 3 → Commodity alternatives

### 4. Stakeholder Report
- Tüm HTML dashboards
- GIF as summary
- Screenshots with annotations

---

## 🎉 Sonuç

Bu dashboard sistemi, **agricultural risk analysis** verisini fully interactive, highly annotated, ve audience-focused bir formata dönüştürür. PyNarrative ve Altair'in gücüyle:

✅ **Interactive**: Hover, zoom, filter
✅ **Annotated**: Key events, thresholds, insights
✅ **Attention-Guiding**: Colors, highlights, markers
✅ **Multi-Format**: HTML (interactive) + GIF (shareable)
✅ **Professional**: Publication-ready quality

**🚀 Ready to explore! Open the HTML files and start interacting!**
