import cv2
import numpy as np
import os
import tempfile
from PIL import Image
import logging

logger = logging.getLogger(__name__)

def validate_image(image_path):
    """Validate if the image is suitable for colorization"""
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            return False, "File does not exist"
        
        # Check file size (max 20MB)
        file_size = os.path.getsize(image_path)
        if file_size > 20 * 1024 * 1024:  # 20MB
            return False, "File too large (max 20MB)"
        
        # Try to read image
        img = cv2.imread(image_path)
        if img is None:
            return False, "Invalid image format"
        
        # Check image dimensions
        height, width = img.shape[:2]
        if height < 32 or width < 32:
            return False, "Image too small (minimum 32x32 pixels)"
        
        if height > 4096 or width > 4096:
            return False, "Image too large (maximum 4096x4096 pixels)"
        
        return True, "Valid image"
        
    except Exception as e:
        logger.error(f"Error validating image: {e}")
        return False, f"Validation error: {str(e)}"

def resize_image_if_needed(image_path, max_size=1024):
    """Resize image if it's too large"""
    try:
        img = cv2.imread(image_path)
        height, width = img.shape[:2]
        
        if max(height, width) > max_size:
            # Calculate new dimensions
            if height > width:
                new_height = max_size
                new_width = int(width * max_size / height)
            else:
                new_width = max_size
                new_height = int(height * max_size / width)
            
            # Resize image
            resized = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
            
            # Save resized image
            cv2.imwrite(image_path, resized)
            logger.info(f"Resized image from {width}x{height} to {new_width}x{new_height}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error resizing image: {e}")
        return False

def enhance_colorized_image(image: np.ndarray) -> np.ndarray:
    """Enhance colorized image quality"""
    try:
        # Применяем адаптивную эквализацию гистограммы в LAB
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # CLAHE только к L каналу
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        # Объединяем каналы и конвертируем обратно в BGR
        enhanced_lab = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
        
        return enhanced

    except Exception as e:
        logger.error(f"Error enhancing image: {e}")
        return image


def create_thumbnail(image_path, size=(200, 200)):
    """Create a thumbnail of the image"""
    try:
        img = cv2.imread(image_path)
        thumbnail = cv2.resize(img, size, interpolation=cv2.INTER_AREA)
        return thumbnail
    except Exception as e:
        logger.error(f"Error creating thumbnail: {e}")
        return None

