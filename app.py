import streamlit as st
import g4f
from PIL import Image
import io

st.set_page_config(page_title="AI Portfolio Factory", page_icon="🛡️", layout="centered")

st.title("🛡️ AI-Driven Portfolio Factory & Security Vault")
st.write("---")

# --- CORE STEGANOGRAPHY LOGIC ---

# Function to hide text inside an image
def hide_text_in_image(uploaded_img, secret_text):
    img = Image.open(uploaded_img).convert("RGB")
    pixels = img.load()
    
    # End marker token '1111111111111110' tells the decoder where to stop reading
    binary_secret = ''.join(format(ord(char), '08b') for char in secret_text) + '1111111111111110'
    
    data_index = 0
    width, height = img.size
    
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

# Function to extract hidden text from an image
def extract_text_from_image(uploaded_img):
    img = Image.open(uploaded_img).convert("RGB")
    pixels = img.load()
    
    binary_data = ""
    width, height = img.size
    
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            binary_data += str(r & 1)
            
            # Check if our end marker token is reached
            if binary_data.endswith('1111111111111110'):
                binary_data = binary_data[:-16] # Strip the marker
                # Convert binary blocks of 8 bits back to characters
                all_bytes = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
                decoded_text = "".join(chr(int(b, 2)) for b in all_bytes)
                return decoded_text
    return "No secret payload found or corrupted data structure."

# --- AI GENERATION LOGIC ---
def generate_ai_content(name, role, skills, bio):
    prompt = f"""
    System: You are an elite tech resume writer. Provide ONLY the final bio. Do not repeat instructions. Do not say 'Here is your bio'.
    User: Turn these details into a headline-grabbing 3-sentence professional bio making me look like an industry expert.
    Name: {name}
    Role: {role}
    Skills: {skills}
    Background: {bio}
    """
    try:
        return g4f.ChatCompletion.create(model=g4f.models.gpt_4, messages=[{"role": "user", "content": prompt}])
    except Exception as e:
        return f"Error: {str(e)}"


# --- CREATING THE TWO CORE TABS ---
tab1, tab2 = st.tabs(["🚀 Build Portfolio & Encode Image", "🔓 Extract Hidden Security Payload"])

with tab1:
    st.markdown("### 🧑‍💻 Enter Details to Generate Portfolio")
    name = st.text_input("Full Name", value="Rudra Mehta")
    role = st.text_input("Professional Title", value="Cybersecurity Analyst")
    skills = st.text_area("Your Core Skills (comma separated)", value="Python, HTML, Cloud Security")
    bio = st.text_area("Tell us about your background", value="I am an ethical hacker focused on secure code and network defense.")
    
    st.write("---")
    st.markdown("### 🔒 Embed Secret Data into Image")
    uploaded_file = st.file_uploader("Upload Profile Image (PNG recommended)", type=["png", "jpg", "jpeg"], key="encoder_upload")
    secret_msg = st.text_input("Secret Verification Key/Note to Hide", value="Verified Cyber Expert Level-1")
    
    if st.button("Generate Secured System ✨"):
        if name and role and skills:
            with st.spinner("Processing configurations..."):
                refined_bio = generate_ai_content(name, role, skills, bio)
                st.success("🎉 Web Content Successfully Staged!")
                
                # HTML Output generation
                html_template = f"""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title>{name} | Portfolio</title>
                    <style>
                        body {{ font-family: 'Segoe UI', sans-serif; background-color: #0d1117; color: #c9d1d9; margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; }}
                        .card {{ background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 40px; max-width: 500px; text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }}
                        h1 {{ color: #58a6ff; margin-bottom: 5px; }}
                        h3 {{ color: #8b949e; font-weight: 400; margin-top: 0; }}
                        p {{ line-height: 1.6; color: #8b949e; text-align: justify; }}
                        .badge {{ background: #21262d; border: 1px solid #30363d; color: #58a6ff; padding: 6px 12px; border-radius: 20px; font-size: 14px; display: inline-block; margin: 4px; }}
                    </style>
                </head>
                <body>
                    <div class="card">
                        <h1>{name}</h1>
                        <h3>{role}</h3>
                        <hr style="border-color: #30363d;">
                        <p>{refined_bio}</p>
                        <div class="skills">
                            {" ".join([f'<span class="badge">{s.strip()}</span>' for s in skills.split(',')])}
                        </div>
                    </div>
                </body>
                </html>
                """
                
                st.download_button(label="Download HTML Website File 🌐", data=html_template, file_name="index.html", mime="text/html")
                
                if uploaded_file is not None:
                    secure_img_bytes = hide_text_in_image(uploaded_file, secret_msg)
                    st.info("🔒 Image Encrypted Successfully!")
                    st.download_button(label="Download Secured Image 🖼️", data=secure_img_bytes, file_name="secure_profile.png", mime="image/png")
        else:
            st.warning("Please fill out the required fields.")

with tab2:
    st.markdown("### 🔓 Secure Steganography Extractor")
    st.write("Upload any profile image generated by this tool to decode the hidden structural signature.")
    
    decode_file = st.file_uploader("Upload Secured Image File", type=["png"], key="decoder_upload")
    
    if st.button("Decrypt & Extract Payload 🔍"):
        if decode_file is not None:
            with st.spinner("Parsing image bits..."):
                extracted_secret = extract_text_from_image(decode_file)
                st.success("🎉 Extraction Complete!")
                st.code(extracted_secret, language="text")
        else:
            st.warning("Please upload a .png file to extract.")