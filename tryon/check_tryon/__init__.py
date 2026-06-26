import os
import torch
import numpy as np
from PIL import Image
import torchvision.transforms as transforms
from check_tryon import networks
from check_tryon.utils.transforms import transform_logits, get_affine_transform
import cv2
import random
import os


def load_image_for_parse(image_path, input_size, transform=None):
    def xywh2cs(x, y, w, h):
        center = np.zeros((2), dtype=np.float32)
        center[0] = x + w * 0.5
        center[1] = y + h * 0.5
        aspect_ratio = input_size[1] * 1.0 / input_size[0]
        if w > aspect_ratio * h:
            h = w * 1.0 / aspect_ratio
        elif w < aspect_ratio * h:
            w = h * aspect_ratio
        scale = np.array([w * 1.0, h * 1.0], dtype=np.float32)
        return center, scale

    def box2cs(box):
        x, y, w, h = box[:4]
        return xywh2cs(x, y, w, h)

    input_size = np.asarray(input_size)
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    h, w, _ = img.shape

    # Get person center and scale
    person_center, s = box2cs([0, 0, w - 1, h - 1])
    r = 0
    trans = get_affine_transform(person_center, s, r, input_size)
    input = cv2.warpAffine(
        img,
        trans,
        (int(input_size[1]), int(input_size[0])),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(0, 0, 0))

    input = transform(input)

    meta = {
        'name': os.path.basename(image_path),
        'center': person_center,
        'height': h,
        'width': w,
        'scale': s,
        'rotation': r
    }

    return input, meta


def get_palette(num_cls, model_type):
    n = num_cls
    palette = [0] * (n * 3)
    if model_type == 'pascal':
        for j in range(1, n):
            palette[j * 3 + 0] = 255
            palette[j * 3 + 1] = 0
            palette[j * 3 + 2] = 0
    elif model_type == 'lip':
        # green will be clothes related parts
        # red will be others
        palette = [
            0, 0, 0,  # Background
            255, 0, 0,  # Hat
            255, 0, 0,  # Hair
            255, 0, 0,  # Glove
            255, 0, 0,  # Sunglasses
            0, 255, 0,  # Upper-clothes
            0, 255, 0,  # Dress
            0, 255, 0,  # Coat
            255, 0, 0,  # Socks
            0, 255, 0,  # Pants
            0, 255, 0,  # Jumpsuits
            255, 0, 0,  # Scarf
            0, 255, 0,  # Skirt
            255, 0, 0,  # Face
            255, 0, 0,  # Left-arm
            255, 0, 0,  # Right-arm
            255, 0, 0,  # Left-leg
            255, 0, 0,  # Right-leg
            255, 0, 0,  # Left-shoe
            255, 0, 0,  # Right-shoe
        ]
    elif model_type == 'atr':
        # green will be clothes related parts
        # red will be others
        palette = [
            0, 0, 0,  # Background
            255, 0, 0,  # Hat
            255, 0, 0,  # Hair
            255, 0, 0,  # Sunglasses
            0, 255, 0,  # Upper-clothes
            0, 255, 0,  # Skirt
            0, 255, 0,  # Pants
            0, 255, 0,  # Dress
            255, 0, 0,  # Belt
            255, 0, 0,  # Left-shoe
            255, 0, 0,  # Right-shoe
            255, 0, 0,  # Face
            255, 0, 0,  # Left-leg
            255, 0, 0,  # Right-leg
            255, 0, 0,  # Left-arm
            255, 0, 0,  # Right-arm
            255, 0, 0,  # Bag
            255, 0, 0,  # Scarf
        ]

    return palette


