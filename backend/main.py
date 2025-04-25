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

# Game Development Contexts
GAME_CONTEXTS = {
    "performance": """
    Focus on:
    - Frame rate optimization
    - Memory management
    - Efficient data structures
    - Batch processing
    - Object pooling
    - Spatial partitioning
    - Asset loading and caching
    """,
    
    "gameplay": """
    Focus on:
    - Input handling
    - Game state management
    - Entity component systems
    - Collision detection
    - Physics calculations
    - AI behavior patterns
    - Game loop structure
    """,
    
    "architecture": """
    Focus on:
    - Design patterns (Observer, State, Command)
    - Code modularity
    - Event systems
    - Scene management
    - Resource management
    - Save/Load systems
    - Networking architecture
    """,
    
    "graphics": """
    Focus on:
    - Rendering optimization
    - Shader implementation
    - Particle systems
    - Animation systems
    - Texture management
    - Camera systems
    - Level of detail
    """
}

# Language-specific best practices
LANGUAGE_PRACTICES = {
    "java": """
    - Use efficient data structures (ArrayList for dynamic arrays)
    - Implement proper garbage collection practices
    - Use StringBuilder for string concatenation
    - Consider thread safety in game loops
    - Utilize Java collections framework efficiently
    """,
    
    "javascript": """
    - Use requestAnimationFrame for game loops
    - Implement proper garbage collection practices
    - Use TypedArrays for performance-critical operations
    - Consider Web Workers for heavy computations
    - Use proper event delegation
    """,
    
    "typescript": """
    - Leverage strict type checking
    - Use interfaces for game entities
    - Implement proper access modifiers
    - Use enums for game states
    - Consider decorators for component systems
    """,
    
    "python": """
    - Use Pygame or Arcade for 2D games
    - Implement proper __slots__ for memory optimization
    - Use NumPy for physics calculations
    - Consider Cython for performance-critical parts
    - Implement proper garbage collection
    """,
    
    "csharp": """
    - Use Unity's built-in optimization features
    - Implement proper memory management
    - Use structs for performance-critical components
    - Consider job system for parallel processing
    - Implement object pooling
    """,
    
    "cpp": """
    - Use smart pointers for memory management
    - Implement proper RAII practices
    - Use data-oriented design
    - Consider SIMD operations
    - Implement proper memory alignment
    """
}

class CodeAnalysisRequest(BaseModel):
    code: str
    prompt: str
    language: str

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

def parse_gemini_response(response_text: str, language: str) -> tuple[str, str]:
    logger.debug(f"Raw response from Gemini: {response_text}")
    
    # Look for code block with or without language specification
    code_markers = [
        (f"```{language}", "```"),  # With language
        ("```", "```")  # Without language
    ]
    
    suggested_code = ""
    explanation = ""
    
    for start_marker, end_marker in code_markers:
        try:
            code_start = response_text.find(start_marker)
            if code_start != -1:
                code_start += len(start_marker)
                code_end = response_text.find(end_marker, code_start)
                if code_end != -1:
                    suggested_code = response_text[code_start:code_end].strip()
                    explanation_start = response_text.find("Explanation:", code_end)
                    if explanation_start != -1:
                        explanation = response_text[explanation_start + 12:].strip()
                    break
        except Exception as e:
            logger.error(f"Error parsing response with marker {start_marker}: {str(e)}")
            continue
    
    if not suggested_code or not explanation:
        logger.error("Failed to parse Gemini response properly")
        logger.debug(f"Found code: {bool(suggested_code)}, Found explanation: {bool(explanation)}")
        raise ValueError("Could not parse response format correctly")
    
    return suggested_code, explanation

