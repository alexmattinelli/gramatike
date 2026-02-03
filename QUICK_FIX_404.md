# 🚨 QUICK FIX: Erro 404 no Mobile

## Sintoma
```
Error 404 - Object not found
This object does not exist or is not publicly accessible at this URL
```

## Solução Rápida (5 minutos)

### 1️⃣ Acesse o Cloudflare Dashboard
👉 https://dash.cloudflare.com/ → **R2**

### 2️⃣ Selecione seu bucket
Clique em **"bucket"** ou **"gramatike"** na lista

### 3️⃣ Habilite Public Access
1. Vá em **Settings**
2. Role até **Public Access**
3. Clique em **"Allow Access"** ou **"Connect Domain"**
4. Selecione **"R2.dev subdomain"**
5. Clique em **"Save"** ou **"Allow Access"**

### 4️⃣ Configure CORS
Ainda em Settings, encontre **CORS policy**:

```json
[
  {
    "AllowedOrigins": ["https://www.gramatike.com.br", "https://*.pages.dev"],
    "AllowedMethods": ["GET", "HEAD"],
    "AllowedHeaders": ["*"],
    "MaxAgeSeconds": 3600
  }
]
```

### 5️⃣ Teste
- Limpe o cache do navegador
- Acesse o site no celular
- ✅ As imagens devem aparecer!

---

**📖 Guia Completo:** [R2_PUBLIC_ACCESS_SETUP.md](R2_PUBLIC_ACCESS_SETUP.md)

**⏱️ Tempo estimado:** 5-10 minutos
