# AI Search Module

## Overview
This project is a graphical visualization tool for various AI search algorithms implemented in Python using PyQt5. The tool allows users to construct a tree structure and perform different search techniques, including DFS, BFS, UCS, Greedy Search, Iterative Deepening Search, Limited DFS, and A* Search.

## Features
- **Graphical Tree Visualization**: Users can dynamically create and modify tree structures.
- **Multiple Search Algorithms**:
  - Depth-First Search (DFS)
  - Limited Depth-First Search
  - Iterative Deepening Search
  - Uniform Cost Search (UCS)
  - Greedy Best-First Search
  - Breadth-First Search (BFS)
  - A* Search
- **Interactive Search Execution**: Users can select goal nodes and visualize the search process step-by-step.
- **Customizable Heuristics and Path Costs**: Nodes can be assigned custom heuristic values and path costs.
- **Reset and Deletion Options**: Users can reset the search algorithm state or delete nodes from the tree.

## Installation
### Prerequisites
Ensure you have Python installed along with the required dependencies:
```sh
pip install PyQt5
```

### Running the Application
1. Clone this repository:
   ```sh
   git clone https://github.com/yourusername/AI-Search-Module.git
   ```
2. Navigate to the project directory:
   ```sh
   cd AI-Search-Module
   ```
3. Run the application:
   ```sh
   python AI_Search_Module.py
   ```

## Usage
1. **Adding Nodes**:
   - Enter node details (character, heuristic value, parent node, and path cost).
   - Click "Add Node" to insert the node into the tree.
2. **Performing Searches**:
   - Click on the desired search algorithm button.
   - Enter the goal node(s) when prompted.
   - The search will be visualized with nodes changing color during traversal.
3. **Resetting and Modifying the Tree**:
   - Use "Delete Node" to remove a specific node.
   - Click "Reset Tree" to clear the entire structure.
   - Click "Reset Algorithm" to clear the visualization without affecting the tree.


