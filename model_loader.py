import cv2
import numpy as np
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class CaffeColorizationModel:
    """Caffe-based image colorization model using OpenCV DNN"""
    
    def __init__(self, model_path: str, prototxt_path: str):
        """
        Initialize the colorization model
        
        Args:
            model_path: Path to the .caffemodel file
            prototxt_path: Path to the .prototxt file
        """
        self.model_path = model_path
        self.prototxt_path = prototxt_path
        self.net = None
        self.pts_in_hull = None
        
        self._load_model()
    
    def _load_model(self):
        """Load the Caffe model using OpenCV DNN"""
        try:
            # Check if files exist
            if not Path(self.model_path).exists():
                raise FileNotFoundError(f"Model file not found: {self.model_path}")
            if not Path(self.prototxt_path).exists():
                raise FileNotFoundError(f"Prototxt file not found: {self.prototxt_path}")
            
            # Load the model using OpenCV DNN
            self.net = cv2.dnn.readNetFromCaffe(self.prototxt_path, self.model_path)
            
            # Try to load cluster centers for colorization (optional)
            pts_path = Path(__file__).parent / 'models' / 'pts_in_hull.npy'
            if pts_path.exists():
                self.pts_in_hull = np.load(pts_path)
                
                # Add cluster centers as 1x1 convolution kernel
                class8 = self.net.getLayerId("class8_ab")
                conv8 = self.net.getLayerId("conv8_313_rh")
                pts = self.pts_in_hull.transpose().reshape(2, 313, 1, 1)
                self.net.getLayer(class8).blobs = [pts.astype(np.float32)]
                self.net.getLayer(conv8).blobs = [np.full([1, 313], 2.606, dtype=np.float32)]
                logger.info("Cluster centers loaded successfully")
            else:
                logger.warning("pts_in_hull.npy not found, model may not work optimally")
            
            logger.info("Caffe colorization model loaded successfully via OpenCV DNN")
            
        except Exception as e:
            logger.error(f"Error loading Caffe model: {e}")
            raise RuntimeError(f"Failed to load colorization model: {e}")
    
    def colorize(self, image_path: str) -> np.ndarray:
        """
        Colorize a grayscale image with improved quality
        
        Args:
            image_path: Path to the input image
            
        Returns:
            Colorized image as numpy array (BGR format)
        """
        try:
            # Read the image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not read image: {image_path}")
            
            # Store original dimensions
            original_height, original_width = image.shape[:2]
            
            # Convert to LAB color space with float32 precision
            scaled = image.astype(np.float32) / 255.0
            lab = cv2.cvtColor(scaled, cv2.COLOR_BGR2LAB)
            
            # Extract L channel from original image
            L_original = lab[:, :, 0]
            
            # Resize to 224x224 for the model with high-quality interpolation
            resized = cv2.resize(lab, (224, 224), interpolation=cv2.INTER_CUBIC)
            L = cv2.split(resized)[0]
            L -= 50  # Mean centering
            
            # Run the model
            self.net.setInput(cv2.dnn.blobFromImage(L))
            ab = self.net.forward()[0, :, :, :].transpose((1, 2, 0))
            
            # Resize ab channels back to original dimensions with high-quality interpolation
            ab_upscaled = cv2.resize(ab, (original_width, original_height), interpolation=cv2.INTER_CUBIC)
            
            # Use bilateral filter to smooth colors while preserving edges
            ab_upscaled[:, :, 0] = cv2.bilateralFilter(ab_upscaled[:, :, 0], d=9, sigmaColor=75, sigmaSpace=75)
            ab_upscaled[:, :, 1] = cv2.bilateralFilter(ab_upscaled[:, :, 1], d=9, sigmaColor=75, sigmaSpace=75)
            
            # Concatenate with ORIGINAL L channel (not resized) for better detail
            colorized = np.concatenate((L_original[:, :, np.newaxis], ab_upscaled), axis=2)
            
            # Convert back to BGR with proper color space conversion
            colorized = cv2.cvtColor(colorized, cv2.COLOR_LAB2BGR)
            colorized = np.clip(colorized, 0, 1)
            
            # Apply subtle sharpening to restore detail
            colorized_8bit = (255 * colorized).astype(np.uint8)
            kernel = np.array([[-1,-1,-1],
                              [-1, 9,-1],
                              [-1,-1,-1]]) * 0.1
            sharpened = cv2.filter2D(colorized_8bit, -1, kernel)
            
            # Blend original and sharpened (70% sharpened, 30% original)
            result = cv2.addWeighted(sharpened, 0.7, colorized_8bit, 0.3, 0)
            
            # Apply subtle contrast adjustment
            result = cv2.convertScaleAbs(result, alpha=1.05, beta=5)
            
            return result
            
        except Exception as e:
            logger.error(f"Error colorizing image: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check if the model is loaded and available"""
        return self.net is not None