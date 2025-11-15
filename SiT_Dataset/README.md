# SiT-Dataset Processing Steps

## 1. Map Creation Process

1. **Original Map Extraction**  
   - First, obtain the raw map data such as `Map.json` files like `CafeStreet.json` and `Courtyard.json`.

2. **Removing Z Values**  
   - Use scripts like `RemoveZ.py` to remove unnecessary Z-axis values from the 3D coordinate system.  
   - This converts the data into a 2D map format and truncates the decimal places beyond the second digit.

3. **File Format Conversion**  
   - Convert the modified JSON files into formats compatible with Gazebo (e.g., `model.sdf`, `model.config`).  
   - Use Python conversion tools like `Converter.py` to transform polyline and path information into the required structures.

4. **Simulation Environment Application**  
   - Import the converted files into the Gazebo simulator to build the environment.  
   - The simulation map is set up with files like `burger.model` and map files.

5. **Map Building and Environmental Parameter Setup**  
   - Reflect environmental components such as buildings, obstacles, and arenas to finalize the experimental map.

## 2. Trajectory Creation Process

1. **Basic Path Data Preparation**  
   - For each map, path data is prepared in text files like `trajectory.txt` with 10Hz sampling, recording IDs and path coordinates.

2. **Path Post-processing**  
   - Use dedicated scripts such as `trajectory_processor.py` to load and process these text files.  
   - This extracts or refines path points and other details; pedestrian (`goalbox`) and obstacle (`obstacle`) data are maintained in separate text files.

3. **Simulation Application**  
   - The extracted trajectory information is used for the robot's movement paths and mission routes within Gazebo.

---
> The map creation process follows the sequence: original data extraction → 2D conversion → environmental file conversion → simulation application.  
> The trajectory creation process flows as: path file preparation → post-processing → integration of environmental data → simulation application.

## 3. Reference

