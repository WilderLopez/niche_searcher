# MVP — App de antigüedades (nombre en clave: **Trove**)

> "El identificador de antigüedades **honesto**, con una colección nativa de verdad."
> Identificar + valorar es el anzuelo; **la colección es el producto**.

Documento vivo. Lo construimos como team **Claude Code + tú**. Todo aquí sale de la
investigación previa (nichos → clone score → minería de reseñas → viabilidad de datos).

---

## 1. Por qué esta app y por qué así

De la minería de reseñas de los líderes (AntiqSnap, etc.) salieron 3 verdades:

1. **La queja #1 (≈50% de las negativas) es el paywall tramposo.** → Nuestra bandera: **honestidad**.
2. **La valoración y el ID fallan y se quedan cortos.** → Ser **honestos con la incertidumbre** (rango + "es una estimación, no una tasación") en vez de sobreprometer.
3. **Los usuarios SUPLICAN gestionar su colección** (notas, campos propios, valor en el tiempo, exportar/compartir). → **La colección es el core**, no la identificación.

Ventaja de elegir antigüedades (vs cartas): **dependencia de datos casi nula**. No hay
catálogo rígido ni feed de precios de terceros hostiles. Una API de visión IA hace el 80%,
y el público **acepta un valor en rango**.

## 2. Usuario objetivo (US)

- **Thrifters / revendedores** ("rastreo cada tesoro que compro de segunda mano").
- **Herederos / vaciado de casas** (heredé cosas, ¿qué valen?).
- **Coleccionistas aficionados** que quieren **catalogar** lo suyo.

## 3. La cuña, hecha reglas de producto (no negociable)

- **Paywall honesto:** free tier real (identificaciones gratis, **sin pedir tarjeta**), precio claro, cómo cancelar visible, sin cuentas atrás engañosas.
- **Honestidad con el valor:** siempre **rango + confianza + "estimación IA, no tasación"**. Nunca un número único falsamente preciso.
- **Sin anuncios. Nunca.**
- **La colección es tuya:** export/compartir de verdad; nada de secuestrar tus datos.

---

## 4. Alcance v1 (MoSCoW — feroz)

### MUST (v1)
- **Capturar → Identificar:** foto → resultado (qué es, categoría, época, material, descripción, **rango de valor** + confianza).
- **Guardar en Mi Colección:** ítem con foto(s), datos de la IA, **notas y campos editables** (estado, procedencia, precio de compra).
- **Mi Colección:** lista + detalle, buscar/filtrar por texto y etiquetas, **valor total** de la colección.
- **Paywall honesto** (RevenueCat): N identificaciones gratis, luego suscripción.
- **Valor honesto + "Ver ventas similares"**: deep-link a la búsqueda de eBay (sin API, 100% legal).
- **Sync iCloud** (SwiftData + CloudKit) para no perder la colección.

### SHOULD (v1.1, si da tiempo)
- **Widget** de pantalla de inicio (valor / nº de ítems).
- **Exportar** la colección a PDF/CSV; **compartir** ítem (Share Sheet).
- Multi-foto por ítem (mejora el ID).

### WON'T (fuera de v1 — explícito)
- ❌ Integración de **venta** en eBay (Sell API) → v2.
- ❌ **Grading**/tasación "oficial".
- ❌ Cuentas/login propio (usamos iCloud, cero fricción).
- ❌ Social/comunidad.
- ❌ Feed de precios de terceros de pago (no hace falta en antigüedades).

---

## 5. Flujo y pantallas (SwiftUI, UI estándar, sin diseño complejo)

1. **Onboarding** (2–3 pantallas): qué hace + permiso de cámara + promesa honesta ("N gratis, sin tarjeta").
2. **Capturar** (`CameraView`): cámara o elegir de fotos → spinner "Analizando…".
3. **Resultado** (`IdentifyResultView`): tarjeta con nombre, categoría, época, material, descripción, **rango de valor + confianza + disclaimer**, botones **[Guardar en colección]** y **[Ver ventas similares ↗]**.
4. **Mi Colección** (`CollectionListView`): lista con miniatura, título, rango de valor; barra superior con **valor total**; buscar + filtro por etiqueta.
5. **Detalle del ítem** (`ItemDetailView`): fotos, datos IA, **campos editables** (notas, estado, procedencia, precio de compra, etiquetas, ⭐), acciones compartir/eliminar.
6. **Paywall** (`PaywallView`, RevenueCat): transparente, precio claro, "cancela cuando quieras".
7. **Ajustes** (`SettingsView`): estado de suscripción, restaurar compras, exportar, privacidad.

Todas son listas / formularios / detalle → **componentes estándar de SwiftUI**. Nada que requiera un diseñador.

---

## 6. Arquitectura y stack

```
[App iOS SwiftUI]
   │  foto + entitlement
   ▼
[Backend proxy mínimo]  ← guarda la API key, valida free-tier/suscripción server-side
   │  prompt estructurado + imagen
   ▼
[Claude Vision API]  → JSON {nombre, categoría, época, material, descripción,
                              valor_min, valor_max, confianza, rationale}
```

