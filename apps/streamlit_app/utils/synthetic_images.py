import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import io

def generate_conjunctiva_sample(hemoglobina: float, seed: int = 42) -> Image.Image:
    """
    Genera una imagen sintética de región de interés (ROI) conjuntival/palmar
    representativa de datasets públicos de anemia no invasiva (sin rostros de niños).
    El índice de palidez (pallor index) se correlaciona fisiológicamente con la hemoglobina.
    """
    np.random.seed(seed)
    width, height = 224, 224
    
    # Base color depending on hemoglobin (Normal Hb >= 11: rosado/rojo vascular; Anemia severa < 7: pálido/amarillento)
    # Erythrocyte vascular saturation ratio
    ratio = np.clip((hemoglobina - 5.0) / 10.0, 0.05, 1.0)
    
    r_base = int(180 + 70 * ratio)
    g_base = int(100 + 40 * (1 - ratio))
    b_base = int(100 + 50 * (1 - ratio))
    
    # Background mucosal tissue with noise
    arr = np.zeros((height, width, 3), dtype=np.uint8)
    noise_r = np.random.normal(0, 12, (height, width))
    noise_g = np.random.normal(0, 10, (height, width))
    noise_b = np.random.normal(0, 10, (height, width))
    
    arr[:, :, 0] = np.clip(r_base + noise_r, 0, 255)
    arr[:, :, 1] = np.clip(g_base + noise_g, 0, 255)
    arr[:, :, 2] = np.clip(b_base + noise_b, 0, 255)
    
    img = Image.fromarray(arr, 'RGB')
    draw = ImageDraw.Draw(img)
    
    # Draw micro-vascular structures (capilares conjuntivales)
    num_vessels = int(15 * ratio + 3)
    for _ in range(num_vessels):
        x1 = np.random.randint(10, width - 10)
        y1 = np.random.randint(10, height - 10)
        x2 = x1 + np.random.randint(-40, 40)
        y2 = y1 + np.random.randint(-40, 40)
        vessel_color = (
            int(min(255, r_base + 30)),
            int(max(20, g_base - 40)),
            int(max(20, b_base - 40))
        )
        draw.line([(x1, y1), (x2, y2)], fill=vessel_color, width=np.random.randint(1, 3))
        
    img = img.filter(ImageFilter.GaussianBlur(radius=0.8))
    return img

def get_demo_image_batch(n_samples: int = 8, seed: int = 42):
    """
    Genera un lote representativo de muestras con metadata asociada.
    """
    samples = []
    np.random.seed(seed)
    for i in range(n_samples):
        hb = round(float(np.random.normal(10.2, 1.8)), 1)
        hb = max(6.0, min(14.5, hb))
        img = generate_conjunctiva_sample(hb, seed=seed + i)
        
        estado = "Normal" if hb >= 11.0 else ("Leve" if hb >= 10.0 else ("Moderada" if hb >= 7.0 else "Severa"))
        samples.append({
            "id": f"IMG-PE-{1001 + i}",
            "hemoglobina_g_dl": hb,
            "estado_anemia": estado,
            "region_anatomica": "Conjuntiva Palpebral Inferior",
            "image": img
        })
    return samples

