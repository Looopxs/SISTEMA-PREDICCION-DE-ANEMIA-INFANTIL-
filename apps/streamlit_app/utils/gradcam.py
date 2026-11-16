import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.cm as cm

class SimpleBiomedicalCNN(nn.Module):
    """
    CNN liviana y eficiente para análisis de biomarcadores conjuntivales/palmares.
    Diseñada con capas convolucionales y pooling para explicabilidad visual Grad-CAM++.
    """
    def __init__(self, num_classes: int = 2):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 16, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(16)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(32)
        self.conv3 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(64)
        self.pool = nn.MaxPool2d(2, 2)
        self.adaptive_pool = nn.AdaptiveAvgPool2d((7, 7))
        self.fc1 = nn.Linear(64 * 7 * 7, 64)
        self.dropout = nn.Dropout(0.3)
        self.fc2 = nn.Linear(64, num_classes)
        
    def forward(self, x):
        x = self.pool(F.relu(self.bn1(self.conv1(x))))
        x = self.pool(F.relu(self.bn2(self.conv2(x))))
        x = self.pool(F.relu(self.bn3(self.conv3(x))))
        x = self.adaptive_pool(x)
        x = torch.flatten(x, 1)
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x

class GradCAMPlusPlus:
    """
    Implementación rigurosa de Grad-CAM++ (Chattopadhyay et al.) para redes convolucionales.
    Calcula pesos ponderados de gradientes de segundo y tercer orden para capturar
    múltiples regiones discriminativas en imágenes biomédicas.
    """
    def __init__(self, model: nn.Module, target_layer: nn.Module):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        self._register_hooks()

    def _register_hooks(self):
        def forward_hook(module, input, output):
            self.activations = output

        def backward_hook(module, grad_in, grad_out):
            self.gradients = grad_out[0]

        self.target_layer.register_forward_hook(forward_hook)
        self.target_layer.register_full_backward_hook(backward_hook)

    def generate(self, input_tensor: torch.Tensor, class_idx: int = 1):
        self.model.eval()
        self.model.zero_grad()
        
        output = self.model(input_tensor)
        score = output[0, class_idx]
        score.backward(retain_graph=True)

        gradients = self.gradients[0] # [C, H, W]
        activations = self.activations[0] # [C, H, W]

        # Grad-CAM++ formulation:
        # alpha_k = (grad^2) / (2*grad^2 + sum(activations * grad^3) + eps)
        grad_2 = gradients.pow(2)
        grad_3 = gradients.pow(3)
        
        spatial_sum = torch.sum(activations * grad_3, dim=(1, 2), keepdim=True)
        alpha = grad_2 / (2.0 * grad_2 + spatial_sum + 1e-7)
        
        # Positive gradients contribution
        weights = torch.sum(alpha * F.relu(gradients), dim=(1, 2)) # [C]
        
        # Weighted combination of activation maps
        cam = torch.zeros(activations.shape[1:], dtype=torch.float32, device=activations.device)
        for i, w in enumerate(weights):
            cam += w * activations[i]

        cam = F.relu(cam)
        cam = cam - cam.min()
        if cam.max() > 0:
            cam = cam / cam.max()

        return cam.detach().cpu().numpy()

def generate_attention_map(input_tensor: torch.Tensor, model: nn.Module) -> np.ndarray:
    """
    Genera un mapa de atención espacial basado en la energía de activación L2 por canal.
    """
    with torch.no_grad():
        x = model.pool(F.relu(model.bn1(model.conv1(input_tensor))))
        x = model.pool(F.relu(model.bn2(model.conv2(x))))
        x = model.pool(F.relu(model.bn3(model.conv3(x))))
        
        # Energy attention map across channels
        attn = torch.mean(x[0].pow(2), dim=0).cpu().numpy()
        attn = attn - attn.min()
        if attn.max() > 0:
            attn = attn / attn.max()
        return attn

def overlay_heatmap_on_image(image_pil: Image.Image, heatmap: np.ndarray, alpha: float = 0.5, colormap_name: str = "jet") -> Image.Image:
    """
    Superpone un mapa de calor Grad-CAM++ sobre la imagen original respetando dimensiones.
    """
    w, h = image_pil.size
    # Resize heatmap to original image size
    heatmap_resized = Image.fromarray(np.uint8(255 * heatmap)).resize((w, h), Image.Resampling.BILINEAR)
    heatmap_arr = np.array(heatmap_resized) / 255.0

    try:
        import matplotlib as mpl
        if hasattr(mpl, "colormaps"):
            cmap = mpl.colormaps[colormap_name]
        elif hasattr(plt, "get_cmap"):
            cmap = plt.get_cmap(colormap_name)
        else:
            cmap = cm.get_cmap(colormap_name)
    except Exception:
        import matplotlib.pyplot as plt
        cmap = plt.get_cmap(colormap_name)
    colored_heatmap = cmap(heatmap_arr)[:, :, :3] # RGB

    img_arr = np.array(image_pil).astype(float) / 255.0
    overlay = (1 - alpha) * img_arr + alpha * colored_heatmap
    overlay = np.clip(overlay * 255, 0, 255).astype(np.uint8)
    return Image.fromarray(overlay)

def get_binary_activation_mask(heatmap: np.ndarray, threshold: float = 0.5, target_size=(224, 224)) -> Image.Image:
    """
    Genera una máscara binaria de segmentación para las regiones con mayor activación (>= threshold).
    """
    mask = (heatmap >= threshold).astype(np.uint8) * 255
    mask_img = Image.fromarray(mask).resize(target_size, Image.Resampling.NEAREST)
    return mask_img