| Capa | Elección | Por qué |
|---|---|---|
| UI | **SwiftUI** | Nativo, rápido con Claude, sin diseño complejo |
| Persistencia | **SwiftData + CloudKit** | Local + sync iCloud sin backend de datos propio |
| IA de visión | **Claude** (`claude-haiku-4-5` por coste; `claude-sonnet-5` para casos difíciles) | Identificación abierta + estimación de valor en rango; somos team Claude |
| Backend | **Función serverless mínima** (Cloudflare Worker / Vercel) | **Nunca** poner la API key en el cliente; enforce del free-tier server-side |
| Suscripciones | **RevenueCat** | Estándar iOS, paywall honesto, gratis bajo ~$2.5k/mes. *(Su MCP ya está conectado en esta sesión.)* |
| Analítica (opcional) | Amplitude / TelemetryDeck | Medir activación y conversión sin dark patterns |

**Modelo de datos (SwiftData):** `Item { id, createdAt, photos, title, category, era, maker, materials, aiDescription, valueLow, valueHigh, currency, confidence, condition, provenance, purchasePrice?, notes, tags[], isFavorite, forSale }`. Etiquetas en vez de carpetas para simplificar v1.

**Valoración honesta (clave, y legal):** el modelo devuelve un **rango + confianza + rationale**, mostrado como *"estimación de IA, no una tasación"*. Para comparables reales, **deep-link** a la búsqueda de vendidos de eBay (`ebay.com/sch/...&LH_Sold=1&LH_Complete=1`) — abrimos Safari/app de eBay, **sin tocar su API** → 0 riesgo legal (justo lo que la investigación descartó por API queda resuelto por deep-link).

---

## 7. Monetización (honesta, sin ads)

- **Free:** p.ej. **5 identificaciones gratis** (sin tarjeta) + colección ilimitada de lo ya identificado.
- **Trove Pro (suscripción):** identificaciones ilimitadas, multi-foto, export, widget, valor en el tiempo.
- **Precio de partida a validar:** ~**$4.99/mes** o **$29.99/año** (ancla anual). Ajustable con RevenueCat sin recompilar.
- **Principios anti-dark-pattern** (nuestro diferenciador): sin pedir tarjeta para el free, "cancela cuando quieras" visible, sin cuenta atrás agresiva. Esto es *marketing*: lo decimos en la ficha y en el paywall.

**Coste operativo a escala pequeña:** datos ≈ **$0** (sin feed de precios) · IA de visión ≈ céntimos por identificación (acotado por el free-tier) · backend y RevenueCat en tier gratis · Apple Developer $99/año. **Arranque casi a coste cero.**

---

## 8. Toque nativo (nuestra ventaja sobre las clones cross-platform)

- **Widget** con el valor / nº de ítems de tu colección.
- **Share Sheet**: añadir ítem desde una foto compartida.
- **Shortcuts / Spotlight** para "Identificar antigüedad".
- **iCloud sync** transparente.
- Rendimiento y pulido Apple (justo donde las clones fallan).

---

## 9. Plan de construcción (milestones — team Claude + tú)

| Hito | Qué entregamos | Yo (Claude) | Tú |
|---|---|---|---|
| **M0 — Setup** | Proyecto Xcode, repo, CLAUDE.md, RevenueCat + backend vacío desplegado | Estructura, scaffolding, CLAUDE.md, config | Cuenta Apple Dev, claves, crear proyecto |
| **M1 — La magia** | Foto → backend → Claude → tarjeta de resultado | Prompt estructurado, backend proxy, parsing, `IdentifyResultView` | Probar con objetos reales |
| **M2 — Colección** | Guardar, listar, detalle, editar, SwiftData+CloudKit | Modelo, vistas, sync | Feedback de UX |
| **M3 — Valor** | Rango + confianza + disclaimer + deep-link eBay | Formato del valor, deep-link | Validar utilidad |
| **M4 — Paywall honesto** | RevenueCat, free-tier server-side, `PaywallView` | Integración, enforcement, copy honesto | Configurar productos en App Store Connect |
| **M5 — Nativo** | Widget, share, export, estados vacíos, pulido | Todo el código | QA en tu iPhone |
| **M6 — Beta → Store** | TestFlight, iterar con reseñas, ASO, envío | Fixes, textos ASO (título/subtítulo/keywords) | Reclutar testers, screenshots, enviar |

**Objetivo realista:** ~**4–6 semanas** a TestFlight con este ritmo.

**ASO desde el día 1** (lo aprendimos como diferenciador): título/subtítulo/keywords centrados en *antique identifier / value / collection*, y la ficha vende la **honestidad** (el hueco emocional que dejan los líderes).

---

## 10. Riesgos y decisiones abiertas

- **Calidad del ID/valor de la IA**: mitigar con multi-foto, prompt afinado y disclaimers honestos. Probar pronto con objetos reales (M1).
- **Coste de IA si escala**: acotado por free-tier + caché; subir a Sonnet solo en casos difíciles.
- **Decisiones tuyas:** (a) nombre definitivo (Trove es provisional; verificar ASO/marca), (b) precio de partida, (c) proveedor de visión (por defecto Claude).

---

## 11. Primer paso concreto (M0)

1. Crear el proyecto Xcode (SwiftUI, iOS 17+, SwiftData+CloudKit) y su repo.
2. Yo genero el **scaffolding + CLAUDE.md** del proyecto y el **backend proxy mínimo** (una función que recibe imagen → llama a Claude → devuelve el JSON estructurado).
3. Cerramos el **prompt de identificación** (el corazón de la magia) y lo probamos con 5–10 fotos reales.
