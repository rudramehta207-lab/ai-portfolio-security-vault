import streamlit as st
import g4f
from PIL import Image
import io
import os
import base64
import qrcode
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

st.set_page_config(page_title="AI Portfolio Vault Pro", page_icon="🛡️", layout="wide")

st.title("🛡️ Enterprise AI Portfolio Factory & Cryptographic Vault")
st.write("---")

# --- INITIALIZE SESSION STATE ---
if 'html_template' not in st.session_state:
    st.session_state['html_template'] = ""
if 'generated' not in st.session_state:
    st.session_state['generated'] = False

# --- CRYPTOGRAPHIC HELPERS (AES-256) ---
def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())

def encrypt_payload(data: str, password: str) -> str:
    salt = os.urandom(16)
    key = derive_key(password, salt)
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(data.encode('utf-8')) + encryptor.finalize()
    # Combine salt + iv + ciphertext into a single string package for steganography
    combined = salt + iv + ciphertext
    return base64.b64encode(combined).decode('utf-8')

def decrypt_payload(encrypted_b64: str, password: str) -> str:
    try:
        combined = base64.b64decode(encrypted_b64.encode('utf-8'))
        salt = combined[:16]
        iv = combined[16:32]
        ciphertext = combined[32:]
        key = derive_key(password, salt)
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_bytes = decryptor.update(ciphertext) + decryptor.finalize()
        return decrypted_bytes.decode('utf-8')
    except Exception:
        return "⚠️ DECRYPTION FAILED: Invalid secret key password or corrupted data framework."

# --- ADVANCED STEGANOGRAPHY LOGIC (LSB) ---
def hide_payload_in_image(uploaded_img, encrypted_text):
    img = Image.open(uploaded_img).convert("RGB")
    pixels = img.load()
    
    # End marker token delimiter
    binary_secret = ''.join(format(ord(char), '08b') for char in encrypted_text) + '1111111111111110'
    
    data_index = 0
    width, height = img.size
    
    if len(binary_secret) > width * height:
        raise ValueError("Payload size exceeds maximum pixel storage availability.")
        
    for y in range(height):
        for x in range(width):
            if data_index < len(binary_secret):
                r, g, b = pixels[x, y]
                r = (r & ~1) | int(binary_secret[data_index])
                pixels[x, y] = (r, g, b)
                data_index += 1
            else:
                break
    
    byte_arr = io.BytesIO()
    img.save(byte_arr, format='PNG')
    return byte_arr.getvalue()

def extract_payload_from_image(uploaded_img):
    img = Image.open(uploaded_img).convert("RGB")
    pixels = img.load()
    
    binary_data = ""
    width, height = img.size
    
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            binary_data += str(r & 1)
            
            if binary_data.endswith('1111111111111110'):
                binary_data = binary_data[:-16]
                all_bytes = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
                return "".join(chr(int(b, 2)) for b in all_bytes)
    return "No secure encrypted structural payload discovered."

# --- AI TEXT PROCESSING ---
def generate_ai_content(name, role, skills, bio):
    prompt = f"System: Elite tech writer. Provide ONLY the final bio statement. No filler text.\nUser: Make a crisp 3-sentence expert bio for {name}, working as a {role}, possessing skills: {skills}. Background context: {bio}"
    try:
        return g4f.ChatCompletion.create(model=g4f.models.gpt_4, messages=[{"role": "user", "content": prompt}])
    except Exception as e:
        return f"Error: {str(e)}"

# --- INTERACTIVE INTERFACE TABS ---
tab1, tab2 = st.tabs(["🚀 Advanced System Studio & Encoder", "🔓 AES Cryptographic Decryption Engine"])

