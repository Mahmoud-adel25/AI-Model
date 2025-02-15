from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGraphicsScene, QGraphicsView,
    QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem,
    QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QLineEdit, QLabel, QMessageBox
)
from collections import deque
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QBrush
from tkinter import simpledialog
import sys
import heapq
from PyQt5.QtCore import QTimer
import time



class Node:
    """Represents a node in the binary tree."""
    
    def __init__(self, char, heuristic, path_cost=0):
        self.char = char
        self.heuristic = heuristic
        self.children = []  # A list to hold multiple child nodes
        self.path_cost = path_cost
        self.parents = []
    def __eq__(self, other):
        # Compare nodes based on their unique character
        return isinstance(other, Node) and self.char == other.char
    

    def __hash__(self):
        # Hash nodes based on their character for dictionary keys and sets
        return hash(self.char)

    def __lt__(self, other):
        if not isinstance(other, Node):
            return NotImplemented
        # Compare the values
        return (self.heuristic < other.heuristic) or (self.path_cost < other.path_cost) or (self.char < other.char)



class TreeVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI PROJECT")
        self.setGeometry(0, 0, 1920, 1050)

        # Graphics Scene and View
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QBrush(Qt.white))
        self.view = QGraphicsView(self.scene, self)
        self.view.setGeometry(0, 0, 1920, 1050)

        # Main Container
        container = QWidget(self)
        self.setCentralWidget(container)
        main_layout = QHBoxLayout(container)

        # Left Panel Layout for Buttons
        left_panel = QVBoxLayout()
        main_layout.addLayout(left_panel)

        # Button Controls for DFS Operations
        self.dfs_button = QPushButton("Perform DFS")
        self.dfs_button.clicked.connect(self.perform_dfs)

        self.limited_dfs_button = QPushButton("Perform Limited DFS")
        self.limited_dfs_button.clicked.connect(self.perform_limited_dfs)

        self.ucs_button = QPushButton("Perform UCS")
        self.ucs_button.clicked.connect(self.perform_ucs)

        self.greedy_button = QPushButton("Perform greedy")
        self.greedy_button.clicked.connect(self.perform_greedy)

        self.iterative_button = QPushButton("Perform iterative")
        self.iterative_button.clicked.connect(self.perform_iterative)

        self.bfs_button = QPushButton("Perform BFS")
        self.bfs_button.clicked.connect(self.perform_bfs)
        
        self.astar_button = QPushButton("Perform A* Search")
        self.astar_button.clicked.connect(self.perform_astar)

        # Add buttons to the left panel
        left_panel.addWidget(self.dfs_button)
        left_panel.addWidget(self.limited_dfs_button)
        left_panel.addWidget(self.ucs_button )
        left_panel.addWidget(self.greedy_button )
        left_panel.addWidget(self.iterative_button )
        left_panel.addWidget(self.bfs_button)
        left_panel.addWidget(self.astar_button)
        

        # Add Reset Algorithm button
        self.reset_algorithm_button = QPushButton("Reset Algorithm")
        self.reset_algorithm_button.clicked.connect(self.reset_algorithm)
        left_panel.addWidget(self.reset_algorithm_button)

        left_panel.addStretch()  # Push the buttons to the top

        # Right Panel Layout for Controls and Tree Visualization
        right_panel = QVBoxLayout()
        main_layout.addLayout(right_panel)  # Add the right panel to the main layout

        # Node Input Fields
        controls = QHBoxLayout()
        self.char_input = QLineEdit()
        self.char_input.setPlaceholderText("Character")
        self.heuristic_input = QLineEdit()
        self.heuristic_input.setPlaceholderText("Heuristic")
        self.parent_input = QLineEdit()
        self.parent_input.setPlaceholderText("Parent Node")
        self.path_cost = QLineEdit()
        self.path_cost.setPlaceholderText("Path Cost")

        controls.addWidget(QLabel("Node:"))
        controls.addWidget(self.char_input)
        controls.addWidget(QLabel("Heuristic:"))
        controls.addWidget(self.heuristic_input)
        controls.addWidget(QLabel("Parent:"))
        controls.addWidget(self.parent_input)
        controls.addWidget(QLabel("Path Cost:"))
        controls.addWidget(self.path_cost)

        # Buttons for Other Actions
        self.add_button = QPushButton("Add Node")
        self.delete_button = QPushButton("Delete Node")
        self.reset_button = QPushButton("Reset Tree")
        self.add_button.clicked.connect(self.add_node)
        self.delete_button.clicked.connect(self.delete_node)
        self.reset_button.clicked.connect(self.reset_tree)
        controls.addWidget(self.add_button)
        controls.addWidget(self.delete_button)
        controls.addWidget(self.reset_button)

        # Add the tree view and controls to the right panel
        right_panel.addWidget(self.view)
        right_panel.addLayout(controls)

        # Initialize the tree root and other variables
        self.tree_root = None
        self.node_positions = {}
        self.node_graphics = {}
        self.algorithm_state = {}  # State of the algorithm
    def reset_node_color(self, char):
        """Resets the color of a node to its original state."""
        if char in self.node_graphics:
            ellipse, _, _ = self.node_graphics[char]
            ellipse.setBrush(QBrush(Qt.yellow))  # Reset to yellow   
    def reset_algorithm(self):
        """Reset algorithm state without resetting the tree."""
      
        self.algorithm_state.clear()
        for item in self.scene.items():
            if isinstance(item, QGraphicsEllipseItem):
                item.setBrush(QBrush(Qt.yellow))  # Reset node color back to yellow
            elif isinstance(item, QGraphicsLineItem):
                item.setPen(QPen(Qt.black, 4))  # Reset edge color to black and line width
            elif isinstance(item, QGraphicsTextItem):
                item.setDefaultTextColor(Qt.black)  # Reset text color to black
    
        QMessageBox.information(self, "Reset Algorithm", "Algorithm state has been reset!")   
    def redraw_tree(self, node):
        """Recursively draws the tree based on updated positions."""
        if not node:
            return

        x, y = self.node_positions[node.char]
        self.draw_node(node, x, y)

        for child in node.children:
            child_x, child_y = self.node_positions[child.char]
            self.draw_edge(x, y, child_x, child_y, cost=child.path_cost)
            self.redraw_tree(child)

    def recalculate_positions(self, node, x, y, spacing):
        """Recursively calculates positions for each node to avoid overlap."""
        if not node:
            return

        # Set the current node's position
        self.node_positions[node.char] = (x, y)

        num_children = len(node.children)
        if num_children > 0:
            # Calculate the total width required for all children
            total_child_width = spacing * (num_children - 1)

            # Start placing the children evenly spaced around the current node's position
            start_x = x - (total_child_width // 2)
            for i, child in enumerate(node.children):
                child_x = start_x + i * spacing
                child_y = y + 100  # Move the child node 100px below the current node
                self.recalculate_positions(child, child_x, child_y, spacing // 2)




    def add_node(self):
        char = self.char_input.text().strip()
        heuristic = self.heuristic_input.text().strip()
        path_cost = self.path_cost.text().strip()
        parent_char = self.parent_input.text().strip()

        if not char or not heuristic:
            return  # Ensure inputs are valid

        # Root Node
        if self.tree_root is None:
            width = self.view.width()
            height = self.view.height()
            #print(f"View size: width={width}, height={height}")

            # Create the root node
            self.tree_root = Node(char, float(heuristic), path_cost=float(path_cost) if path_cost else 0)
            # Update the root node position to the desired position
            self.node_positions[char] = (width // 4, height // 4)  # Adjust the positioning as per your requirements
            self.draw_node(self.tree_root, width // 4, height // 4)
            self.clear_inputs()
            return  # Return after adding the root node (no parent required)

        # Find Parent Node
        if parent_char not in self.node_positions:
            return  # Parent not found

        parent_node = self.find_node(self.tree_root, parent_char)
        if not parent_node:
            return

        # Add as a new Child Node
        child_node = Node(char, float(heuristic), path_cost=float(path_cost) if path_cost else 0)
        parent_node.children.append(child_node)

        # Recalculate positions and redraw the tree
        self.node_positions.clear()  # Clear previous positions
        self.scene.clear()  # Clear the scene
        
        self.recalculate_positions(self.tree_root, self.view.width() // 4, self.view.height() // 4, 300)
        self.redraw_tree(self.tree_root)

        self.clear_inputs()

    def reset_tree(self):
        """Resets the tree by clearing the scene and all data structures."""
        self.scene.clear()
        self.tree_root = None
        self.node_positions = {}
        self.node_graphics = {}
        self.goal_node = None  # Reset the goal node

        # Clear input fields
        self.clear_inputs()
    
    def delete_node(self):
        """Delete a node from the tree."""
        char = self.char_input.text().strip()
        if char not in self.node_positions:
            return  # Node not found

        # Find the node to delete
        node_to_delete = self.find_node(self.tree_root, char)

        # Prevent deleting parent nodes with children
        if node_to_delete and node_to_delete.children:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Deletion Error")
            msg_box.setText("Cannot delete a parent node with children.")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec_()
            return

        # Remove the edge to the parent
        self.remove_edge_to_parent(char)

        # Remove node graphics
        if char in self.node_graphics:
            for item in self.node_graphics[char]:
                self.scene.removeItem(item)
            del self.node_graphics[char]

        # Remove node from the tree
        self.delete_node_recursive(self.tree_root, char)
        del self.node_positions[char]

        # Clear the input field after deletion
        self.char_input.clear()

    def remove_edge_to_parent(self, char):
        """Remove the edge and cost text connecting the node to its parent."""
        if char not in self.node_positions:
            return

        parent = self.find_parent(self.tree_root, char)
        if not parent or parent.char not in self.node_positions:
            return

        parent_pos = self.node_positions[parent.char]
        child_pos = self.node_positions[char]

        # Remove the line and cost label
        items_to_remove = []
        for item in self.scene.items():
            if isinstance(item, QGraphicsLineItem):
                line = item.line()
                if (
                    (line.x1() == parent_pos[0] and line.y1() == parent_pos[1] and
                     line.x2() == child_pos[0] and line.y2() == child_pos[1]) or
                    (line.x1() == child_pos[0] and line.y1() == child_pos[1] and
                     line.x2() == parent_pos[0] and line.y2() == parent_pos[1])
                ):
                    items_to_remove.append(item)
            elif isinstance(item, QGraphicsTextItem):
                mid_x = (parent_pos[0] + child_pos[0]) // 2
                mid_y = (parent_pos[1] + child_pos[1]) // 2
                if abs(item.pos().x() - (mid_x - 25)) < 5 and abs(item.pos().y() - (mid_y - 10)) < 5:
                    items_to_remove.append(item)

        for item in items_to_remove:
            self.scene.removeItem(item)

    def delete_node_recursive(self, current, char):
        """Helper function to delete a node from the tree."""
        if not current:
            return None

        # Remove the node from the children list
        if any(child.char == char for child in current.children):
            current.children = [child for child in current.children if child.char != char]
        else:
            for child in current.children:
                self.delete_node_recursive(child, char)

        return current

    def find_node(self, current, char):
        """Find a node in the tree by its character."""
        if not current:
            return None
        if current.char == char:
            return current
        # Iterate through all children, not just left or right
        for child in current.children:
            result = self.find_node(child, char)
            if result:
                return result
        return None

    def find_parent(self, current, char):
        """Find the parent of a node."""
        if not current:
            return None
        # Check if the current node is the parent of any child
        for child in current.children:
            if child.char == char:
                return current
            result = self.find_parent(child, char)
            if result:
                return result
        return None


    def draw_edge(self, x1, y1, x2, y2, cost):
        """Draw an edge between two nodes."""
        line = QGraphicsLineItem(x1, y1, x2, y2)
        pen = QPen(Qt.black, 4)  # Set the pen width to 4 for a bolder line
        line.setPen(pen)
        self.scene.addItem(line)  # Add the edge first, ensuring it stays behind nodes

        mid_x = (x1 + x2) // 2
        mid_y = (y1 + y2) // 2
        cost_text = QGraphicsTextItem(f"{cost}")
        cost_text.setPos(mid_x - 25, mid_y - 10)
        cost_text.setDefaultTextColor(Qt.black)
        self.scene.addItem(cost_text)

    def draw_node(self, node, x, y):
        """Draw a node at the given position."""
        radius = 23
        ellipse = QGraphicsEllipseItem(x - radius, y - radius, 2.5 * radius, 2.5 * radius)
        ellipse.setBrush(QBrush(Qt.yellow))
        ellipse.setPen(QPen(Qt.black))
        self.scene.addItem(ellipse)  # Add node after edge to ensure it's on top

        char_text = QGraphicsTextItem(node.char)
        char_text.setPos(x - 3, y - 15)
        self.scene.addItem(char_text)

        heuristic_text = QGraphicsTextItem(f"{node.heuristic}")
        heuristic_text.setPos(x - 5, y + 5)
        self.scene.addItem(heuristic_text)

        # Set Z-value for the node to ensure it appears above the edge
        ellipse.setZValue(1)
        char_text.setZValue(2)
        heuristic_text.setZValue(2)

        self.node_graphics[node.char] = [ellipse, char_text, heuristic_text]
        

    def clear_inputs(self):
        self.char_input.clear()
        self.heuristic_input.clear()
        self.parent_input.clear()
        self.path_cost.clear()  # Corrected line

    def visualize_path(self, path):
        """Highlight the path from the traversal result."""
        if not path or len(path) < 2:
            return

        # Highlight the nodes in the path
        for char in path:
            if char in self.node_graphics:
                ellipse, _, _ = self.node_graphics[char]
                ellipse.setBrush(QBrush(Qt.green))
                QApplication.processEvents()
                time.sleep(0.5)

        # Highlight the edges in the path
        for i in range(len(path) - 1):
            parent_char = path[i]
            child_char = path[i + 1]

            # Find the parent node in the tree
            parent_node = self.find_node(self.tree_root, parent_char)

            # If parent node exists, highlight the edge to the child
            if parent_node:
                for child in parent_node.children:
                    if child.char == child_char:
                        parent_pos = self.node_positions.get(parent_char)
                        child_pos = self.node_positions.get(child_char)
                        if parent_pos and child_pos:
                            self.highlight_edge(parent_pos, child_pos)

    # Handle potential branching in the path
        for i in range(len(path) - 2):
            current_char = path[i]
            current_node = self.find_node(self.tree_root, current_char)
            for child in current_node.children:
                if child.char in path[i+2:]:  # Check if any descendant in the path
                    parent_pos = self.node_positions.get(current_char)
                    child_pos = self.node_positions.get(child.char)
                    if parent_pos and child_pos:
                        self.highlight_edge(parent_pos, child_pos)

    def is_descendant(self, current, parent, child):
        """Checks if child is a descendant of parent in the tree."""
        if not current:
            return False
        if current.char == child:
            return True
        # Check through all children of the current node
        for child_node in current.children:
            if self.is_descendant(child_node, parent, child):
                return True
        return False

    def highlight_edge(self, parent_pos, child_pos):
        """Highlight the edge between two positions."""
        for item in self.scene.items():
            if isinstance(item, QGraphicsLineItem):
                line = item.line()
                if (
                    (line.x1() == parent_pos[0] and line.y1() == parent_pos[1] and
                    line.x2() == child_pos[0] and line.y2() == child_pos[1]) or
                    (line.x1() == child_pos[0] and line.y1() == child_pos[1] and
                    line.x2() == parent_pos[0] and line.y2() == parent_pos[1])
                ):
                    item.setPen(QPen(Qt.green, 3))  # Green, thicker line for the edge
                    QApplication.processEvents()
                    time.sleep(0.5)
    def highlight_edge2(self, parent_pos, child_pos):
        """Highlight the edge between two positions."""
        for item in self.scene.items():
            if isinstance(item, QGraphicsLineItem):
                line = item.line()
                if (
                    (line.x1() == parent_pos[0] and line.y1() == parent_pos[1] and
                    line.x2() == child_pos[0] and line.y2() == child_pos[1]) or
                    (line.x1() == child_pos[0] and line.y1() == child_pos[1] and
                    line.x2() == parent_pos[0] and line.y2() == parent_pos[1])
                ):
                    item.setPen(QPen(Qt.blue, 3))  # Green, thicker line for the edge
                    
    #############################################################
    def perform_dfs(self):
        """Performs Depth-First Search on the tree and visualizes the path."""
        if not self.tree_root:
            return  # No tree to traverse

        # Get user input for the goal nodes
        goal_node_chars, ok = QInputDialog.getText(self, "Choose Goals", "Enter the characters of the goal nodes (comma-separated):")
        if not ok or not goal_node_chars:
            return  # User canceled or entered empty input

        # Convert input into a set of goal nodes
        goal_node_chars = {char.strip() for char in goal_node_chars.split(",")}
        if not goal_node_chars:
            QMessageBox.warning(self, "Invalid Input", "Please enter at least one valid goal node.")
            return

        # Use a stack (implemented with deque) for DFS
        stack = deque([(self.tree_root, None)])  # Stack contains (current_node, parent_node)
        visited = set()  # Keep track of visited nodes
        path = []  # Store the path during DFS

        def highlight_step():
            """Inner function to highlight the next step."""
            if not stack:
                # All nodes processed, but no goal was found
                QMessageBox.information(self, "DFS Result", "None of the goal nodes were reachable through DFS.")
                return

            current_node, parent_node = stack.pop()

            # Highlight the current node
            if current_node.char in self.node_graphics:
                ellipse, _, _ = self.node_graphics[current_node.char]
                ellipse.setBrush(QBrush(Qt.blue))  # Set the node color to blue
                ellipse.update()  # Force the ellipse to refresh visually

            # Mark the node as visited
            visited.add(current_node.char)
            path.append(current_node.char)  # Add to the traversal path

            # Highlight the edge from parent to current
            if parent_node:
                parent_pos = self.node_positions[parent_node.char]
                current_pos = self.node_positions[current_node.char]
                self.highlight_edge2(parent_pos, current_pos)

            # Check if the current node is one of the goal nodes
            if current_node.char in goal_node_chars:
                # Highlight the path and stop further processing
                self.visualize_path(path)
                QMessageBox.information(self, "DFS Result", f"Goal Node Found: {current_node.char}\nDFS Path: {' -> '.join(path)}")
                return  # Stop the search

            # Process children in reverse order for DFS (last child is processed first)
            for child in reversed(current_node.children):
                if child.char not in visited:
                    stack.append((child, current_node))

            # Continue to the next step
            QTimer.singleShot(800, highlight_step)  # 800ms delay between steps

        # Start the visualization
        highlight_step()
        
    ############################################################################   
    def perform_limited_dfs(self):
        """Performs Depth-First Search with a user-defined depth limit."""
        if not self.tree_root:
            return  # No tree to traverse

        # Get user input for the goal nodes
        goal_node_chars, ok = QInputDialog.getText(self, "Choose Goals", "Enter the characters of the goal nodes (comma-separated):")
        if not ok or not goal_node_chars:
            return  # User canceled or entered empty input

        # Convert input into a set of goal nodes
        goal_node_chars = {char.strip() for char in goal_node_chars.split(",")}
        if not goal_node_chars:
            QMessageBox.warning(self, "Invalid Input", "Please enter at least one valid goal node.")
            return

        # Get user input for the depth limit (level)
        depth_limit, ok = QInputDialog.getInt(self, "Depth Limit", "Enter the maximum depth for DFS:", min=0)
        if not ok:
            return  # User canceled or entered invalid depth

        # Use a stack (implemented with deque) for DFS
        stack = deque([(self.tree_root, None, 0)])  # Stack contains (current_node, parent_node, depth)
        visited = set()  # Keep track of visited nodes
        path = []  # Store the path during DFS
        found_goal = False  # Flag to check if goal node is found

        def highlight_step():
            """Inner function to highlight the next step."""
            nonlocal found_goal  # Declare found_goal as nonlocal to modify the outer variable

            if not stack:
                # All nodes processed, but no goal was found
                if found_goal:
                    QMessageBox.information(self, "DFS Result", f"Goal Node Found: {current_node.char}\nDFS Path: {' -> '.join(path)}")
                    
                else:
                    QMessageBox.information(self, "DFS Result", "None of the goal nodes were found within the depth limit.")
                return

            current_node, parent_node, current_depth = stack.pop()

            # Highlight the current node
            if current_node.char in self.node_graphics:
                ellipse, _, _ = self.node_graphics[current_node.char]
                ellipse.setBrush(QBrush(Qt.blue))  # Set the node color to blue
                ellipse.update()  # Force the ellipse to refresh visually

            # Mark the node as visited
            visited.add(current_node.char)
            path.append(current_node.char)  # Add to the traversal path

            # Highlight the edge from parent to current
            if parent_node:
                parent_pos = self.node_positions[parent_node.char]
                current_pos = self.node_positions[current_node.char]
                self.highlight_edge2(parent_pos, current_pos)

            # Check if the current node is one of the goal nodes
            if current_node.char in goal_node_chars:
                found_goal = True
                self.visualize_path(path)
                # Stop the search if goal is found
                QTimer.singleShot(500, lambda: QMessageBox.information(self, "DFS Result", f"Goal Node Found: {current_node.char}\nDFS Path: {' -> '.join(path)}"))

                return

            # Process children in reverse order for DFS (last child is processed first) if within depth limit
            if current_depth < depth_limit:
                for child in reversed(current_node.children):
                    if child.char not in visited:
                        stack.append((child, current_node, current_depth + 1))

            # Continue to the next step
            QTimer.singleShot(800, highlight_step)  # 800ms delay between steps

        # Start the visualization
        highlight_step()
        
    ##################### TO BE CONTINUED ########################################
    def perform_iterative(self):
        goals = simpledialog.askstring("Input", "Enter the goal node values (comma-separated)")
        if not goals:
            QMessageBox.warning(self, "Error", "Please enter at least one goal node.")
            return

        goals = [goal.strip() for goal in goals.split(',') if goal.strip()]
        if not goals:
            QMessageBox.warning(self, "Error", "Invalid input. Please enter valid goal nodes.")
            return

        def get_max_depth():
            max_depth = simpledialog.askinteger("Input", "Enter the maximum depth (positive integer)")
            if max_depth is None:
                return None  # Return None to indicate no valid input
            if max_depth <= 0:
                QMessageBox.warning(self, "Error", "Please enter a valid maximum depth.")
                return None
            else:
                return max_depth

        while True:
            max_depth = get_max_depth()
            if max_depth is None:
                break  # Exit the loop if the user chooses not to retry

            self.reset_visualization_to_original()  # Reset visualization at the start of each new depth level

            depth_limit = max_depth
            stack = deque([(self.tree_root, None, 0)])  # (current_node, parent_node, current_depth)
            path = []
            visited = set()
            found_goal = False

            def highlight_step():
                nonlocal found_goal

                if not stack:
                    if found_goal:
                        return
                    else:
                        QMessageBox.information(self, "Search Result", "None of the goal nodes were reachable within the given depth.")
                        return

                current_node, parent_node, current_depth = stack.pop()

                if current_node.char in self.node_graphics:
                    ellipse, _, _ = self.node_graphics[current_node.char]
                    ellipse.setBrush(QBrush(Qt.blue))  # Highlight the node
                    ellipse.update()

                visited.add(current_node.char)
                path.append(current_node.char)

                if parent_node:
                    parent_pos = self.node_positions[parent_node.char]
                    current_pos = self.node_positions[current_node.char]
                    self.highlight_edge2(parent_pos, current_pos)

                if current_node.char in goals:
                    found_goal = True
                    self.visualize_path(path)
                    QTimer.singleShot(500, lambda: QMessageBox.information(self, "Result", f"Goal Node Found: {current_node.char}\nPath: {' -> '.join(path)}"))
                    return

                if current_depth < depth_limit:
                    for child in reversed(current_node.children):
                        if child.char not in visited:
                            stack.append((child, current_node, current_depth + 1))

                QTimer.singleShot(800, highlight_step)  # Delay between steps

            highlight_step()
            if found_goal:
                break

    def reset_visualization_to_original(self):
        for node_char, (ellipse, _, _) in self.node_graphics.items():
            ellipse.setBrush(QBrush(Qt.yellow))  # Reset to original color
            ellipse.update()
        for item in self.scene.items():
            if isinstance(item, QGraphicsLineItem):
                item.setPen(QPen(Qt.black))  # Reset edges to original color
                item.update()
                
    ###########################################################################
    def perform_greedy(self):
        goals = simpledialog.askstring("Input", "Enter the goal nodes (comma-separated)")
        if not goals:
            QMessageBox.warning(self, "Error", "Please enter the goal nodes.")
            return

        goal_nodes = [goal.strip() for goal in goals.split(",")]
        if self.tree_root is None:
            QMessageBox.warning(self, "Error", "The tree is empty.")
            return

        for goal in goal_nodes:
            if goal not in self.node_positions:
                QMessageBox.warning(self, "Error", f"Goal node '{goal}' does not exist in the tree.")
                return

        priority_queue = []
        heapq.heappush(priority_queue, (self.tree_root.heuristic, self.tree_root, [self.tree_root.char], self.tree_root.heuristic))
        visited = set()

        while priority_queue:
            total_heuristic, current_node, path, path_cost = heapq.heappop(priority_queue)

            if current_node.char in visited:
                continue

            visited.add(current_node.char)

            if current_node.char in self.node_graphics:
                ellipse, _, _ = self.node_graphics[current_node.char]
                ellipse.setBrush(QBrush(Qt.blue))
                QApplication.processEvents()
                time.sleep(0.5)

            if current_node.char in goal_nodes:
                QMessageBox.information(self, "Result", f"Path to reach '{current_node.char}' (using Greedy Search): {' -> '.join(path)} with total heuristic cost {path_cost}")
                self.visualize_path(path)
                return

            for child in current_node.children:
                if child.char not in visited:
                    new_path_cost = path_cost + child.heuristic
                    heapq.heappush(priority_queue, (child.heuristic, child, path + [child.char], new_path_cost))

        QMessageBox.information(self, "Result", f"None of the goal nodes are reachable.")

    
    ##################################################################################################
    def perform_bfs(self):
        """Perform Breadth-First Search (BFS) with step-by-step visualization."""
        if not self.tree_root:
            QMessageBox.warning(self, "Error", "Tree is empty. Add nodes first.")
            return

        start_char, ok_start = QInputDialog.getText(self, "BFS", "Enter the starting node:")
        if not ok_start or not start_char.strip():
            return
        start_char = start_char.strip()

        goals_input, ok_goal = QInputDialog.getText(self, "BFS", "Enter the goal nodes (comma-separated):")
        if not ok_goal or not goals_input.strip():
            return
        goal_chars = [goal.strip() for goal in goals_input.split(",")]

        if start_char not in self.node_positions:
            QMessageBox.warning(self, "Error", f"Node {start_char} does not exist.")
            return
        for goal_char in goal_chars:
            if goal_char not in self.node_positions:
                QMessageBox.warning(self, "Error", f"Node {goal_char} does not exist.")
                return

        queue = deque([(start_char, [start_char])])
        visited = set()
        traversal = []

        while queue:
            current_char, path = queue.popleft()

            if current_char in visited:
                continue

            visited.add(current_char)
            traversal.append(current_char)

            if current_char in self.node_graphics:
                ellipse, _, _ = self.node_graphics[current_char]
                ellipse.setBrush(QBrush(Qt.yellow))
                QApplication.processEvents()
                time.sleep(0.5)

            if current_char in goal_chars:
                self.visualize_path(path)
                QMessageBox.information(
                    self, "BFS Result", f"Traversal: {' -> '.join(traversal)}\nPath to Goal: {' -> '.join(path)}"
                )
                return

            current_node = self.find_node(self.tree_root, current_char)
            for child in current_node.children:
                if child.char not in visited:
                    queue.append((child.char, path + [child.char]))

            if current_char in self.node_graphics:
                ellipse.setBrush(QBrush(Qt.blue))
                QApplication.processEvents()
                time.sleep(0.5)

        QMessageBox.information(
            self, "BFS Result", f"Traversal: {' -> '.join(traversal)}\nGoal nodes not found."
        )
        
    #####################
    # This is the A* Algorithm with multiple goal support and alphabetical tie-breaking
    def perform_astar(self):
       """Performs A* Search on the tree for multiple goals and visualizes the paths."""
       if not self.tree_root:
           return  # No tree to traverse
   
       # Get user input for the goal nodes
       goal_nodes_input, ok = QInputDialog.getText(self, "Choose Goals", "Enter the characters of the goal nodes separated by commas:")
   
       if not ok or not goal_nodes_input:
           return  # User canceled or entered empty input
   
       goal_node_chars = [char.strip() for char in goal_nodes_input.split(",") if char.strip()]
       goal_nodes = [self.find_node(self.tree_root, char) for char in goal_node_chars]
   
       if any(node is None for node in goal_nodes):
           QMessageBox.warning(self, "Error", "One or more goal nodes not found!")
           return
   
       # Ask user whether to stop search after finding the first goal
       stop_after_first, ok = QInputDialog.getItem(
           self, "Search Mode",
           "Stop search after finding:",
           ["First goal", "All goals"],
           editable=False
       )
   
       if not ok:
           return  # User canceled
   
       stop_after_first = stop_after_first == "First goal"
   
       # Priority queue and sets
       open_set = []  # Priority queue: (f_score, id(node), node)
       heapq.heappush(open_set, (0, id(self.tree_root), self.tree_root))
   
       closed_set = set()
       came_from = {}
       g_score = {self.tree_root: 0}  # Cost from start to node
   
       found_goals = set()
       paths = {}
   
       def highlight_step():
           """Inner function to visualize the next step."""
           nonlocal found_goals
   
           if not open_set:
               # No more nodes to process
               if not found_goals:
                   QMessageBox.information(self, "A* Result", "None of the goal nodes were found.")
               else:
                   # Visualize all paths after all goals are found
                   for goal_char, path in paths.items():
                       self.visualize_path(path)
                       QMessageBox.information(self, "Goal Found", f"Goal: {goal_char}, Path: {' -> '.join(path)}")
               return
   
           # Pop the node with the lowest f_score
           current_f_score, _, current_node = heapq.heappop(open_set)
   
           # Skip this node if it's already expanded
           if current_node in closed_set:
               QTimer.singleShot(800, highlight_step)  # Continue to the next step
               return
   
           # Highlight the current node
           if current_node.char in self.node_graphics:
               ellipse, _, _ = self.node_graphics[current_node.char]
               ellipse.setBrush(QBrush(Qt.blue))  # Set the node color to blue
               ellipse.update()  # Force the ellipse to refresh visually
   
           # Mark the node as expanded
           closed_set.add(current_node)
   
           # Goal check
           if current_node.char in goal_node_chars and current_node.char not in found_goals:
               path = []
               temp_node = current_node
   
               while temp_node:
                   path.append(temp_node.char)
                   temp_node = came_from.get(temp_node)
   
               path.reverse()
               paths[current_node.char] = path
   
               # Add the goal to the found set
               found_goals.add(current_node.char)
   
               if stop_after_first:
                   # Visualize and show the path for the first goal found
                   self.visualize_path(path)
                   QMessageBox.information(self, "Goal Found", f"Goal: {current_node.char}, Path: {' -> '.join(path)}")
                   return
   
               if len(found_goals) == len(goal_nodes):
                   # Visualize all paths after all goals are found
                   for goal_char, path in paths.items():
                       self.visualize_path(path)
                       QMessageBox.information(self, "Goal Found", f"Goal: {goal_char}, Path: {' -> '.join(path)}")
                   return
   
           # Explore neighbors
           for child in current_node.children:
               tentative_g_score = g_score[current_node] + child.path_cost
   
               # Only consider this path if it's better
               if tentative_g_score < g_score.get(child, float('inf')):
                   came_from[child] = current_node
                   g_score[child] = tentative_g_score
                   f_score = tentative_g_score + child.heuristic
   
                   # Push the updated node into open_set with tie-breaking
                   heapq.heappush(open_set, (f_score, id(child), child))
   
           # Sort the open_set by f_score and break ties alphabetically by node.char
           open_set.sort(key=lambda x: (x[0], x[2].char))
   
           # Continue to the next step
           QTimer.singleShot(800, highlight_step)  # 800ms delay between steps

      # Start the visualization
       highlight_step()
                     
    ##################################################
    def perform_ucs(self):
            """Perform Uniform Cost Search (UCS) on the tree."""
            goals_input = simpledialog.askstring("Input", "Enter the goal nodes (comma-separated)")
            if not goals_input:
                QMessageBox.warning(self, "Error", "Please enter at least one goal node.")
                return
            
            goals = [goal.strip() for goal in goals_input.split(',')]

            if self.tree_root is None:
                QMessageBox.warning(self, "Error", "The tree is empty.")
                return

            for goal in goals:
                if goal not in self.node_positions:
                    QMessageBox.warning(self, "Error", f"Goal node '{goal}' does not exist in the tree.")
                    return

            priority_queue = []
            heapq.heappush(priority_queue, (0, self.tree_root.char, self.tree_root, [self.tree_root.char]))
            visited = set()

            while priority_queue:
                total_cost, _, current_node, path = heapq.heappop(priority_queue)

                if current_node.char in visited:
                    continue

                visited.add(current_node.char)

                if current_node.char in self.node_graphics:
                    ellipse, _, _ = self.node_graphics[current_node.char]
                    ellipse.setBrush(QBrush(Qt.blue))
                    QApplication.processEvents()
                    time.sleep(0.5)

                if current_node.char in goals:
                    QMessageBox.information(self, "Result", f"Path to reach '{current_node.char}' (using UCS): {' -> '.join(path)} with total cost {total_cost}")
                    self.visualize_path(path)
                    return

                for child in current_node.children:
                    if child.char not in visited:
                        new_total_cost = total_cost + child.path_cost
                        heapq.heappush(priority_queue, (new_total_cost, child.char, child, path + [child.char]))

            QMessageBox.information(self, "Result", "None of the goal nodes are reachable.")






if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TreeVisualizer()
    window.show()
    sys.exit(app.exec_())
    