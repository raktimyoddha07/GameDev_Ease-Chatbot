#include <iostream>
#include <vector>
#include <string>
#include <windows.h>

class GameObject {
public:
    int* position;  // Memory leak potential
    std::string name;
    bool isActive;

    GameObject() {
        position = new int[2];  // No delete in destructor
        position[0] = 0;
        position[1] = 0;
    }

    void Update() {
        if(isActive == true) {  // Redundant comparison
            position[0] += 1;
            Sleep(100);  // Blocking sleep in game loop
        }
    }
};

class GameManager {
private:
    std::vector<GameObject*> gameObjects;  // Raw pointers
    int score = 0;

public:
    void AddObject(std::string name) {
        GameObject* obj = new GameObject();  // Memory leak
        obj->name = name;
        gameObjects.push_back(obj);
    }

    void GameLoop() {
        while(1) {  // Infinite loop without exit condition
            for(int i = 0; i < gameObjects.size(); i++) {  // C-style loop
                gameObjects[i]->Update();  // No null check
                
                // Inefficient string concatenation
                std::string debug = "Updated object: " + gameObjects[i]->name + " Score: ";
                debug = debug + std::to_string(score);
                std::cout << debug << std::endl;  // Console output in game loop
            }
        }
    }

    void UpdateScore(int points) {
        score == points;  // Assignment operator error
    }
};

int main() {
    GameManager manager;
    manager.AddObject("Player");
    
    // Memory leak - no cleanup
    int* tempScore = new int(100);
    manager.UpdateScore(*tempScore);
    
    std::vector<int> scores;  // Vector with no reserve
    for(int i = 0; i < 1000; i++) {
        scores.push_back(i);  // Potential reallocation overhead
    }
    
    manager.GameLoop();  // Blocking call
    return 0;  // Unreachable code
} 