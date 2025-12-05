

import io
from pathlib import Path
from PIL import Image
import streamlit as st

from backend.model_utils import load_model, segment_object_only

# ----------------- Helpers -----------------
def resize_image(img: Image.Image, max_width=350):
    w, h = img.size
    if w <= max_width:
        return img
    scale = max_width / w
    new_size = (max_width, int(h*scale))
    return img.resize(new_size, Image.Resampling.LANCZOS)

# ----------------- Streamlit Setup -----------------
st.set_page_config(page_title="SegMe – Smart Masking", layout="wide")

# ----------------- CSS Styling -----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
[data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #d4e7ff, #f8fbff); }
.title { font-size: 46px; font-weight: 800; text-align: center;
        background: linear-gradient(90deg, #0057ff, #4bc7ff, #007bff); -webkit-background-clip: text; color: transparent; margin-bottom: -5px;}
.subtitle { text-align: center; font-size: 20px; color: #154360; margin-bottom: 40px; }
.card { background: rgba(255,255,255,0.9); padding: 28px; border-radius: 18px; backdrop-filter: blur(10px);
        box-shadow: 0px 6px 20px rgba(0,0,0,0.09); margin-bottom: 35px; border-left: 6px solid #4A90E2; }
.section-header { font-size: 28px; font-weight: 700; background: linear-gradient(90deg, #003f78, #007bff);
                  -webkit-background-clip: text; color: transparent; }
.feature-box { background: #f4f9ff; padding: 20px; border-radius: 14px; text-align: center; box-shadow: 0 3px 10px rgba(0,0,0,0.06); transition: 0.25s; }
.feature-box:hover { transform: translateY(-3px); background: #e9f3ff; }
.feature-title { font-size: 20px; font-weight: 700; margin-top: 10px; }
.stButton > button { background: linear-gradient(90deg,#007bff,#00c6ff); color: white; font-size: 18px; padding: 10px 25px; border-radius: 12px; border: none; transition: 0.2s; }
.stButton > button:hover { transform: scale(1.03); }
.stDownloadButton > button { background: linear-gradient(90deg,#14c38e,#00a272); color: white; font-size: 18px; padding: 10px 25px; border-radius: 12px; border: none; }
.stDownloadButton > button:hover { transform: scale(1.03); }
img { border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.12); }
</style>
""", unsafe_allow_html=True)

# ----------------- Title -----------------
st.markdown("<div class='title'>SegMe — Smart Object Masking</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Fast, clean and professional masking directly from your browser</div>", unsafe_allow_html=True)

# ----------------- Features -----------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("<div class='section-header'>✨ Features</div>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("""<div class='feature-box'><div style='font-size:45px;'>🧼</div>
                   <div class='feature-title'>Background Removal</div>
                   Removes background completely.</div>""", unsafe_allow_html=True)
with c2:
    st.markdown("""<div class='feature-box'><div style='font-size:45px;'>🎯</div>
                   <div class='feature-title'>Foreground Only</div>
                   Keeps only the main subject.</div>""", unsafe_allow_html=True)
with c3:
    st.markdown("""<div class='feature-box'><div style='font-size:45px;'>⚡</div>
                   <div class='feature-title'>Fast Inference</div>
                   Runs on CPU/GPU directly in browser.</div>""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ----------------- Sample Input/Output -----------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("<div class='section-header'>📸 Sample Input & Output</div>", unsafe_allow_html=True)
BASE_DIR = Path(__file__).parent
SAMPLES_DIR = BASE_DIR.parent / "samples"

col1, col2 = st.columns(2)
if (SAMPLES_DIR/"sample_input.jpg").exists():
    col1.image(resize_image(Image.open(SAMPLES_DIR/"sample_input.jpg")), caption="Sample Input", width=340)
if (SAMPLES_DIR/"sample_output.png").exists():
    col2.image(resize_image(Image.open(SAMPLES_DIR/"sample_output.png")), caption="Sample Output", width=340)
st.markdown("</div>", unsafe_allow_html=True)

# ----------------- Try Me -----------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("<div class='section-header'>🚀 Try It Yourself</div>", unsafe_allow_html=True)
uploaded = st.file_uploader("Upload your image", type=["png","jpg","jpeg","webp"])
bg_color = st.color_picker("Pick background color", "#000000")
device = "cuda" if torch.cuda.is_available() else "cpu"
model = load_model(device)

if uploaded:
    img = Image.open(uploaded).convert("RGB")
    st.image(resize_image(img), caption="Your Image", width=350)

    if st.button("Process Image"):
        with st.spinner("Applying mask…"):
            bg = tuple(int(bg_color.lstrip("#")[i:i+2], 16) for i in (0,2,4))
            result = segment_object_only(img, model, device, bg)

        st.image(resize_image(result), caption="Output", width=350)
        buf = io.BytesIO()
        result.save(buf, format="PNG")
        buf.seek(0)
        st.download_button("Download Result", buf, "masked_output.png", "image/png")
st.markdown("</div>", unsafe_allow_html=True)






import numpy as np
import cv2
from PIL import Image
import torch
from torchvision import transforms
from torchvision.models import segmentation

# ----------------- Config -----------------
FG_THRESHOLD = 0.6
MORPH_KERNEL = 7
MORPH_ITER = 3
KEEP_LARGEST = True

# ----------------- Model loader -----------------
@torch.no_grad()
def load_model(device="cpu"):
    model = segmentation.deeplabv3_resnet50(pretrained=True, progress=False)
    model.eval()
    model.to(device)
    return model

# ----------------- Preprocessing -----------------
preprocess = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485,0.456,0.406],
                         std=[0.229,0.224,0.225])
])

def image_to_tensor(img_pil: Image.Image, device="cpu"):
    return preprocess(img_pil).unsqueeze(0).to(device)

# ----------------- Mask Helpers -----------------
def keep_largest_component(mask_np):
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask_np, 8)
    if num_labels <= 1:
        return mask_np
    areas = stats[1:, cv2.CC_STAT_AREA]
    largest_label = 1 + int(np.argmax(areas))
    return (labels == largest_label).astype("uint8") * 255

def refine_mask(prob_map):
    bin_mask = (prob_map >= FG_THRESHOLD).astype("uint8") * 255
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (MORPH_KERNEL,MORPH_KERNEL))
    cleaned = cv2.morphologyEx(bin_mask, cv2.MORPH_CLOSE, kernel, iterations=MORPH_ITER)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel, iterations=MORPH_ITER)
    if KEEP_LARGEST:
        cleaned = keep_largest_component(cleaned)
    return cleaned

def sharpen_image(img):
    blur = cv2.GaussianBlur(img, (0,0), 3)
    sharp = cv2.addWeighted(img, 1.7, blur, -0.7, 0)
    return np.clip(sharp, 0, 255).astype("uint8")

# ----------------- Core Segmentation -----------------
def segment_object_only(img_pil: Image.Image, model, device="cpu", bg_color=(0,0,0)):
    tensor = image_to_tensor(img_pil, device)
    out = model(tensor)
    logits = out['out'][0]
    probs = torch.softmax(logits, dim=0).cpu().numpy()

    fg_prob = np.max(probs[1:], axis=0)
    img_w, img_h = img_pil.size
    fg_prob_resized = cv2.resize(fg_prob, (img_w,img_h), cv2.INTER_NEAREST)
    bin_mask = refine_mask(fg_prob_resized)

    src = np.array(img_pil).astype("float32")/255.0
    bg = np.ones_like(src) * (np.array(bg_color)/255.0)
    alpha = (bin_mask/255)[:, :, None]
    out_rgb = src*alpha + bg*(1-alpha)

    return Image.fromarray(sharpen_image(out_rgb))
