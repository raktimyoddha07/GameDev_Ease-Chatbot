from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict
import google.generativeai as genai
import os
from dotenv import load_dotenv
import logging
import traceback

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv("GOOGLE_API_KEY")
logger.debug(f"API Key found: {'Yes' if api_key else 'No'}")

if not api_key:
    logger.error("No API key found in .env file")
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

try:
    genai.configure(api_key=api_key)
    # Use Gemini 1.5 Flash model
    model = genai.GenerativeModel('gemini-1.5-flash')
    logger.info("Successfully configured Gemini API with Gemini 1.5 Flash")
except Exception as e:
    logger.error(f"Failed to configure Gemini API: {str(e)}")
    raise

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Phaser.js Development Contexts
PHASER_CONTEXTS = {
    "performance": """
    Phaser.js Performance Optimization Focus:
    1. Game Loop Optimization
       - Fixed timestep implementation
       - Delta time calculations
       - Frame rate limiting
       - VSync handling
       - Game loop throttling
    
    2. Memory Management
       - Object pooling for sprites and particles
       - Texture atlas usage
       - Asset preloading and caching
       - Scene cleanup and disposal
       - Memory leak prevention
    
    3. Rendering Optimization
       - Sprite batching
       - Render texture usage
       - Canvas/WebGL context management
       - Layer management
       - Culling techniques
    
    4. Physics Optimization
       - Arcade physics optimization
       - Matter.js physics settings
       - Collision group management
       - Static body usage
       - Physics world bounds
    """,
    
    "gameplay": """
    Phaser.js Gameplay Systems Focus:
    1. Input Systems
       - Keyboard input handling
       - Touch/pointer input
       - Gamepad support
       - Input plugin usage
       - Gesture recognition
    
    2. Scene Management
       - Scene transitions
       - Scene loading
       - Scene lifecycle
       - Scene communication
       - Scene preloading
    
    3. Game State
       - State machine implementation
       - Save/Load systems
       - Progress tracking
       - Achievement systems
       - Game flow control
    
    4. Physics and Collision
       - Arcade physics setup
       - Matter.js integration
       - Collision detection
       - Physics bodies
       - Collision callbacks
    """,
    
    "architecture": """
    Phaser.js Architecture Focus:
    1. Scene Organization
       - Scene hierarchy
       - Scene inheritance
       - Scene composition
       - Scene dependencies
       - Scene loading order
    
    2. Plugin Development
       - Custom plugin creation
       - Plugin lifecycle
       - Plugin configuration
       - Plugin events
       - Plugin dependencies
    
    3. Event System
       - Event emitter usage
       - Custom events
       - Event bubbling
       - Event cleanup
       - Event prioritization
    
    4. Asset Management
       - Asset loading pipeline
       - Asset preloading
       - Asset caching
       - Asset versioning
       - Asset cleanup
    """,
    
    "graphics": """
    Phaser.js Graphics Systems Focus:
    1. Sprite Management
       - Sprite creation
       - Sprite animation
       - Sprite groups
       - Sprite pooling
       - Sprite layering
    
    2. Particle Systems
       - Particle emitter setup
       - Particle effects
       - Particle optimization
       - Particle blending
       - Particle physics
    
    3. Shader Implementation
       - Custom shaders
       - Post-processing
       - Shader uniforms
       - Shader compilation
       - Shader optimization
    
    4. Camera Systems
       - Camera follow
       - Camera bounds
       - Camera effects
       - Multiple cameras
       - Camera transitions
    """
}

# Phaser.js Best Practices
PHASER_BEST_PRACTICES = """
Phaser.js Development Best Practices:

1. Scene Management
   - Use scene inheritance for common functionality
   - Implement proper scene lifecycle methods
   - Handle scene transitions smoothly
   - Clean up resources in scene shutdown
   - Use scene plugins for shared functionality

2. Asset Loading
   - Preload assets in loading scenes
   - Use texture atlases for sprites
   - Implement proper loading progress
   - Handle loading errors gracefully
   - Cache frequently used assets

3. Performance
   - Use object pooling for frequently created objects
   - Implement proper culling for off-screen objects
   - Optimize physics calculations
   - Use render textures for complex effects
   - Implement proper garbage collection

4. Code Organization
   - Use ES6 classes for game objects
   - Implement proper inheritance
   - Use composition over inheritance
   - Follow SOLID principles
   - Use TypeScript for better type safety

5. Game Architecture
   - Implement proper state management
   - Use event system for communication
   - Create reusable components
   - Implement proper error handling
   - Use dependency injection
"""

class CodeAnalysisRequest(BaseModel):
    code: str
    prompt: str

class CodeSuggestion(BaseModel):
    original: str
    suggested: str
    explanation: str

def determine_context(prompt: str) -> str:
    prompt_lower = prompt.lower()
    if any(word in prompt_lower for word in ["fps", "slow", "performance", "optimize", "speed", "memory", "lag"]):
        return "performance"
    elif any(word in prompt_lower for word in ["gameplay", "control", "input", "collision", "physics", "ai"]):
        return "gameplay"
    elif any(word in prompt_lower for word in ["structure", "pattern", "architecture", "design", "system"]):
        return "architecture"
    elif any(word in prompt_lower for word in ["render", "visual", "graphic", "shader", "animation"]):
        return "graphics"
    return "performance"  # Default context

@app.post("/analyze", response_model=CodeSuggestion)
async def analyze_code(request: CodeAnalysisRequest):
    try:
        logger.info("Received code analysis request")
        logger.debug(f"Code: {request.code}")
        logger.debug(f"Prompt: {request.prompt}")

        # Determine the most relevant context
        context = determine_context(request.prompt)
        logger.info(f"Determined context: {context}")

        # Enhanced prompt for Phaser.js development
        prompt = f"""As an expert Phaser.js developer specializing in {context}, analyze and improve this code.
        
        {PHASER_CONTEXTS[context]}

        {PHASER_BEST_PRACTICES}

        Original code:
        ```javascript
        {request.code}
        ```

        User's specific request: {request.prompt}

        Provide your response in this exact format:
        ```javascript
        [Your improved Phaser.js optimized code here]
        ```

        Explanation:
        [Provide a detailed explanation of the improvements made, focusing on Phaser.js best practices and performance implications]
        """

        logger.debug("Sending request to Gemini API...")
        try:
            response = model.generate_content(prompt)
            logger.debug(f"Received response from Gemini: {response.text if response else 'No response'}")
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")

        if not response or not response.text:
            logger.error("Empty response from Gemini")
            raise HTTPException(status_code=500, detail="Empty response from Gemini")

        # Parse response
        try:
            response_text = response.text
            code_start = response_text.find("```javascript") + 12
            code_end = response_text.find("```", code_start)
            explanation_start = response_text.find("Explanation:", code_end)

            if code_start == -1 or code_end == -1 or explanation_start == -1:
                logger.error(f"Failed to parse response. Markers not found. Response: {response_text}")
                raise ValueError("Could not parse response format")

            suggested_code = response_text[code_start:code_end].strip()
            explanation = response_text[explanation_start + 11:].strip()

            logger.info("Successfully parsed response")
            logger.debug(f"Suggested code: {suggested_code}")
            logger.debug(f"Explanation: {explanation}")

            return CodeSuggestion(
                original=request.code,
                suggested=suggested_code,
                explanation=explanation
            )
        except Exception as e:
            logger.error(f"Error parsing response: {str(e)}")
            logger.error(f"Response text: {response_text}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Error parsing response: {str(e)}")

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 