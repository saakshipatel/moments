import os
import io
from dotenv import load_dotenv
from google.cloud import vision
from PIL import Image

load_dotenv()

class MLService:
    def __init__(self):
        # Set credentials path
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if credentials_path:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
            try:
                self.client = vision.ImageAnnotatorClient()
            except Exception as e:
                print(f"Error initializing Google Vision client: {e}")
                self.client = None
        else:
            print("Google credentials not found")
            self.client = None
    
    def generate_alt_text(self, image_path):
        """Generate alternative text for an image using Google Vision"""
        if not self.client:
            return "Image uploaded by user"
        
        try:
            # Read image file
            with io.open(image_path, 'rb') as image_file:
                content = image_file.read()
            
            image = vision.Image(content=content)
            
            # Get image description
            response = self.client.label_detection(image=image)
            labels = response.label_annotations
            
            # Also try to get a better description using landmark or logo detection
            landmark_response = self.client.landmark_detection(image=image)
            landmarks = landmark_response.landmark_annotations
            
            # Try to get text in image
            text_response = self.client.text_detection(image=image)
            texts = text_response.text_annotations
            
            # Build alt text
            alt_text_parts = []
            
            if landmarks:
                alt_text_parts.append(landmarks[0].description)
            
            if labels and len(labels) > 0:
                # Use top 3 labels for description
                top_labels = [label.description for label in labels[:3]]
                if not landmarks:
                    alt_text_parts.append("Image containing " + ", ".join(top_labels))
            
            if alt_text_parts:
                return ". ".join(alt_text_parts)
            else:
                return "Image uploaded by user"
                
        except Exception as e:
            print(f"Error generating alt text: {e}")
            return "Image uploaded by user"
    
    def detect_objects(self, image_path):
        """Detect objects in image for search using Google Vision"""
        if not self.client:
            return []
        
        try:
            # Read image file
            with io.open(image_path, 'rb') as image_file:
                content = image_file.read()
            
            image = vision.Image(content=content)
            
            # Collect all possible objects/tags
            objects = []
            
            # Get labels (general objects)
            response = self.client.label_detection(image=image, max_results=10)
            for label in response.label_annotations:
                if label.score > 0.5:  # Confidence threshold
                    objects.append(label.description.lower())
            
            # Get objects (specific object detection)
            object_response = self.client.object_localization(image=image)
            for obj in object_response.localized_object_annotations:
                if obj.score > 0.5:
                    objects.append(obj.name.lower())
            
            # Get landmarks
            landmark_response = self.client.landmark_detection(image=image)
            for landmark in landmark_response.landmark_annotations:
                objects.append(landmark.description.lower())
            
            # Get logos
            logo_response = self.client.logo_detection(image=image)
            for logo in logo_response.logo_annotations:
                objects.append(logo.description.lower())
            
            # Remove duplicates while preserving order
            seen = set()
            unique_objects = []
            for obj in objects:
                if obj not in seen:
                    seen.add(obj)
                    unique_objects.append(obj)
            
            return unique_objects
            
        except Exception as e:
            print(f"Error detecting objects: {e}")
            return []
    
    def get_detailed_analysis(self, image_path):
        """Get comprehensive image analysis for better search and alt text"""
        if not self.client:
            return {
                'alt_text': 'Image uploaded by user',
                'objects': [],
                'colors': [],
                'text': ''
            }
        
        try:
            with io.open(image_path, 'rb') as image_file:
                content = image_file.read()
            
            image = vision.Image(content=content)
            
            # Perform multiple detections in one call for efficiency
            features = [
                vision.Feature(type_=vision.Feature.Type.LABEL_DETECTION, max_results=10),
                vision.Feature(type_=vision.Feature.Type.OBJECT_LOCALIZATION, max_results=10),
                vision.Feature(type_=vision.Feature.Type.TEXT_DETECTION, max_results=1),
                vision.Feature(type_=vision.Feature.Type.LANDMARK_DETECTION, max_results=5),
                vision.Feature(type_=vision.Feature.Type.LOGO_DETECTION, max_results=5),
                vision.Feature(type_=vision.Feature.Type.IMAGE_PROPERTIES),
            ]
            
            request = vision.AnnotateImageRequest(
                image=image,
                features=features
            )
            
            response = self.client.annotate_image(request)
            
            # Process results
            result = {
                'alt_text': self._build_alt_text_from_response(response),
                'objects': self._extract_objects_from_response(response),
                'dominant_colors': self._extract_colors_from_response(response),
                'text': response.text_annotations[0].description if response.text_annotations else ''
            }
            
            return result
            
        except Exception as e:
            print(f"Error in detailed analysis: {e}")
            return {
                'alt_text': 'Image uploaded by user',
                'objects': [],
                'colors': [],
                'text': ''
            }
    
    def _build_alt_text_from_response(self, response):
        """Helper to build alt text from API response"""
        parts = []
        
        if response.landmark_annotations:
            parts.append(response.landmark_annotations[0].description)
        elif response.label_annotations:
            top_labels = [label.description for label in response.label_annotations[:3]]
            parts.append("Image containing " + ", ".join(top_labels))
        
        return ". ".join(parts) if parts else "Image uploaded by user"
    
    def _extract_objects_from_response(self, response):
        """Helper to extract all objects from API response"""
        objects = []
        
        for label in response.label_annotations:
            if label.score > 0.5:
                objects.append(label.description.lower())
        
        for obj in response.localized_object_annotations:
            if obj.score > 0.5:
                objects.append(obj.name.lower())
        
        return list(dict.fromkeys(objects))  # Remove duplicates
    
    def _extract_colors_from_response(self, response):
        """Helper to extract dominant colors"""
        colors = []
        if response.image_properties_annotation:
            for color in response.image_properties_annotation.dominant_colors.colors[:3]:
                colors.append({
                    'red': color.color.red,
                    'green': color.color.green,
                    'blue': color.color.blue,
                    'score': color.score
                })
        return colors

# Initialize service
ml_service = MLService() 
