import sqlite3
import os
from datetime import datetime

DB_FILE = "inventory.db"

# Основна ініціалізація бази

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Таблиця інвентаря
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY,
        name TEXT,
        quantity INTEGER,
        inv_number TEXT,
        category TEXT,
        added_at TEXT,
        location_id INTEGER,
        status TEXT,
        image_path TEXT,
        custom_fields TEXT,
        description TEXT,
        comments TEXT
    )''')
    # Таблиця місць зберігання (ієрархія)
    c.execute('''CREATE TABLE IF NOT EXISTS locations (
        id INTEGER PRIMARY KEY,
        name TEXT,
        parent_id INTEGER
    )''')
    # Таблиця категорій
    c.execute('''CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE
    )''')
    # Таблиця статусів
    c.execute('''CREATE TABLE IF NOT EXISTS statuses (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE
    )''')
    # Таблиця історії змін
    c.execute('''CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY,
        inventory_id INTEGER,
        action TEXT,
        timestamp TEXT,
        details TEXT
    )''')
    # Таблиця користувацьких полів (метадані)
    c.execute('''CREATE TABLE IF NOT EXISTS custom_fields (
        id INTEGER PRIMARY KEY,
        name TEXT,
        field_type TEXT
    )''')
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(DB_FILE)

# --- CRUD для інвентаря ---
def get_inventory(sort_by="name", ascending=True, filters=None):
    import traceback
    try:
        conn = get_connection()
        c = conn.cursor()
        query = "SELECT * FROM inventory"
        params = []
        if filters:
            filter_clauses = []
            for k, v in filters.items():
                filter_clauses.append(f"{k}=?")
                params.append(v)
            if filter_clauses:
                query += " WHERE " + " AND ".join(filter_clauses)
        query += f" ORDER BY {sort_by} {'ASC' if ascending else 'DESC'}"
        c.execute(query, params)
        items = c.fetchall()
        conn.close()
        return items
    except Exception as ex:
        print(f"Помилка у get_inventory: {ex}\n{traceback.format_exc()}")
        return []

def add_inventory(item):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO inventory (name, quantity, inv_number, category, added_at, location_id, status, image_path, custom_fields, description, comments) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (item['name'], item['quantity'], item['inv_number'], item['category'], item['added_at'], item['location_id'], item['status'], item['image_path'], item['custom_fields'], item.get('description', ''), item.get('comments', '')))
    conn.commit()
    conn.close()

def edit_inventory(item_id, item):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE inventory SET name=?, quantity=?, inv_number=?, category=?, added_at=?, location_id=?, status=?, image_path=?, custom_fields=?, description=?, comments=? WHERE id=?",
              (item['name'], item['quantity'], item['inv_number'], item['category'], item['added_at'], item['location_id'], item['status'], item['image_path'], item['custom_fields'], item.get('description', ''), item.get('comments', ''), item_id))
    conn.commit()
    conn.close()

def delete_inventory(item_id):
    """
    Delete an inventory item and its associated image file.
    
    Args:
        item_id (int): The ID of the inventory item to delete
    """
    conn = get_connection()
    c = conn.cursor()
    
    try:
        # First fetch image path to delete the file
        c.execute("SELECT image_path FROM inventory WHERE id=?", (item_id,))
        row = c.fetchone()
        
        if row and row[0]:  # If there's an image path
            img_path = row[0]
            if os.path.isfile(img_path):
                try:
                    # Delete the image file
                    os.remove(img_path)
                    print(f"[INFO] Видалено файл зображення: {img_path}")
                    
                    # Log directory info for debugging
                    img_dir = os.path.dirname(img_path)
                    print(f"[INFO] Залишаємо директорію: {img_dir}")
                    
                    try:
                        dir_contents = os.listdir(img_dir)
                        print(f"[DEBUG] Вміст директорії {img_dir}: {dir_contents}")
                    except Exception as list_err:
                        print(f"[WARN] Не вдалося отримати вміст директорії {img_dir}: {list_err}")
                            
                except Exception as ex:
                    # Log the error but continue with database deletion
                    print(f"[WARN] Не вдалося видалити файл зображення '{img_path}': {ex}")
    except Exception as ex:
        print(f"[ERROR] Помилка при отриманні шляху до зображення: {ex}")
    
    try:
        # Delete the database record
        c.execute("DELETE FROM inventory WHERE id=?", (item_id,))
        conn.commit()
        print(f"[INFO] Видалено запис інвентаря з ID: {item_id}")
    except Exception as db_err:
        print(f"[ERROR] Помилка при видаленні запису з бази даних: {db_err}")
        conn.rollback()
        raise  # Re-raise the exception to handle it in the UI
    finally:
        conn.close()

# --- Місця зберігання ---
def get_locations():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM locations")
    locations = c.fetchall()
    conn.close()
    return locations

def add_location(name, parent_id=None):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO locations (name, parent_id) VALUES (?, ?)", (name, parent_id))
    conn.commit()
    conn.close()

def edit_location(loc_id, name, parent_id=None):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE locations SET name=?, parent_id=? WHERE id=?", (name, parent_id, loc_id))
    conn.commit()
    conn.close()

def delete_location(loc_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM locations WHERE id=?", (loc_id,))
    conn.commit()
    conn.close()

# --- Категорії та статуси (унікальні значення з інвентаря) ---
def get_categories():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT DISTINCT name FROM categories")
    cats = [row[0] for row in c.fetchall() if row[0]]
    conn.close()
    return cats

def add_category(name):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO categories (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

def edit_category(old_name, new_name):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE categories SET name=? WHERE name=?", (new_name, old_name))
    conn.commit()
    conn.close()

def delete_category(name):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM categories WHERE name=?", (name,))
    conn.commit()
    conn.close()

def get_statuses():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT DISTINCT name FROM statuses")
    stats = [row[0] for row in c.fetchall() if row[0]]
    conn.close()
    return stats

def add_status(name):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO statuses (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

def edit_status(old_name, new_name):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE statuses SET name=? WHERE name=?", (new_name, old_name))
    conn.commit()
    conn.close()

def delete_status(name):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM statuses WHERE name=?", (name,))
    conn.commit()
    conn.close()

# --- Фільтрація ---
def filter_inventory(filters):
    return get_inventory(filters=filters)

# --- Експорт ---
def export_inventory(fmt="csv", filename="inventory_export"):  # fmt: csv, xlsx, pdf
    import pandas as pd
    items = get_inventory()
    df = pd.DataFrame(items, columns=["id", "name", "quantity", "inv_number", "category", "added_at", "location_id", "status", "image_path", "custom_fields", "description", "comments"])
    if fmt == "csv":
        df.to_csv(filename + ".csv", index=False)
        return filename + ".csv"
    elif fmt == "xlsx":
        df.to_excel(filename + ".xlsx", index=False)
        return filename + ".xlsx"
    elif fmt == "pdf":
        try:
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Spacer
            from reportlab.lib import colors
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            try:
                pdfmetrics.registerFont(TTFont("DejaVuSans", "DejaVuSans.ttf"))
                base_font = "DejaVuSans"
            except Exception:
                base_font = "Helvetica"  # fallback, може не показати кирилицю
            # Формуємо дані для таблиці
            header = ["Фото", "Назва", "К-сть", "№", "Категорія", "Статус", "Коментарі"]
            rows = []
            max_img_h = 60
            for _, name, qty, inv_num, cat, _, _, status, img_path, _, _, comments in items:
                # Завантажити та масштабувати зображення, якщо воно існує
                if img_path and os.path.isfile(img_path):
                    try:
                        img = Image(img_path, width=max_img_h, height=max_img_h)
                    except Exception:
                        img = ""
                else:
                    img = ""
                rows.append([img, name, str(qty), inv_num, cat, status, comments])

            doc = SimpleDocTemplate(filename + ".pdf", pagesize=landscape(A4))
            table_data = [header] + rows
            col_widths = [70, 140, 40, 80, 100, 80, 200]
            tbl = Table(table_data, colWidths=col_widths, repeatRows=1)
            tbl.setStyle(TableStyle([
                ("FONTNAME", (0,0), (-1,-1), base_font),
                ("FONTSIZE", (0,0), (-1,-1), 11),
                ("LEADING", (0,0), (-1,-1), 13),
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (2, 1), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            elems = [tbl]
            doc.build(elems)
            return filename + ".pdf"
        except Exception as ex:
            print("PDF export error:", ex)
            # fallback to CSV
            df.to_csv(filename + ".csv", index=False)
            return filename + ".csv"
    else:
        return None

def export_inventory_to_pdf(filename="inventory_export.pdf", location_id=None):
    """Експорт у PDF. Якщо location_id None – експортуємо все."""
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph
    from reportlab.lib import colors
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    import os

    # --- Утиліта для кириличних шрифтів ---
    _CYR_FONT = None
    def _register_cyrillic_font():
        nonlocal _CYR_FONT
        if _CYR_FONT:
            return _CYR_FONT
        candidates = [
            "DejaVuSans.ttf",
            r"C:\\Windows\\Fonts\\DejaVuSans.ttf",
            r"C:\\Windows\\Fonts\\arial.ttf",
            r"C:\\Windows\\Fonts\\arialuni.ttf",
            r"/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
        for path in candidates:
            if os.path.isfile(path):
                try:
                    pdfmetrics.registerFont(TTFont("CyrFont", path))
                    _CYR_FONT = "CyrFont"
                    return _CYR_FONT
                except Exception:
                    pass
        _CYR_FONT = "Helvetica"
        return _CYR_FONT

    font_name = _register_cyrillic_font()
    styles = getSampleStyleSheet()
    para_style = ParagraphStyle(
        name="cyr",
        parent=styles["BodyText"],
        fontName=font_name,
        fontSize=11,
        leading=13,
        wordWrap="CJK",
    )
    items = get_inventory(filters={"location_id": location_id} if location_id else None)
    table_data = [[Paragraph(t, para_style) for t in ["Назва", "№", "К-сть", "Категорія", "Статус", "Коментарі", "Фото"]]]
    for it in items:
        img_path = it[8] or ""
        img_elem = Image(img_path, width=60, height=60) if img_path and os.path.exists(img_path) else ""
        table_data.append([
            Paragraph(it[1] or "", para_style),
            Paragraph(it[3] or "", para_style),
            Paragraph(str(it[2]), para_style),
            Paragraph(it[4] or "", para_style),
            Paragraph(it[7] or "", para_style),
            Paragraph(it[11] or "", para_style),
            img_elem,
        ])
    col_widths = [150, 70, 45, 110, 90, 200, 70]
    doc = SimpleDocTemplate(filename, pagesize=landscape(A4))
    tbl = Table(table_data, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-1), font_name),
        ("FONTSIZE", (0,0), (-1,-1), 11),
        ("LEADING", (0,0), (-1,-1), 13),
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#455a64")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
        ("ALIGN", (2,1), (2,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
    ]))
    doc.build([tbl])
    return filename

# --- Резервне копіювання ---
def restore_db(backup_file):
    import shutil
    shutil.copy(backup_file, DB_FILE)

# --- Журнал змін ---
def log_history(inventory_id, action, details=""):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO history (inventory_id, action, timestamp, details) VALUES (?, ?, ?, ?)",
              (inventory_id, action, datetime.now().isoformat(), details))
    conn.commit()
    conn.close()

def get_history():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM history ORDER BY timestamp DESC")
    records = c.fetchall()
    conn.close()
    return records

# --- Користувацькі поля ---
def get_custom_fields():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM custom_fields")
    fields = c.fetchall()
    conn.close()
    return fields

def add_custom_field(name, field_type):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO custom_fields (name, field_type) VALUES (?, ?)", (name, field_type))
    conn.commit()
    conn.close()

def edit_custom_field(field_id, name, field_type):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE custom_fields SET name=?, field_type=? WHERE id=?", (name, field_type, field_id))
    conn.commit()
    conn.close()

def delete_custom_field(field_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM custom_fields WHERE id=?", (field_id,))
    conn.commit()
    conn.close()

# Перевіряє, чи існує інвентарний номер у базі
def inventory_inv_number_exists(inv_number: str, exclude_id: int | None = None) -> bool:
    """Повертає True, якщо інвентарний номер уже існує.

    Parameters
    ----------
    inv_number : str
        Інвентарний номер для перевірки.
    exclude_id : int | None
        Якщо вказано, рядок з таким id не враховується (корисно при редагуванні).
    """
    conn = get_connection()
    c = conn.cursor()
    if exclude_id is not None:
        c.execute("SELECT 1 FROM inventory WHERE inv_number=? AND id<>?", (inv_number, exclude_id))
    else:
        c.execute("SELECT 1 FROM inventory WHERE inv_number=?", (inv_number,))
    exists = c.fetchone() is not None
    conn.close()
    return exists