with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🧑‍💻 Workspace Profile Parameters")
        name = st.text_input("Full Name", value="Rudra Mehta")
        role = st.text_input("Professional Title", value="Cybersecurity Analyst")
        skills = st.text_area("Core Technical Skills", value="Python, HTML, Cloud Security")
        bio = st.text_area("Background Context Summary", value="I am an ethical hacker focused on secure code and network defense.")
        
        st.write("---")
        st.markdown("### 🔒 Cryptography & Steganography Configuration")
        uploaded_file = st.file_uploader("Upload Cover Image Assets (PNG recommended)", type=["png", "jpg", "jpeg"])
        
        secret_msg = st.text_area("Secret Credentials / License Keys to Hide", value="Verification Auth Token: SEC-LEVEL-9942")
        crypto_pass = st.text_input("Set AES-256 Protection Password", type="password", value="CyberVaultPass123")
        
        if st.button("Compile Enterprise Vault ✨"):
            if name and role and skills and crypto_pass:
                with st.spinner("Encrypting datasets and generating infrastructure blueprints..."):
                    refined_bio = generate_ai_content(name, role, skills, bio)
                    
                    # Generate Custom QR Verification Code pointing to your verification server
                    qr = qrcode.QRCode(version=1, box_size=10, border=4)
                    qr.add_data("https://ai-portfolio-factory.netlify.app") # Your live validation domain
                    qr.make(fit=True)
                    qr_img = qr.make_image(fill_color="black", back_color="white")
                    
                    qr_buffer = io.BytesIO()
                    qr_img.save(qr_buffer, format="PNG")
                    qr_b64 = base64.b64encode(qr_buffer.getvalue()).decode()
                    
                    # Build Comprehensive HTML Page Blueprint Data Structure
                    st.session_state['html_template'] = f"""
                    <!DOCTYPE html>
                    <html lang='en'>
                    <head>
                        <meta charset='UTF-8'>
                        <title>{name} | Portfolio</title>
                        <style>
                            body {{ font-family: 'Segoe UI', sans-serif; background-color: #0d1117; color: #c9d1d9; margin: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh; }}
                            .card {{ background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 40px; max-width: 500px; text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }}
                            h1 {{ color: #58a6ff; margin-bottom: 5px; }}
                            h3 {{ color: #8b949e; font-weight: 400; margin-top: 0; }}
                            p {{ line-height: 1.6; color: #8b949e; text-align: justify; }}
                            .badge {{ background: #21262d; border: 1px solid #30363d; color: #58a6ff; padding: 6px 12px; border-radius: 20px; font-size: 14px; display: inline-block; margin: 4px; }}
                            .qr-sec {{ margin-top: 25px; background: white; padding: 10px; border-radius: 8px; display: inline-block; }}
                        </style>
                    </head>
                    <body>
                        <div class='card'>
                            <h1>{name}</h1>
                            <h3>{role}</h3>
                            <hr style='border-color: #30363d;'>
                            <p>{refined_bio}</p>
                            <div class='skills'>
                                {" ".join([f'<span class="badge">{s.strip()}</span>' for s in skills.split(',')])}
                            </div>
                            <div class='qr-sec'>
                                <p style='color: black; margin: 0 0 5px 0; font-size: 12px; font-weight: bold;'>Scan to Verify Integrity</p>
                                <img src='data:image/png;base64,{qr_b64}' width='130' height='130' alt='Verification QR Code'/>
                            </div>
                        </div>
                    </body>
                    </html>
                    """
                    st.session_state['generated'] = True
                    
                    if uploaded_file is not None:
                        # 1. AES Encrypt the message first
                        encrypted_payload = encrypt_payload(secret_msg, crypto_pass)
                        # 2. Hide the encrypted blob inside the image pixels
                        st.session_state['secure_img_bytes'] = hide_payload_in_image(uploaded_file, encrypted_payload)
            else:
                st.warning("Ensure all registration fields and crypto validation keys are assigned.")

    with col2:
        st.markdown("### 👁️ Real-Time Visual Workspace Preview")
        if st.session_state['generated']:
            # Render visual component iframe window instantly
            st.components.v1.html(st.session_state['html_template'], height=550, scrolling=True)
            
            st.write("---")
            st.markdown("### 💾 Distribution Deliverables")
            st.download_button(
                label="Download Production HTML Website File 🌐", 
                data=st.session_state['html_template'], 
                file_name="index.html", 
                mime="text/html"
            )
            if 'secure_img_bytes' in st.session_state:
                st.download_button(
                    label="Download AES-Secured Image Asset 🖼️", 
                    data=st.session_state['secure_img_bytes'], 
                    file_name="secure_profile.png", 
                    mime="image/png"
                )
        else:
            st.info("Input configurations and trigger compile parameters to render the visual workspace layer.")

with tab2:
    st.markdown("### 🔓 Production Decryption & Extraction Console")
    st.write("Upload a pixel-secured image to strip the cryptography wrapper and parse target database tables.")
    
    decode_file = st.file_uploader("Upload Encrypted Image Target (.png)", type=["png"], key="decoder_upload")
    decode_pass = st.text_input("Enter Private AES-256 Authentication Key", type="password", key="decoder_pass")
    
    if st.button("Decrypt & Decode Payload Datastream 🔍"):
        if decode_file is not None and decode_pass:
            with st.spinner("Extracting hidden pixels and running cipher calculations..."):
                # Extract hidden raw string string packet from image bits
                raw_extracted_text = extract_payload_from_image(decode_file)
                
                if "No secure encrypted structural payload" in raw_extracted_text:
                    st.error(raw_extracted_text)
                else:
                    # Run raw text through the AES-256 decryption process
                    final_decrypted_message = decrypt_payload(raw_extracted_text, decode_pass)
                    
                    if "⚠️ DECRYPTION FAILED" in final_decrypted_message:
                        st.error(final_decrypted_message)
                    else:
                        st.success("🎉 Cryptographic Extraction Complete! Secure Payload Unlocked:")
                        st.code(final_decrypted_message, language="text")
        else:
            st.warning("Please supply both a valid targeted image file and structural decryption password matrix keys.")