@app.post("/analyze", response_model=CodeSuggestion)
async def analyze_code(request: CodeAnalysisRequest):
    try:
        logger.info(f"Received request for language: {request.language}")
        logger.debug(f"Code: {request.code}")
        logger.debug(f"Prompt: {request.prompt}")

        # Comprehensive game development contexts
        game_contexts = {
            "performance": """
            Performance Optimization Focus:
            1. Game Loop Optimization
               - Fixed timestep implementation
               - Variable timestep handling
               - Frame timing and synchronization
               - Delta time calculations
               - Frame rate limiting and VSync
            
            2. Memory Management
               - Object pooling systems
               - Resource caching
               - Memory defragmentation
               - Garbage collection optimization
               - Asset streaming
            
            3. Rendering Optimization
               - Batch rendering systems
               - Culling techniques (frustum, occlusion)
               - LOD (Level of Detail) systems
               - Texture atlasing
               - Shader optimization
               - Draw call reduction
            
            4. Physics Optimization
               - Broad phase collision detection
               - Spatial partitioning (Quadtree, Octree)
               - Physics engine optimization
               - Collision response optimization
               - Rigidbody management
            """,

            "gameplay": """
            Gameplay Systems Focus:
            1. Input Systems
               - Input mapping and configuration
               - Input buffering and prediction
               - Gesture recognition
               - Input state management
               - Controller support
            
            2. Combat Systems
               - Hit detection and hitboxes
               - Damage calculation systems
               - Combat state machines
               - Combo systems
               - Projectile management
            
            3. AI Systems
               - Pathfinding (A*, Dijkstra)
               - Behavior trees
               - State machines for AI
               - Decision making systems
               - Group behavior coordination
               - Navigation mesh usage
            
            4. Game Mechanics
               - Power-up systems
               - Inventory management
               - Quest/Mission systems
               - Achievement systems
               - Progression systems
               - Economy systems
            """,

            "architecture": """
            Game Architecture Focus:
            1. Core Systems
               - Entity Component System (ECS)
               - Event/Message systems
               - Service locator pattern
               - Dependency injection
               - Scene graph management
            
            2. Data Management
               - Save/Load systems
               - Serialization
               - Data persistence
               - Configuration management
               - Asset management
            
            3. Game State
               - State machine implementation
               - Scene management
               - Level loading systems
               - Checkpoint systems
               - Game flow control
            
            4. Networking
               - Client-server architecture
               - State synchronization
               - Network prediction
               - Lag compensation
               - Multiplayer session management
            """,

            "graphics": """
            Graphics Systems Focus:
            1. Rendering Pipeline
               - Custom shaders
               - Post-processing effects
               - Particle systems
               - Animation systems
               - Camera systems
            
            2. Visual Effects
               - Sprite management
               - Special effects systems
               - Weather systems
               - Lighting systems
               - Shadow techniques
            
            3. UI/UX
               - HUD systems
               - Menu systems
               - UI animation
               - Screen space effects
               - UI state management
            
            4. Asset Pipeline
               - Texture management
               - Model loading
               - Animation data
               - Asset bundling
               - Resource streaming
            """,

            "audio": """
            Audio Systems Focus:
            1. Sound Engine
               - Audio source management
               - 3D positional audio
               - Sound mixing
               - Audio effects processing
               - Stream management
            
            2. Music Systems
               - Dynamic music system
               - Music state management
               - Transition systems
               - Adaptive music
               - Playlist management
            
            3. Sound Effects
               - SFX pooling
               - Priority system
               - Distance-based attenuation
               - Environmental effects
               - Real-time effects
            """,

            "tools": """
            Game Development Tools Focus:
            1. Debug Systems
               - Performance profiling
               - Debug visualization
               - Logging systems
               - State inspection
               - Replay systems
            
            2. Level Tools
               - Level editor integration
               - Tile system management
               - Procedural generation
               - Environment systems
               - Spawn point management
            
            3. Testing
               - Unit testing framework
               - Integration testing
               - Automated testing
               - Replay testing
               - Performance testing
            """
        }

        # Language-specific game development patterns
        language_patterns = {
            "java": """
            Java Game Development Best Practices:
            1. Game Engine Integration
               - LibGDX optimization patterns
               - LWJGL best practices
               - JavaFX game loop patterns
               - JMonkey engine patterns
               - Custom game loop implementation
            
            2. Performance Patterns
               - Efficient collection usage (ArrayDeque for game objects)
               - Object pooling implementation
               - Garbage collection optimization
               - Thread management for game loops
               - Double/Triple buffering patterns
            
            3. Architecture Patterns
               - Entity Component System (ECS)
               - Game state management
               - Scene graph implementation
               - Event handling system
               - Asset management patterns
               - Resource loading optimization
            
            4. Game Systems
               - Collision detection optimization
               - Physics engine integration
               - Sprite batch rendering
               - Animation system patterns
               - Input handling system
               - Sound system management
            """,
            
            "python": """
            Python Game Development Best Practices:
            1. Pygame Optimization
               - Surface caching
               - Sprite group optimization
               - Rect collision optimization
               - Event handling patterns
               - Sound management
            
            2. Performance Patterns
               - NumPy for physics calculations
               - Cython for critical paths
               - Proper surface locking
               - Efficient sprite management
               - Resource loading optimization
            
            3. Architecture
               - Scene management system
               - State machine implementation
               - Event system patterns
               - Component-based design
               - Resource management
            """,

            "javascript": """
            JavaScript Game Development Best Practices:
            1. Canvas Optimization
               - RequestAnimationFrame usage
               - Double buffering
               - Canvas state management
               - Sprite batching
               - Layer management
            
            2. WebGL Integration
               - Shader management
               - Buffer optimization
               - Texture handling
               - WebGL state caching
               - Render queue management
            
            3. Browser Optimization
               - Asset preloading
               - Web Worker utilization
               - Memory management
               - Event delegation
               - Resource caching
            """,

            "typescript": """
            TypeScript Game Development Best Practices:
            1. Type Safety
               - Game state interfaces
               - Entity type definitions
               - Component type safety
               - Event type definitions
               - Asset type management
            
            2. Architecture Patterns
               - Dependency injection
               - Service decorators
               - Module organization
               - Generic constraints
               - Abstract factories
            
            3. Engine Integration
               - Engine type definitions
               - Plugin type safety
               - Framework integration
               - Module augmentation
               - Declaration merging
            """,

            "cpp": """
            C++ Game Development Best Practices:
            1. Memory Management
               - Custom allocators
               - Memory pools
               - RAII patterns
               - Smart pointer usage
               - Memory alignment
            
            2. Performance
               - SIMD optimization
               - Cache coherency
               - Data-oriented design
               - Template metaprogramming
               - Compiler optimization
            
            3. Engine Systems
               - Component systems
               - Memory managers
               - Resource handling
               - Threading patterns
               - Platform abstraction
            """,

            "csharp": """
            C# Game Development Best Practices:
            1. Unity Integration
               - MonoBehaviour patterns
               - Coroutine optimization
               - Scriptable Objects
               - Custom editors
               - Asset management
            
            2. Performance
               - Struct optimization
               - Job system usage
               - Burst compilation
               - Memory management
               - Unity DOTS
            
            3. Architecture
               - Component patterns
               - Event systems
               - Service locator
               - Object pooling
               - Scene management
            """
        }

        # Determine the most relevant context based on the code and prompt
        def determine_context(code: str, prompt: str) -> str:
            prompt_lower = prompt.lower()
            code_lower = code.lower()
            
            # Check for context clues in both code and prompt
            if any(term in prompt_lower or term in code_lower for term in ['fps', 'performance', 'optimize', 'speed', 'memory', 'lag']):
                return 'performance'
            elif any(term in prompt_lower or term in code_lower for term in ['input', 'player', 'enemy', 'combat', 'ai', 'npc']):
                return 'gameplay'
            elif any(term in prompt_lower or term in code_lower for term in ['component', 'system', 'manager', 'service', 'state']):
                return 'architecture'
            elif any(term in prompt_lower or term in code_lower for term in ['render', 'draw', 'sprite', 'shader', 'camera']):
                return 'graphics'
            elif any(term in prompt_lower or term in code_lower for term in ['sound', 'audio', 'music', 'play']):
                return 'audio'
            elif any(term in prompt_lower or term in code_lower for term in ['debug', 'test', 'tool', 'editor']):
                return 'tools'
            
            return 'performance'  # Default to performance context

        # Determine the most relevant context
        context = determine_context(request.code, request.prompt)
        logger.info(f"Determined context: {context}")

        # Enhanced prompt for game development
        prompt = f"""As an expert game developer specializing in {context}, analyze and improve this {request.language} code.
        
        {game_contexts[context]}

        Language-specific game development considerations:
        {language_patterns.get(request.language.lower(), "Apply general game development best practices.")}

        Original code:
        ```{request.language}
        {request.code}
        ```

        User's specific request: {request.prompt}

        Provide your response in this exact format:
        ```{request.language}
        [Your improved game-optimized code here]
        ```

        Explanation:
        [Provide a detailed explanation of the improvements made, focusing on game development benefits and performance implications]
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
            code_start = response_text.find("```") + 3
            if "```" + request.language in response_text:
                code_start = response_text.find("```" + request.language) + len(request.language) + 3
            
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