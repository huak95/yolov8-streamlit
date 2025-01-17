# Python In-built packages
from pathlib import Path
import PIL

# External packages
import streamlit as st

# Local Modules
import settings
import helper

import os

# Setting page layout
st.set_page_config(
    page_title="Object Detection using YOLOv8",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main page heading
st.title("Object Detection using YOLOv8")

# Sidebar
st.sidebar.header("ML Model Config")

# Model Options
model_type = st.sidebar.radio(
    "Select Task", ['Detection', 'Segmentation', 'CustomModel'])

confidence = float(st.sidebar.slider(
    "Select Model Confidence", 25, 100, 40)) / 100

image_size = int(st.sidebar.number_input(
    "Select Model Image Size", value=640))

# Selecting Detection Or Segmentation
# Custom Model Upload
if model_type == 'Detection':
    model_path = Path(settings.DETECTION_MODEL)
elif model_type == 'Segmentation':
    model_path = Path(settings.SEGMENTATION_MODEL)
elif model_type == 'CustomModel':
    uploaded_weight = st.sidebar.file_uploader(
        "Choose an weight...", type=('pt')
    )

    model_path = Path('./weights/yolov8-custom.pt')
    with open(model_path, 'wb') as f:
        f.write(uploaded_weight.getbuffer())
        
# setting
show_labels = st.sidebar.toggle('show_labels', True) 
show_conf = st.sidebar.toggle('show_conf', True)
show_boxes = st.sidebar.toggle('show_boxes', True)
show_masks = st.sidebar.toggle('show_masks', True)

# Load Pre-trained ML Model
try:
    model = helper.load_model(model_path)
except Exception as ex:
    st.error(f"Unable to load model. Check the specified path: {model_path}")
    st.error(ex)

st.sidebar.header("Image/Video Config")
source_radio = st.sidebar.radio(
    "Select Source", settings.SOURCES_LIST)

source_img = None
# If image is selected
if source_radio == settings.IMAGE:
    source_img = st.sidebar.file_uploader(
        "Choose an image...", type=("jpg", "jpeg", "png", 'bmp', 'webp'))

    col1, col2 = st.columns(2)

    with col1:
        try:
            if source_img is None:
                default_image_path = str(settings.DEFAULT_IMAGE)
                default_image = PIL.Image.open(default_image_path)
                st.image(default_image_path, caption="Default Image",
                         use_column_width=True)
            else:
                uploaded_image = PIL.Image.open(source_img)
                st.image(source_img, caption="Uploaded Image",
                         use_column_width=True)
        except Exception as ex:
            st.error("Error occurred while opening the image.")
            st.error(ex)

    with col2:
        if source_img is None:
            default_detected_image_path = str(settings.DEFAULT_DETECT_IMAGE)
            default_detected_image = PIL.Image.open(
                default_detected_image_path)
            st.image(default_detected_image_path, caption='Detected Image',
                     use_column_width=True)
        else:
            if st.sidebar.button('Detect Objects'):
                res = model.predict(uploaded_image,
                                    conf=confidence,
                                    imgsz=image_size,
                                    )
                boxes = res[0].boxes
                # st.text(help(res[0].plot))
                res_plotted = res[0].plot(
                    labels=show_labels,
                    conf=show_conf, 
                    boxes=show_boxes,
                    masks=show_masks,
                    )[:, :, ::-1]

                st.image(res_plotted, caption='Detected Image',
                         use_column_width=True)
                
                pil_res_plotted = PIL.Image.fromarray(res_plotted)
                pil_res_plotted.save("res.jpg")
                
                with open("res.jpg", "rb") as file:
                    btn = st.download_button(
                            label="Download image",
                            data=file,
                            file_name=f"{source_img.name.split('.')[0]}_detect.png",
                            mime="image/png"
                        )

                try:
                    with st.expander("Detection Results"):
                        for box in boxes:
                            st.write(box.data)
                except Exception as ex:
                    # st.write(ex)
                    st.write("No image is uploaded yet!")

elif source_radio == settings.VIDEO:
    helper.play_stored_video(confidence, model)

elif source_radio == settings.WEBCAM:
    helper.play_webcam(confidence, model)

elif source_radio == settings.RTSP:
    helper.play_rtsp_stream(confidence, model)

elif source_radio == settings.YOUTUBE:
    helper.play_youtube_video(confidence, model)

else:
    st.error("Please select a valid source type!")
