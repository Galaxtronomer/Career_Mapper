# Career Mapper

Career Mapper is a web-based interactive career mapping tool built using **Python** and **Leaflet.js**.

It allows you to:
- 🗺️ Add, move, and remove location drops on the map (e.g., city of your college/university/institute).
- ✍️ Add, edit, rotate, and remove custom text labels (e.g., name of your college/university/institute).
- ➰ Draw curves with arrows between points (e.g., show your movements from one place to another).

---

## Files

- **career_mapper.py** → Runs the tool (⚠️ does **not autosave**; changes in the browser will not persist).
- **career_mapper_autosave.py** → Runs the tool with autosave (✅ changes made in the browser will persist when reloaded).
- **career_map.html** → The generated HTML file.
- **map_mapper.png** → Screenshot used in this README.

---

## How to Run

Run the tool without autosave:

```bash
python career_mapper.py
