# Visual Changes Guide - Nuvem de Palavras

## 1. Dynamic Creation Form

### Before:
```
┌─────────────────────────────────────┐
│ Tipo                                │
│ ┌─────────────────────────────────┐ │
│ │ Palavra única            ▼      │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

### After:
```
┌─────────────────────────────────────┐
│ Tipo                                │
│ ┌─────────────────────────────────┐ │
│ │ Nuvem de Palavras        ▼      │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

---

## 2. Response Form

### Before:
```
┌────────────────────────────────────────────┐
│ Digite até 3 palavras                      │
│ ┌────────────────────────────────────────┐ │
│ │                                        │ │
│ └────────────────────────────────────────┘ │
│                                            │
│ ┌──────────┐                               │
│ │  Enviar  │                               │
│ └──────────┘                               │
└────────────────────────────────────────────┘
```

### After:
```
┌────────────────────────────────────────────┐
│ Palavra 1                                  │
│ ┌────────────────────────────────────────┐ │
│ │                                        │ │ ← Required
│ └────────────────────────────────────────┘ │
│                                            │
│ Palavra 2                                  │
│ ┌────────────────────────────────────────┐ │
│ │                                        │ │ ← Optional
│ └────────────────────────────────────────┘ │
│                                            │
│ Palavra 3                                  │
│ ┌────────────────────────────────────────┐ │
│ │                                        │ │ ← Optional
│ └────────────────────────────────────────┘ │
│                                            │
│ ┌──────────┐                               │
│ │  Enviar  │                               │
│ └──────────┘                               │
└────────────────────────────────────────────┘
```

---

## 3. User Response Display

### Before:
```
┌────────────────────────────────────────────┐
│ ✓ Você já respondeu: substantivo verbo     │
└────────────────────────────────────────────┘
```

### After (Example with 3 words):
```
┌───────────────────────────────────────────────────┐
│ ✓ Você já respondeu: substantivo, verbo, adjetivo │
└───────────────────────────────────────────────────┘
```

### After (Example with 2 words):
```
┌──────────────────────────────────────────┐
│ ✓ Você já respondeu: substantivo, verbo  │
└──────────────────────────────────────────┘
```

### After (Example with 1 word):
```
┌────────────────────────────────────┐
│ ✓ Você já respondeu: substantivo   │
└────────────────────────────────────┘
```

---

## 4. Word Cloud Generation

### How It Works:

**Before:**
- User submits: "substantivo verbo"
- Word cloud receives: 1 entry with 2 words
- Words parsed: ["substantivo", "verbo"]

**After:**
- User submits:
  - Palavra 1: "substantivo"
  - Palavra 2: "verbo"
  - Palavra 3: "adjetivo"
- Word cloud receives: 3 separate entries
- Words collected: ["substantivo", "verbo", "adjetivo"]

Each word appears individually in the cloud with proper frequency counting!

---

## 5. CSV Export Format

### Before:
```csv
timestamp,dynamic_id,usuario_id,tipo,content
2025-01-15T10:30:00,1,123,oneword,substantivo verbo
```

### After (3 words):
```csv
timestamp,dynamic_id,usuario_id,tipo,content
2025-01-15T10:30:00,1,123,oneword,"substantivo, verbo, adjetivo"
```

### After (2 words):
```csv
timestamp,dynamic_id,usuario_id,tipo,content
2025-01-15T10:30:00,1,123,oneword,"substantivo, verbo"
```

### After (1 word):
```csv
timestamp,dynamic_id,usuario_id,tipo,content
2025-01-15T10:30:00,1,123,oneword,substantivo
```

---

## Key Visual Improvements

### 1. **Clearer Intent** 🎯
   - Name changed from "Palavra única" → "Nuvem de Palavras"
   - Better describes what users will create

### 2. **Better Input Organization** 📝
   - 3 distinct input fields instead of 1
   - Clear labels: "Palavra 1", "Palavra 2", "Palavra 3"
   - Visual separation makes it obvious each is independent

### 3. **Flexible Submission** ✨
   - Users can submit 1, 2, or 3 words
   - Only first field required
   - No confusion about word limits

### 4. **Improved Response Display** 👁️
   - Shows all submitted words clearly
   - Comma-separated for readability
   - Conditional display (doesn't show empty fields)

### 5. **Enhanced Word Cloud** ☁️
   - Each word contributes individually to frequency
   - More accurate word cloud generation
   - Better visualization of contributions

---

## User Flow Example

### Scenario: Teacher creates "Classes Gramaticais" dynamic

1. **Create Dynamic:**
   - Select "Nuvem de Palavras" from dropdown ✓
   - Title: "Classes Gramaticais"
   - Description: "Cite 3 classes gramaticais que você conhece"

2. **Students Respond:**
   
   **Student 1:**
   - Palavra 1: substantivo ✓
   - Palavra 2: verbo ✓
   - Palavra 3: adjetivo ✓
   
   **Student 2:**
   - Palavra 1: pronome ✓
   - Palavra 2: artigo ✓
   - Palavra 3: (empty)
   
   **Student 3:**
   - Palavra 1: substantivo ✓
   - Palavra 2: (empty)
   - Palavra 3: (empty)

3. **Word Cloud Shows:**
   ```
   SUBSTANTIVO (appears larger - 2 occurrences)
   verbo    adjetivo    pronome    artigo
   ```

4. **CSV Export:**
   ```csv
   timestamp,dynamic_id,usuario_id,tipo,content
   2025-01-15T10:30:00,1,1,oneword,"substantivo, verbo, adjetivo"
   2025-01-15T10:31:00,1,2,oneword,"pronome, artigo"
   2025-01-15T10:32:00,1,3,oneword,substantivo
   ```

---

## Technical Notes

- **Backwards Compatible**: Old single-word responses still display correctly
- **No Breaking Changes**: Existing data preserved
- **Validation**: 50 chars per field max (allows compound words like "guarda-chuva")
- **Required Fields**: Only Palavra 1 is required
- **Data Format**: JSON payload with word1, word2, word3 keys
