import torch
import cv2
import numpy as np
from torchvision import transforms
# from segment_anything import sam_model_registry, SamPredictor
from mobile_sam import sam_model_registry, SamAutomaticMaskGenerator, SamPredictor
import numpy as np
import pandas as pd
import os, random
import shutil


# Load the SAM model
sam_model = sam_model_registry['vit_b'](checkpoint='./sam_b.pt')
sam_model = sam_model.to('cuda')

# Create a SAM predictor
sam_predictor = SamPredictor(sam_model)


def inference_on_sam_model(sam_predictor, frame, points):
    """
    Perform inference on the SAM model using the detected points.
    Args:
        sam_model: SAM model for inference.
        frame (np.array): Frame image.
        points (list): List of (x, y) coordinates of detected points.

    Returns:
        Inference result from the SAM model.
    """
    # Assuming frame is already in RGB format or BGR format, if not, convert it
    if frame.shape[-1] == 3:  # Check if image has 3 channels
        # Convert BGR to RGB if necessary
        print('conversion required')
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    else:
        image = frame
    sam_predictor.set_image(image)

    # Convert points to the expected format for SAM predictor
    input_points = np.array(points, dtype=np.int32)

    # Create a label array with the correct length, and with the label for each point
    input_labels = np.ones(len(points), dtype=np.int32)

    # Perform the SAM predictor inference
    masks, scores, logits = sam_predictor.predict(
        # point_coords=input_points,
        box=input_points[None, :],
        point_labels=input_labels,
        multimask_output=False,
    )

    return masks[0]


def has_transparent_bg_heuristic(image):
    """Checks for potential transparency based on edge statistics using OpenCV.

    Args:
        image: Loaded image as a NumPy array.

    Returns:
        True if the image has high edge activity on the borders, 
        suggesting potential transparency. False otherwise.
    """
    # Convert to grayscale for edge detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply edge detection (e.g., Canny edge detector)
    edges = cv2.Canny(gray, 100, 200)  # Adjust thresholds as needed

    # Calculate edge density on borders (e.g., top and bottom 10% of image)
    height, width = image.shape[:2]
    top_edge_density = np.mean(edges[:int(height * 0.1), :])
    bottom_edge_density = np.mean(edges[int(height * 0.9):, :])

    # Compare edge density on borders with overall image (adjust threshold)
    edge_ratio = (top_edge_density + bottom_edge_density) / np.mean(edges)
    return edge_ratio > 1.5  # Adjust threshold based on your image data

def remove_background_from_garment(input_img_path:str, output_img_path:str)->None:
    # Load the image
    image = cv2.imread(input_img_path)

    # check if the image already has transparency
    # if has_transparent_bg_heuristic(image):
    #     print(f'image already has transparency: {input_img_path}')
    #     return False

    # get width and height of the image
    height, width, _ = image.shape
    aspect_ratio = width / height
    sx, sy = 128*aspect_ratio, 256*aspect_ratio

    # Define the points for the SAM model
    point_coords = [
        [width//2 - sx, height//2 - sy],
        [width//2 + sx, height//2 - sy],
        [width//2 + sx, height//2 + sy],
        [width//2 - sx, height//2 + sy],
    ]
    box = np.array([0, 0, width, height])
    # Perform inference on the SAM model
    mask = inference_on_sam_model(sam_predictor, image, box)

    # Save the mask
    color = np.array([1, 1, 1, 1])
    h, w = mask.shape[-2:]
    mask_image = mask.reshape(h, w, 1) * color.reshape(1, 1, -1)
    mask_image = ((1-mask_image) * 255).astype(np.uint8)
    # make the first 50 and last 50 pixels transparent vertically
    mask_image[:, :50, 3] = 0
    mask_image[:, -50:, 3] = 0
    # Save the mask image
    # cv2.imwrite('mask.png', mask_image)
    # make all non white pixels transparent in the original image
    original_image_rgba = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
    transparent_background = np.zeros_like(original_image_rgba)

    transparent_background[:, :, :] = original_image_rgba[:, :, :]
    transparent_background[:, :, 3] = mask_image[:, :, 3]

    cv2.imwrite(output_img_path, transparent_background)
    return True


if __name__ == '__main__':
    df = pd.read_csv('products_tryon_output.csv')

    output_df = pd.DataFrame(columns=[
        'product_id', 'category', 'subcategory', 'image_tryon_url',
        'score', 'raw_image_path', 'final_image_path'
    ])

    for i in range(len(df)):
        raw_image_path = df.loc[i, 'raw_image_path']
        extension = raw_image_path.split('.')[-1]
        filename = os.path.basename(raw_image_path).split('.')[0] + '.png'
        final_image_path = f'../tmp/tryon/{filename}'
        if extension.lower() == 'png':
            shutil.copyfile(raw_image_path, final_image_path)
        else:
            remove_background_from_garment(raw_image_path, final_image_path)

        print(f'processed {i+1}/{len(df)} images')

        output_df.loc[len(output_df)] = [
            df.loc[i, 'product_id'],
            df.loc[i, 'category'],
            df.loc[i, 'subcategory'],
            df.loc[i, 'image_tryon_url'],
            df.loc[i, 'score'],
            raw_image_path,
            final_image_path
        ]
        output_df.to_csv('final_tryon_images.csv', index=False)