def create_model_mask(image_path, output_dir, model_type):
    input_dir = os.path.dirname(image_path)
    output_dir = output_dir

    if torch.cuda.is_available() is False:
        raise EnvironmentError("CUDA is not available.")
    os.environ['CUDA_VISIBLE_DEVICES'] = '0'

    dataset_settings = {
        'lip': {
            'input_size': [473, 473],
            'num_classes': 20,
            'label': ['Background', 'Hat', 'Hair', 'Glove', 'Sunglasses', 'Upper-clothes', 'Dress', 'Coat',
                      'Socks', 'Pants', 'Jumpsuits', 'Scarf', 'Skirt', 'Face', 'Left-arm', 'Right-arm',
                      'Left-leg', 'Right-leg', 'Left-shoe', 'Right-shoe']
        },
        'atr': {
            'input_size': [512, 512],
            'num_classes': 18,
            'label': ['Background', 'Hat', 'Hair', 'Sunglasses', 'Upper-clothes', 'Skirt', 'Pants', 'Dress', 'Belt',
                      'Left-shoe', 'Right-shoe', 'Face', 'Left-leg', 'Right-leg', 'Left-arm', 'Right-arm', 'Bag', 'Scarf']
        },
        'pascal': {
            'input_size': [512, 512],
            'num_classes': 7,
            'label': ['Background', 'Head', 'Torso', 'Upper Arms', 'Lower Arms', 'Upper Legs', 'Lower Legs'],
        }
    }

    num_classes = dataset_settings[model_type]['num_classes']
    input_size = dataset_settings[model_type]['input_size']
    label = dataset_settings[model_type]['label']
    print("Evaluating total class number {} with {}".format(num_classes, label))

    model = networks.init_model(
        'resnet101', num_classes=num_classes, pretrained=None)
    state_dict = torch.load(
        f'./check_tryon/checkpoints/{model_type}.pth')['state_dict']

    from collections import OrderedDict

    new_state_dict = OrderedDict()
    for k, v in state_dict.items():
        name = k[7:]  # remove `module.`
        new_state_dict[name] = v
    model.load_state_dict(new_state_dict)
    model.cuda()
    model.eval()

    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.406, 0.456, 0.485], std=[
                             0.225, 0.224, 0.229])
    ])

    image, meta = load_image_for_parse(
        image_path, input_size, transform=transform)

    with torch.no_grad():
        # for idx, batch in enumerate(tqdm(dataloader)):
        #     image, meta = batch
        #     img_name = meta['name'][0]
        #     if img_name != os.path.basename(image_path):
        #         continue
        center = meta['center']
        scale = meta['scale']
        w = meta['width']
        h = meta['height']
        image_tensor = image.unsqueeze(0).cuda()
        # break

        output = model(image_tensor)

        c = center
        s = scale
        # w = image.width
        # h = image.height

        # print("""
        #         c: {}
        #         s: {}
        #         w: {}
        #         h: {}
        #         """.format(c, s, w, h))

        upsample = torch.nn.Upsample(
            size=input_size, mode='bilinear', align_corners=True)
        upsample_output = upsample(output[0][-1][0].unsqueeze(0))
        upsample_output = upsample_output.squeeze()
        upsample_output = upsample_output.permute(1, 2, 0)  # CHW -> HWC

        logits_result = transform_logits(
            upsample_output.data.cpu().numpy(), c, s, w, h, input_size=input_size)
        parsing_result = np.argmax(logits_result, axis=2)

        palette = get_palette(num_classes, model_type)
        output_img = Image.fromarray(
            np.asarray(parsing_result, dtype=np.uint8))
        output_img.putpalette(palette)

        output_path = os.path.join(
            output_dir, os.path.basename(image_path)[:-4] + '.png')
        output_img.save(output_path)

    return output_path


def background_remover_human(input_image_path: str) -> str:
    # try:
    output_image_path = create_model_mask(
        input_image_path, '../tmp/output', 'pascal')

    original_image = cv2.imread(input_image_path)

    # Load the mask image
    mask = cv2.imread(output_image_path, cv2.IMREAD_GRAYSCALE)

    # Threshold the mask to create a binary mask
    _, binary_mask = cv2.threshold(mask, 1, 255, cv2.THRESH_BINARY)

    # Convert the original image to RGBA format
    original_image_rgba = cv2.cvtColor(original_image, cv2.COLOR_BGR2BGRA)

    # Create a transparent background
    transparent_background = np.zeros_like(original_image_rgba)

    # Copy the original image to the transparent background using the binary mask
    transparent_background[:, :, :] = original_image_rgba[:, :, :]
    transparent_background[:, :, 3] = binary_mask

    # Save the final image
    final_filename = random.randbytes(16).hex()
    final_image_path = f"../tmp/output/{final_filename}.png"
    cv2.imwrite(final_image_path, transparent_background)

    os.remove(output_image_path)

    return final_image_path


def is_available_for_tryon(input_image_path: str) -> bool:
    output_image_path = create_model_mask(
        input_image_path, '../tmp/output', 'atr')
    # Load the mask image
    mask = cv2.imread(output_image_path)

    red_pixels = np.count_nonzero(
        (mask[:, :, 2] == 255) &
        (mask[:, :, 1] == 0) &
        (mask[:, :, 0] == 0)
    )
    green_pixels = np.count_nonzero(
        (mask[:, :, 2] == 0) &
        (mask[:, :, 1] == 255) &
        (mask[:, :, 0] == 0)
    )

    allowed_percentage = 6
    try:
        red_percentage = (red_pixels / green_pixels) * 100
    except ZeroDivisionError:
        print("No cloth detected")
        return False

    print(f"Human presence percentage: {red_percentage}")

    os.remove(output_image_path)

    if red_percentage >= allowed_percentage:
        return False
    else:
        return True


def background_remover_cloth(input_image_path: str) -> str:
    mask_image_path = create_model_mask(
        input_image_path, '../tmp/output', 'atr')

    original_image = cv2.imread(input_image_path)
    # Load the mask image
    mask = cv2.imread(mask_image_path)
    # Extract the green part of the mask
    green_mask = np.where((mask[:, :, 1] == 255) & (mask[:, :, 0] == 0) & (
        mask[:, :, 2] == 0), 255, 0).astype(np.uint8)
    red_mask = np.where((mask[:, :, 0] == 0) & (mask[:, :, 1] == 0) & (
        mask[:, :, 2] == 255), 255, 0).astype(np.uint8)
    final_mask = green_mask + red_mask
    # Convert the original image to RGBA format
    original_image_rgba = cv2.cvtColor(original_image, cv2.COLOR_BGR2BGRA)
    # Create a transparent background
    transparent_background = np.zeros_like(original_image_rgba)
    # Copy the original image to the transparent background using the green mask
    transparent_background[:, :, :] = original_image_rgba[:, :, :]
    transparent_background[:, :, 3] = final_mask
    # Save the final image
    final_filename = random.randbytes(16).hex()
    final_image_path = f"../tmp/output/{final_filename}.png"
    cv2.imwrite(final_image_path, transparent_background)

    os.remove(mask_image_path)

    return final_image_path
