import flet as ft

import os
import flet as ft
from db import get_inventory, add_inventory, edit_inventory, delete_inventory, get_locations, get_categories, get_statuses, filter_inventory, export_inventory, restore_db, inventory_inv_number_exists
from datetime import datetime
import shutil

SORT_FIELDS = [
    ("Назва", "name"),
    ("Кількість", "quantity"),
    ("Інвентарний номер", "inv_number"),
    ("Категорія", "category"),
    ("Дата додавання", "added_at"),
    ("Місце зберігання", "location_name"),
    ("Статус", "status")
]

FILTER_FIELDS = [
    ("Категорія", "category"),
    ("Місце зберігання", "location_id"),
    ("Статус", "status")
]

# Стале місце для збереження фотографій
IMAGES_DIR = "images"
os.makedirs(IMAGES_DIR, exist_ok=True)

# --- Діалоги для додавання категорії/статусу ---
def categories_dialog(page):
    from db import get_categories, add_category, delete_category
    categories = get_categories()

    def add_category_dialog_inner(page):
        new_cat = ft.TextField(label="Нова категорія", width=200)
        def save_new_cat(e):
            try:
                add_category(new_cat.value)
                page.snack_bar = ft.SnackBar(ft.Text(f"Категорію '{new_cat.value}' додано!"), open=True)
                page.dialog.open = False
                refresh_inventory(page)
                if hasattr(page, 'inventory_container'):
                    page.inventory_container.content = ft.Column(build_inventory_list(page), expand=True)
                categories_dialog(page)
                page.update()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Помилка додавання категорії: {ex}"), open=True)
                page.update()
        page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Додати категорію"),
            content=new_cat,
            actions=[ft.TextButton("Додати", on_click=save_new_cat), ft.TextButton("Скасувати", on_click=lambda e: (setattr(page.dialog, 'open', False), page.update()))],
            open=True
        )
        page.overlay.append(page.dialog)
        page.update()

    def edit_category_dialog(page, cat_name):
        from db import edit_category  # Must exist: edit_category(old_name, new_name)
        new_name = ft.TextField(label="Нова назва категорії", value=cat_name, width=200)
        def on_save(e):
            try:
                edit_category(cat_name, new_name.value)
                page.dialog.open = False
                refresh_inventory(page)
                if hasattr(page, 'inventory_container'):
                    page.inventory_container.content = ft.Column(build_inventory_list(page), expand=True)
                categories_dialog(page)
                page.update()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Помилка редагування категорії: {ex}"), open=True)
                page.update()
        page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Редагувати категорію"),
            content=new_name,
            actions=[
                ft.TextButton("Скасувати", on_click=lambda e: (setattr(page.dialog, 'open', False), page.update())),
                ft.TextButton("Зберегти", on_click=on_save),
            ],
            open=True
        )
        page.overlay.append(page.dialog)
        page.update()

    def delete_category_confirm(page, cat_name):
        def on_delete(e):
            delete_category(cat_name)
            page.dialog.open = False
            refresh_inventory(page)
            if hasattr(page, 'inventory_container'):
                page.inventory_container.content = ft.Column(build_inventory_list(page), expand=True)
            categories_dialog(page)
            page.update()
        page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Видалити '{cat_name}'?"),
            content=ft.Text("Видалити цю категорію?"),
            actions=[
                ft.TextButton("Скасувати", on_click=lambda e: (setattr(page.dialog, 'open', False), page.update())),
                ft.TextButton("Видалити", on_click=on_delete),
            ],
            open=True
        )
        page.overlay.append(page.dialog)
        page.update()

    cat_rows = [
        ft.Row([
            ft.Text(cat, size=16),
            ft.IconButton(content=ft.Text("✏️"), tooltip="Редагувати", on_click=lambda e, c=cat: edit_category_dialog(page, c)),
            ft.IconButton(content=ft.Text("🗑️"), tooltip="Видалити", on_click=lambda e, c=cat: delete_category_confirm(page, c)),
        ]) for cat in categories
    ]
    add_btn = ft.ElevatedButton("Додати категорію", icon="➕", on_click=lambda e: add_category_dialog_inner(page))
    page.dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Категорії"),
        content=ft.Column([add_btn] + cat_rows, scroll=ft.ScrollMode.AUTO),
        actions=[ft.TextButton("Закрити", on_click=lambda e: (setattr(page.dialog, 'open', False), page.update()))],
        open=True
    )
    page.overlay.append(page.dialog)
    page.update()

def add_category_dialog(page):
    # For compatibility: just open categories_dialog
    categories_dialog(page)


def statuses_dialog(page):
    from db import get_statuses, add_status, delete_status
    statuses = get_statuses()

    def add_status_dialog_inner(page):
        new_status = ft.TextField(label="Новий статус", width=160)
        def save_new_status(e):
            try:
                add_status(new_status.value)
                page.snack_bar = ft.SnackBar(ft.Text(f"Статус '{new_status.value}' додано!"), open=True)
                page.dialog.open = False
                refresh_inventory(page)
                if hasattr(page, 'inventory_container'):
                    page.inventory_container.content = ft.Column(build_inventory_list(page), expand=True)
                statuses_dialog(page)
                page.update()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Помилка додавання статусу: {ex}"), open=True)
                page.update()
        page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Додати статус"),
            content=new_status,
            actions=[ft.TextButton("Додати", on_click=save_new_status), ft.TextButton("Скасувати", on_click=lambda e: (setattr(page.dialog, 'open', False), page.update()))],
            open=True
        )
        page.overlay.append(page.dialog)
        page.update()

    def edit_status_dialog(page, status_name):
        from db import edit_status  # Must exist: edit_status(old_name, new_name)
        new_name = ft.TextField(label="Нова назва статусу", value=status_name, width=160)
        def on_save(e):
            try:
                edit_status(status_name, new_name.value)
                page.dialog.open = False
                refresh_inventory(page)
                if hasattr(page, 'inventory_container'):
                    page.inventory_container.content = ft.Column(build_inventory_list(page), expand=True)
                statuses_dialog(page)
                page.update()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Помилка редагування статусу: {ex}"), open=True)
                page.update()
        page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Редагувати статус"),
            content=new_name,
            actions=[
                ft.TextButton("Скасувати", on_click=lambda e: (setattr(page.dialog, 'open', False), page.update())),
                ft.TextButton("Зберегти", on_click=on_save),
            ],
            open=True
        )
        page.overlay.append(page.dialog)
        page.update()

    def delete_status_confirm(page, status_name):
        def on_delete(e):
            delete_status(status_name)
            page.dialog.open = False
            refresh_inventory(page)
            if hasattr(page, 'inventory_container'):
                page.inventory_container.content = ft.Column(build_inventory_list(page), expand=True)
            statuses_dialog(page)
            page.update()
        page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Видалити '{status_name}'?"),
            content=ft.Text("Видалити цей статус?"),
            actions=[
                ft.TextButton("Скасувати", on_click=lambda e: (setattr(page.dialog, 'open', False), page.update())),
                ft.TextButton("Видалити", on_click=on_delete),
            ],
            open=True
        )
        page.overlay.append(page.dialog)
        page.update()

    status_rows = [
        ft.Row([
            ft.Text(status, size=16),
            ft.IconButton(content=ft.Text("✏️"), tooltip="Редагувати", on_click=lambda e, s=status: edit_status_dialog(page, s)),
            ft.IconButton(content=ft.Text("🗑️"), tooltip="Видалити", on_click=lambda e, s=status: delete_status_confirm(page, s)),
        ]) for status in statuses
    ]
    add_btn = ft.ElevatedButton("Додати статус", icon="➕", on_click=lambda e: add_status_dialog_inner(page))
    page.dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Статуси"),
        content=ft.Column([add_btn] + status_rows, scroll=ft.ScrollMode.AUTO),
        actions=[ft.TextButton("Закрити", on_click=lambda e: (setattr(page.dialog, 'open', False), page.update()))],
        open=True
    )
    page.overlay.append(page.dialog)
    page.update()

def add_status_dialog(page):
    # For compatibility: just open statuses_dialog
    statuses_dialog(page)


# --- Основний вигляд ---
def clear_filter_and_refresh(page):
    page.inv_state['filter_field'] = None
    page.inv_state['filter_value'] = ''
    # Do not reset search query!
    refresh_inventory(page)
    # Update the filter row to hide the clear filter button
    filter_row = next((c for c in page.views[0].controls if c.key == "filter_row"), None)
    if filter_row:
        clear_btn = next((c for c in filter_row.controls if hasattr(c, 'key') and c.key == "clear_filter_btn"), None)
        if clear_btn:
            clear_btn.visible = False
    page.update()

def get_filter_row(page):
    def on_search_submit(e):
        query = e.control.value
        page.inv_state['search_query'] = query
        do_inventory_search(page, query, search_field)

    def on_search_click(e):
        query = search_field.value
        page.inv_state['search_query'] = query
        do_inventory_search(page, query, search_field)

    def on_search_change(e):
        query = e.control.value
        page.inv_state['search_query'] = query
        do_inventory_search(page, query, search_field)

    search_field = ft.TextField(
        hint_text="Пошук...",
        width=300,
        on_submit=on_search_submit,
        on_change=on_search_change,
        key="search_field",    # унікальний ключ допомагає зберегти фокус
        autofocus=True          # автоматичний фокус при перерендері
    )
    page.search_field = search_field
    search_button = ft.IconButton(
        icon="search",
        tooltip="Пошук",
        on_click=on_search_click
    )
    return ft.Row([
        search_field,
        search_button,
        ft.Container(width=16),
        ft.ElevatedButton("🔍 Фільтр", on_click=lambda e: open_filter_dialog(page)),
        ft.ElevatedButton(
            "❌ Скинути фільтр",
            visible=bool(page.inv_state.get('filter_field') and page.inv_state.get('filter_value')),
            on_click=lambda e: clear_filter_and_refresh(page),
            key="clear_filter_btn"
        ),
        ft.Container(width=16)
    ], key="filter_row")

def on_search_change(page, query, search_field=None):
    # Оновлюємо список та зберігаємо фокус на полі пошуку
    if hasattr(page, 'inventory_container'):
        do_inventory_search(page, query, search_field)
    # Оновлюємо інтерфейс
    page.update()

def do_inventory_search(page, query, search_field=None):
    from db import get_inventory
    all_items = get_inventory(
        sort_by='name',
        ascending=True,
        filters={page.inv_state['filter_field']: page.inv_state['filter_value']} if page.inv_state['filter_field'] and page.inv_state['filter_value'] else None
    )
    q = (query or '').lower().strip()
    if q:
        # Пошук у назві (1), інвентарному номері (3) та описі (11)
        search_indices = (1, 3, 11)
        filtered = [item for item in all_items if any(q in str(item[idx]).lower() for idx in search_indices if idx < len(item))]
    else:
        filtered = all_items
    page.inv_state['inventory'] = filtered
    if hasattr(page, 'inventory_container'):
        page.inventory_container.content = ft.Column(build_inventory_list(page), expand=True)
    
    # Відновити фокус на полі пошуку після оновлення
    if search_field and hasattr(search_field, 'focus'):
        search_field.focus()
    page.update()

def main_view(page: ft.Page):
    # Стан для сортування, фільтрації, списку, snackbar
    if not hasattr(page, 'inv_state'):
        page.inv_state = {
            'sort_by': 'name',
            'ascending': True,
            'filter_field': None,
            'filter_value': '',
            'inventory': [],
            'snackbar': None
        }
    # Створюємо контейнер для списку інвентаря
    # Контейнер має анімацію прозорості для плавного появлення списку
    page.inventory_container = ft.Container(
        content=ft.Column(build_inventory_list(page), expand=True),
        expand=True,
        opacity=1,
        animate_opacity=ft.Animation(500, "easeInOut"),
    )
    # Створюємо кнопку додавання
    add_button = ft.FloatingActionButton(
        text="+",
        bgcolor="#2196F3",
        on_click=lambda e: add_edit_dialog(page),
        tooltip="Додати предмет",
        autofocus=True,
        width=56,
        height=56,
    )

    # Основний layout сторінки з кнопкою додавання
    page.views.clear()
    page.views.append(
        ft.View(
            "/",
            [
                get_filter_row(page),
                ft.Container(
                    ft.Column([
                        page.inventory_container
                    ], expand=True),
                    expand=True
                ),
                # Додаємо кнопку як частину інтерфейсу
                ft.Container(
                    content=add_button,
                    alignment=ft.alignment.bottom_right,
                    padding=ft.padding.only(bottom=20, right=20),
                    expand=True
                )
            ],
            appbar=ft.AppBar(
                title=ft.Text("Інвентаризація обладнання"),
                bgcolor="#f5f5f5",
                actions=[
                    ft.Container(ft.IconButton(content=ft.Text("⬇️"), tooltip="Експорт", on_click=lambda e: export_dialog(page)), border=ft.border.all(1, "#bdbdbd"), border_radius=6, padding=2),
                    ft.Container(ft.IconButton(content=ft.Text("🕓"), tooltip="Журнал змін", on_click=lambda e: history_dialog(page)), border=ft.border.all(1, "#bdbdbd"), border_radius=6, padding=2),
                    ft.Container(ft.IconButton(content=ft.Text("📍"), tooltip="Місця зберігання", on_click=lambda e: locations_dialog(page)), border=ft.border.all(1, "#bdbdbd"), border_radius=6, padding=2),
                    ft.Container(ft.IconButton(content=ft.Text("🗂️"), tooltip="Додати категорію", on_click=lambda e: add_category_dialog(page)), border=ft.border.all(1, "#bdbdbd"), border_radius=6, padding=2),
                    ft.Container(ft.IconButton(content=ft.Text("🏷️"), tooltip="Додати статус", on_click=lambda e: add_status_dialog(page)), border=ft.border.all(1, "#bdbdbd"), border_radius=6, padding=2),
                ]
            ),
        )
    )
    
    # Зберігаємо посилання на кнопку
    page.floating_action_button = add_button
    page.update()
    refresh_inventory(page)

    # Показуємо список з fade-in
    page.inventory_container.opacity = 1
    page.inventory_container.update()
# DO NOT CALL main_view(page) anywhere else in the code except here at app startup

# --- CRUD, фільтрація, пошук ---

def on_search_button_click(page):
    query = page.search_field_ref.value if hasattr(page, 'search_field_ref') else ''
    print(f"[DEBUG] on_search_button_click called with query: {query}")
    page.inv_state['search_query'] = query
    # Оновлюємо список згідно з пошуком
    from db import get_inventory
    all_items = get_inventory(
        sort_by='name',
        ascending=True,
        filters={page.inv_state['filter_field']: page.inv_state['filter_value']} if page.inv_state['filter_field'] and page.inv_state['filter_value'] else None
    )
    q = (query or '').lower().strip()
    if q:
        # Пошук у назві (1), інвентарному номері (3) та описі (10)
        search_indices = (1, 3, 11)
        filtered = [item for item in all_items if any(q in str(item[idx]).lower() for idx in search_indices if idx < len(item))]
    else:
        filtered = all_items
    page.inv_state['inventory'] = filtered
    if hasattr(page, 'inventory_container'):
        page.inventory_container.content = ft.Column(build_inventory_list(page), expand=True)
        page.inventory_container.update()
    page.update()



def open_filter_dialog(page):
    from db import get_categories, get_statuses
    cats = get_categories()
    stats = get_statuses()
    filter_field = ft.Dropdown(
        label="Поле",
        options=[ft.dropdown.Option("name", "Назва"), ft.dropdown.Option("quantity", "Кількість"), ft.dropdown.Option("inv_number", "Інвентарний №"), ft.dropdown.Option("category", "Категорія"), ft.dropdown.Option("status", "Статус")],
        value=page.inv_state['filter_field'],
        width=220
    )
    filter_value = ft.TextField(label="Значення", value=page.inv_state['filter_value'], width=220)
    filter_category = ft.Dropdown(label="Категорія", options=[ft.dropdown.Option(c, c) for c in cats] or [ft.dropdown.Option("", "-")], value=page.inv_state['filter_value'] if page.inv_state['filter_field']=="category" else None, width=220)
    filter_status = ft.Dropdown(label="Статус", options=[ft.dropdown.Option(s, s) for s in stats], value=page.inv_state['filter_value'] if page.inv_state['filter_field']=="status" else None, width=220)
    only_with_photo = ft.Checkbox(label="Тільки з фото", value=False)

    def apply_filter(e=None):
        page.inv_state['filter_field'] = filter_field.value
        if filter_field.value == "category":
            page.inv_state['filter_value'] = filter_category.value
        elif filter_field.value == "status":
            page.inv_state['filter_value'] = filter_status.value
        else:
            page.inv_state['filter_value'] = filter_value.value
        page.dialog.open = False
        refresh_inventory(page)
        # Оновити фільтровий рядок для появи/зникнення кнопки
        if len(page.views[0].controls) > 0:
            filter_row = get_filter_row(page)
            page.views[0].controls[0] = filter_row
        page.update()

    def clear_filter(e=None):
        page.inv_state['filter_field'] = None
        page.inv_state['filter_value'] = ''
        try:
            filter_field.value = None
            filter_value.value = ''
            filter_category.value = None
            filter_status.value = None
            only_with_photo.value = False
            page.dialog.open = False
        except Exception:
            pass
        refresh_inventory(page)
        if len(page.views[0].controls) > 0:
            filter_row = get_filter_row(page)
            page.views[0].controls[0] = filter_row
        page.update()

    def clear_filter_and_refresh(page):
        page.inv_state['filter_field'] = None
        page.inv_state['filter_value'] = ''
        refresh_inventory(page)
        page.views[0].controls[2] = get_filter_row(page)
        page.update()

    def on_field_change(e):
        filter_value.visible = filter_field.value not in ["category", "status"]
        filter_category.visible = filter_field.value == "category"
        filter_status.visible = filter_field.value == "status"
        page.update()

    filter_field.on_change = on_field_change
    on_field_change(None)

    page.dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Фільтр"),
        content=ft.Column([
            filter_field,
            filter_value,
            filter_category,
            filter_status,
            only_with_photo
        ], spacing=10, tight=True),
        actions=[
            ft.TextButton("Скасувати", on_click=lambda e: (setattr(page.dialog, 'open', False), page.update())),
            ft.TextButton("Застосувати", on_click=apply_filter),
        ],
        open=True
    )
    page.overlay.append(page.dialog)
    page.update()

def build_inventory_list(page):
    import traceback
    from db import get_inventory, delete_inventory, log_history, get_locations
    # Підготуємо відповідність id -> назва місця
    locations = get_locations()
    loc_map = {loc[0]: loc[1] for loc in locations}
    # Виправлена логіка фільтрації: не застосовувати фільтр, якщо поле або значення порожнє
    filters = None
    if page.inv_state.get('filter_field') and str(page.inv_state.get('filter_value')):
        filters = {page.inv_state['filter_field']: page.inv_state['filter_value']}
    # Якщо вже відфільтровано пошуком – використовуємо готовий список
    if page.inv_state.get('search_query'):
        items = page.inv_state.get('inventory', [])
    else:
        items = get_inventory(
            sort_by=page.inv_state['sort_by'],
            ascending=page.inv_state['ascending'],
            filters=filters
        )
    q = (page.inv_state.get('search_query') or '').lower().strip()
    def hl(text: str, size: int | None = None, default_color: str | None = None):
        """Повертає ft.Text з підсвіченими фрагментами, що збігаються з q."""
        if not text:
            return ft.Text("", size=size, color=default_color)
        if not q:
            return ft.Text(str(text), size=size, color=default_color)
        lower = str(text).lower()
        if q not in lower:
            return ft.Text(str(text), size=size, color=default_color)

        spans: list[ft.TextSpan] = []
        pos = 0
        qlen = len(q)
        while True:
            idx = lower.find(q, pos)
            if idx == -1:
                spans.append(ft.TextSpan(str(text)[pos:], style=ft.TextStyle(color=default_color)))
                break
            # Частина перед збігом
            if idx > pos:
                spans.append(ft.TextSpan(str(text)[pos:idx], style=ft.TextStyle(color=default_color)))
            # Збіг
            spans.append(ft.TextSpan(
                str(text)[idx:idx+qlen],
                style=ft.TextStyle(weight=ft.FontWeight.BOLD, bgcolor="#fff59d", color=default_color)
            ))
            pos = idx + qlen
        return ft.Text(spans=spans, size=size)
    rows = []
    for idx, item in enumerate(items):
        try:
            if len(item) < 12:
                continue
            location_name = loc_map.get(item[6], "—") if item[6] else "—"
            image_cell = ft.Container(
                ft.Image(src=item[8], width=40, height=40, fit=ft.ImageFit.COVER),
                on_click=lambda e, p=item[8]: show_full_image(page, p)
            ) if item[8] else ft.Text("🖼️")
            action_cell = ft.Row([
                ft.IconButton(icon="edit", tooltip="Редагувати", on_click=lambda e, i=item: add_edit_dialog(page, i)),
                ft.IconButton(icon="delete", tooltip="Видалити", on_click=lambda e, i=item: delete_dialog(page, i))
            ])
            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Container(image_cell, alignment=ft.alignment.center)),  # 40x40 image, centered
                    ft.DataCell(ft.Container(hl(item[1], 14), expand=True, padding=ft.padding.symmetric(vertical=10))),
                    ft.DataCell(ft.Container(ft.Text(str(item[2])), alignment=ft.alignment.center, padding=ft.padding.symmetric(vertical=10))),
                    ft.DataCell(ft.Container(hl(item[3], 14), padding=ft.padding.symmetric(vertical=10))),
                    ft.DataCell(ft.Container(ft.Text(item[4] or "—"), padding=ft.padding.symmetric(vertical=10))),
                    ft.DataCell(ft.Container(ft.Text(item[7] or "—"), padding=ft.padding.symmetric(vertical=10))),
                    ft.DataCell(ft.Container(ft.Text(location_name), padding=ft.padding.symmetric(vertical=10))),
                    ft.DataCell(ft.Container(ft.Text(item[5]), padding=ft.padding.symmetric(vertical=10))),
                    ft.DataCell(ft.Container(action_cell, padding=ft.padding.symmetric(vertical=10)))
                ],
                # Modern look: subtle shadow and rounded corners for each row
                # (if supported by your Flet version)
                # If not supported, this is safe to ignore
                # shadow_color="#e3e3e3",
                # border_radius=8
            )
            rows.append(row)
        except Exception:
            pass

    # Визначаємо пропорції ширини колонок (сума = 1.0)
    col_weights = {
        "photo": 0.15,
        "name": 0.25, 
        "quantity": 0.1,
        "number": 0.15,
        "category": 0.15,
        "status": 0.1,
        "location": 0.15,
        "date": 0.1,
        "actions": 0.15
    }
    
    table = ft.DataTable(
        width=1250,
        data_row_min_height=48,  # Default row height for compact table
        heading_row_height=60,  # Slightly increased heading row height for balance,
        columns=[
            ft.DataColumn(ft.Text("Фото")),
            ft.DataColumn(ft.Text("Назва")),
            ft.DataColumn(ft.Text("К-сть")),
            ft.DataColumn(ft.Text("№")),
            ft.DataColumn(ft.Text("Категорія")),
            ft.DataColumn(ft.Text("Статус")),
            ft.DataColumn(ft.Text("Місце")),
            ft.DataColumn(ft.Text("Додано")),
            ft.DataColumn(ft.Text("Дії")),
        ],
        rows=rows,
        column_spacing=20,
        heading_row_color="#e0e0e0",
        data_row_color={"even": "#fafafa"},
        horizontal_margin=10,
        expand=True
    )

    # Адаптивний контейнер
    return [table]

def add_edit_dialog(page, item=None):
    import tempfile
    import traceback
    from db import add_inventory, edit_inventory, get_locations, get_categories, get_statuses, get_custom_fields, log_history, inventory_inv_number_exists
    from datetime import datetime

    try:
        locations = get_locations()
        categories = get_categories()
        statuses = get_statuses()
        custom_fields = get_custom_fields()

        is_edit = item is not None
        title = "Редагування елемента" if is_edit else "Додавання елемента"

        # Fallback для item
        item = item or [None]*12
        # Поля для форми
        name = ft.TextField(label="Назва", value=item[1] if len(item)>1 and item[1] else "", width=300)
        quantity = ft.TextField(label="Кількість", value=str(item[2]) if len(item)>2 and item[2] else "1", width=100, keyboard_type=ft.KeyboardType.NUMBER)
        inv_number = ft.TextField(label="Інвентарний номер", value=item[3] if len(item)>3 and item[3] else "", width=200)
        category = ft.Dropdown(label="Категорія", options=[ft.dropdown.Option(c, c) for c in categories] or [ft.dropdown.Option("", "-")], value=item[4] if len(item)>4 and item[4] in categories else None, width=200)
        added_at = ft.TextField(label="Дата додавання", value=item[5] if len(item)>5 and item[5] else datetime.now().strftime("%Y-%m-%d"), width=150)
        location = ft.Dropdown(label="Місце зберігання", options=[ft.dropdown.Option(str(l[0]), l[1]) for l in locations] or [ft.dropdown.Option("", "-")], value=str(item[6]) if len(item)>6 and item[6] else None, width=200)
        status = ft.Dropdown(label="Статус", options=[ft.dropdown.Option(s, s) for s in statuses] or [ft.dropdown.Option("", "-")], value=item[7] if len(item)>7 and item[7] in statuses else None, width=200)
        image_path = ft.Text(value=item[8] if len(item)>8 and item[8] else "", visible=False)
        image_preview = ft.Image(src=item[8], width=64, height=64) if is_edit and len(item)>8 and item[8] else ft.Text("🖼️")
        comments = ft.TextField(label="Коментарі", value=item[11] if is_edit else "", multiline=True, max_lines=3, width=500)

        # Користувацькі поля (JSON у БД)
        import json
        try:
            custom_vals = json.loads(item[9]) if is_edit and len(item)>9 and item[9] else {}
        except Exception:
            custom_vals = {}
        custom_inputs = []
        for f in custom_fields:
            field_id, field_name, field_type = f
            val = custom_vals.get(field_name, "")
            if field_type == 'text':
                inp = ft.TextField(label=field_name, value=val, width=200)
            elif field_type == 'number':
                inp = ft.TextField(label=field_name, value=str(val), width=120, keyboard_type=ft.KeyboardType.NUMBER)
            elif field_type == 'date':
                inp = ft.TextField(label=field_name, value=val, width=150)
            else:
                inp = ft.TextField(label=field_name, value=val, width=200)
            custom_inputs.append((field_name, inp))
    except Exception as ex:
        tb = traceback.format_exc()
        page.snack_bar = ft.SnackBar(ft.Text(f"Помилка у формі: {ex}\n{tb}"), open=True)
        page.update()
        return

    # Константи для валідації зображень
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png'}
    
    # Завантаження зображення
    def on_upload(e):
        if not e.files:
            return
            
        file = e.files[0]
        file_path = file.path
        
        # Валідація розширення файлу
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            page.snack_bar = ft.SnackBar(
                ft.Text("Дозволені лише зображення у форматі JPG, JPEG або PNG"), 
                open=True
            )
            page.update()
            return
            
        # Валідація розміру файлу
        try:
            file_size = os.path.getsize(file_path)
            if file_size > MAX_IMAGE_SIZE:
                page.snack_bar = ft.SnackBar(
                    ft.Text(f"Розмір зображення перевищує {MAX_IMAGE_SIZE/1024/1024}МБ"), 
                    open=True
                )
                page.update()
                return
        except Exception as ex:
            print(f"Помилка перевірки розміру файлу: {ex}")
        
        # Оновлюємо UI
        image_path.value = file_path
        image_preview.src = file_path
        image_preview.update()
        
        # Показуємо повідомлення про успішне завантаження
        page.snack_bar = ft.SnackBar(
            ft.Text("Зображення успішно завантажено"),
            open=True
        )
        page.update()

    upload = ft.FilePicker(on_result=on_upload)
    if upload not in page.overlay:
        page.overlay.append(upload)
    upload_btn = ft.ElevatedButton("Завантажити зображення", on_click=lambda e: upload.pick_files(allow_multiple=False, allowed_extensions=["jpg","jpeg","png"]))

    # Збереження
    def on_save(e):
        try:
            print("[DEBUG] on_save start")
            # Validate inputs
            if not name.value.strip():
                page.snack_bar = ft.SnackBar(ft.Text("Вкажіть назву предмета!"), open=True)
                page.update()
                return
            # Safe quantity conversion
            try:
                qty_val = int(quantity.value.strip() or "0")
                print(f"[DEBUG] qty_val = {qty_val}")
            except ValueError:
                page.snack_bar = ft.SnackBar(ft.Text("Кількість повинна бути невідʼємним цілим числом"), open=True)
                page.update()
                return
            # Duplicate inventory number check is done later, but ensure provided number trimmed
            inv_num_trim = (inv_number.value or "").strip()
            # Перевірка дубліката інвентарного номера ДО будь-яких операцій з файлом
            if inv_num_trim:
                if inventory_inv_number_exists(inv_num_trim, item[0] if is_edit else None):
                    if not hasattr(page, 'snack_bar') or page.snack_bar is None:
                        page.snack_bar = ft.SnackBar(content=ft.Text("Такий інвентарний номер вже існує!"), open=True)
                    else:
                        page.snack_bar.content = ft.Text("Такий інвентарний номер вже існує!")
                        page.snack_bar.open = True
                    page.update()
                    return
            # Підготовка фото (копіюємо у IMAGES_DIR за потреби)
            final_image_path = image_path.value
            if final_image_path:
                try:
                    # Видаляємо старе зображення, якщо воно існує та відрізняється від нового
                    if is_edit and item[8] and item[8] != final_image_path and os.path.isfile(item[8]):
                        try:
                            os.remove(item[8])
                            print(f"[INFO] Видалено старе зображення: {item[8]}")
                        except Exception as del_ex:
                            print(f"[WARN] Не вдалося видалити старе зображення {item[8]}: {del_ex}")
                    
                    # Перевіряємо, чи файл вже в папці IMAGES_DIR
                    if not os.path.commonpath([os.path.abspath(final_image_path), os.path.abspath(IMAGES_DIR)]) == os.path.abspath(IMAGES_DIR):
                        _, ext = os.path.splitext(final_image_path)
                        safe_inv = inv_num_trim or str(int(datetime.now().timestamp()))
                        new_filename = f"{safe_inv}_{int(datetime.now().timestamp())}{ext}"
                        dest_path = os.path.join(IMAGES_DIR, new_filename)
                        
                        # Копіюємо файл
                        shutil.copy2(final_image_path, dest_path)
                        print(f"[INFO] Скопійовано зображення до {dest_path}")
                        
                        # Оновлюємо шлях до нового зображення
                        final_image_path = dest_path
                        
                        # Не видаляємо файл, якщо він знаходиться в IMAGES_DIR або це новий файл
                        # Файл буде видалений при наступному оновленні або видаленні запису
                        if os.path.dirname(final_image_path) != os.path.abspath(IMAGES_DIR):
                            # Замість видалення, просто логуємо
                            print(f"[INFO] Тимчасовий файл залишено: {final_image_path}")
                except Exception as copy_ex:
                    print(f"[ERROR] Помилка при обробці зображення: {copy_ex}")
                    page.snack_bar = ft.SnackBar(
                        ft.Text(f"Помилка при обробці зображення: {str(copy_ex)}"),
                        open=True
                    )
                    page.update()
                    return
            print(f"[DEBUG] final_image_path = {final_image_path}")
            data = {
                'name': name.value.strip(),
                'quantity': qty_val,
                'inv_number': inv_num_trim,
                'category': category.value,
                'added_at': added_at.value,
                'location_id': int(location.value) if location.value else None,
                'status': status.value,
                'image_path': final_image_path,
                'description': '',  # not used
                'comments': comments.value,
                'custom_fields': json.dumps({k: inp.value for k, inp in custom_inputs}),
            }
            if is_edit:
                print(f"[DEBUG] calling edit_inventory id={item[0]}")
                edit_inventory(item[0], data)
                log_history(item[0], "edit", f"Змінено: {data['name']}")
            else:
                print("[DEBUG] calling add_inventory")
                add_inventory(data)
                log_history(None, "add", f"Додано: {data['name']}")
            page.dialog.open = False
            refresh_inventory(page)
            page.snack_bar = ft.SnackBar(ft.Text("Елемент збережено!"), open=True)
            page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Помилка збереження: {ex}"), open=True)
            page.update()

    # item fallback для нових предметів
    if item is None or len(item) < 12:
        item = list(item) if item else [None]*12
        while len(item) < 12:
            item.append(None)
    # Діалог
    page.dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(title),
        content=ft.Column([
            name, quantity, inv_number, category, added_at, location, status,
            ft.Row([image_preview, upload_btn]),
            comments,
            *[inp for _, inp in custom_inputs],
        ], width=650, scroll=ft.ScrollMode.AUTO),
        actions=[
            ft.TextButton("Скасувати", on_click=lambda e: (setattr(page.dialog, 'open', False), page.update())),
            ft.TextButton("Зберегти", on_click=on_save),
        ],
        open=True
    )
    page.overlay.append(page.dialog)
    page.update()

def delete_dialog(page, item):
    from db import delete_inventory, log_history
    delete_inventory(item[0])
    log_history(item[0], "delete", f"Видалено: {item[1]}")
    refresh_inventory(page)
    page.snack_bar = ft.SnackBar(ft.Text("Елемент видалено!"), open=True)
    page.update()

def export_dialog(page):
    from db import export_inventory_to_pdf, get_locations
    import time
    locs = get_locations()
    dd_loc = ft.Dropdown(
        label="Місце зберігання",
        options=[ft.dropdown.Option("all", "Всі")] + [ft.dropdown.Option(str(l[0]), l[1]) for l in locs],
        value="all",
        width=250
    )
    def do_export(e):
        try:
            ts = int(time.time())
            filename = f"inventory_{ts}.pdf"
            loc_id = None if dd_loc.value == "all" else int(dd_loc.value)
            export_inventory_to_pdf(filename, loc_id)
            page.snack_bar = ft.SnackBar(ft.Text(f"Експортовано у {filename}"), open=True)
            page.dialog.open = False
            page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Помилка експорту: {ex}"), open=True)
            page.update()
    page.dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Експорт у PDF"),
        content=dd_loc,
        actions=[
            ft.TextButton("Скасувати", on_click=lambda e: (setattr(page.dialog, 'open', False), page.update())),
            ft.TextButton("Експорт", on_click=do_export)
        ],
        open=True
    )
    page.overlay.append(page.dialog)
    page.update()

def history_dialog(page):
    from db import get_history
    import datetime
    records = get_history()

    # Фільтри
    filter_action = ft.Dropdown(label="Тип дії", options=[ft.dropdown.Option("Всі", "Всі")] + [ft.dropdown.Option(a, a) for a in sorted(set(r[2] for r in records))], value="Всі", width=120)
    filter_inv = ft.TextField(label="Інвентарний номер", width=150)
    filter_date = ft.TextField(label="Дата (YYYY-MM-DD)", width=120)

    def apply_filters():
        filtered = records
        if filter_action.value and filter_action.value != "Всі":
            filtered = [r for r in filtered if r[2] == filter_action.value]
        if filter_inv.value:
            filtered = [r for r in filtered if filter_inv.value.lower() in (r[1] and str(r[1]).lower()) or filter_inv.value.lower() in (r[4] and str(r[4]).lower())]
        if filter_date.value:
            filtered = [r for r in filtered if r[3].startswith(filter_date.value)]
        return filtered

    def update_table(e=None):
        filtered = apply_filters()
        history_list.controls = [
            ft.Container(
                ft.Row([
                    ft.Text(str(r[0]), width=40, size=12, color="#888"),
                    ft.Text(str(r[1]), width=80, size=12),
                    ft.Text(r[2], width=60, size=12, color="#2b5" if r[2]=='add' else ("#b52" if r[2]=='delete' else "#258")),
                    ft.Text(r[3][:19], width=120, size=12, color="#888"),
                    ft.Text(r[4], size=12),
                ], spacing=8),
                bgcolor="#f7f7f7" if i%2==0 else None,
                padding=6,
                border_radius=6
            ) for i, r in enumerate(filtered)
        ]
        history_list.update()
        count_text.value = f"Всього записів: {len(filtered)}"
        count_text.update()

    # Список для журналу змін з прокручуванням
    history_list = ft.ListView(
        controls=[],
        expand=True,
        spacing=6,
        auto_scroll=False
    )
    count_text = ft.Text("")

    def update_table(e=None):
        filtered = apply_filters()
        history_list.controls = [
            ft.Container(
                ft.Row([
                    ft.Text(str(r[0]), width=40, size=12, color="#888"),
                    ft.Text(str(r[1]), width=80, size=12),
                    ft.Text(r[2], width=60, size=12, color="#2b5" if r[2]=='add' else ("#b52" if r[2]=='delete' else "#258")),
                    ft.Text(r[3][:19], width=120, size=12, color="#888"),
                    ft.Text(r[4], size=12),
                ], spacing=8),
                bgcolor="#f7f7f7" if i%2==0 else None,
                padding=6,
                border_radius=6
            ) for i, r in enumerate(filtered)
        ]
        history_list.update()
        count_text.value = f"Всього записів: {len(filtered)}"
        count_text.update()


    # Діалог
    page.dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Журнал змін інвентаря"),
        content=ft.Container(
            ft.Column([
                ft.Row([filter_action, filter_inv, filter_date, ft.ElevatedButton("Фільтрувати", on_click=update_table)]),
                count_text,
                ft.Container(history_list, expand=True),
            ], scroll=ft.ScrollMode.AUTO),
            width=800
        ),
        actions=[ft.TextButton("Закрити", on_click=lambda e: (setattr(page.dialog, 'open', False), page.update()))],
        open=True
    )
    page.overlay.append(page.dialog)
    page.update()
    update_table()


def locations_dialog(page):
    from db import get_locations, add_location, edit_location, delete_location
    locations = get_locations()

    # Побудова дерева місць
    def build_tree(locations, parent_id=None):
        nodes = []
        for loc in filter(lambda l: l[2] == parent_id, locations):
            children = build_tree(locations, loc[0])
            nodes.append(
                ft.Row([
                    ft.Text(loc[1], size=16),
                    ft.IconButton(content=ft.Text("✏️"), tooltip="Редагувати", on_click=lambda e, l=loc: edit_location_dialog(page, l)),
                    ft.IconButton(content=ft.Text("🗑️"), tooltip="Видалити", on_click=lambda e, l=loc: delete_location_confirm(page, l)),
                ] + ([ft.Column(children)] if children else []))
            )
        return nodes

    def add_location_dialog(page, parent_id=None):
        name = ft.TextField(label="Назва місця", width=200)
        def on_save(e):
            try:
                add_location(name.value, parent_id)
                page.dialog.open = False
                page.update()
                locations_dialog(page)
                # Оновити всі випадаючі списки місць у діалогах
                if hasattr(page, 'inventory_container'):
                    page.inventory_container.content = ft.Column(build_inventory_list(page), expand=True)
                page.update()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Помилка додавання місця: {ex}"), open=True)
                page.update()
        page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Додати місце зберігання"),
            content=name,
            actions=[
                ft.TextButton("Скасувати", on_click=lambda e: (setattr(page.dialog, 'open', False), page.update())),
                ft.TextButton("Додати", on_click=on_save),
            ],
            open=True
        )
        page.overlay.append(page.dialog)
        page.update()

    def edit_location_dialog(page, loc):
        name = ft.TextField(label="Назва місця", value=loc[1], width=200)
        parent = ft.Dropdown(label="Батьківське місце", options=[ft.dropdown.Option(str(l[0]), l[1]) for l in locations if l[0] != loc[0]], value=str(loc[2]) if loc[2] else None, width=200)
        def on_save(e):
            try:
                edit_location(loc[0], name.value, int(parent.value) if parent.value else None)
                page.dialog.open = False
                page.update()
                locations_dialog(page)
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Помилка редагування місця: {ex}"), open=True)
                page.update()
        page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Редагувати місце зберігання"),
            content=ft.Column([name, parent]),
            actions=[
                ft.TextButton("Скасувати", on_click=lambda e: (setattr(page.dialog, 'open', False), page.update())),
                ft.TextButton("Зберегти", on_click=on_save),
            ],
            open=True
        )
        page.overlay.append(page.dialog)
        page.update()

    def delete_location_confirm(page, loc):
        def on_delete(e):
            delete_location(loc[0])
            page.dialog.open = False
            page.update()
            locations_dialog(page)
        page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Видалити '{loc[1]}'?"),
            content=ft.Text("Видалити це місце та всі підмісця?"),
            actions=[
                ft.TextButton("Скасувати", on_click=lambda e: (setattr(page.dialog, 'open', False), page.update())),
                ft.TextButton("Видалити", on_click=on_delete),
            ],
            open=True
        )
        page.overlay.append(page.dialog)
        page.update()

    # Основний діалог з деревом
    tree = build_tree(locations)
    add_btn = ft.ElevatedButton("Додати кореневе місце", icon="➕", on_click=lambda e: add_location_dialog(page, None))
    page.dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Місця зберігання (ієрархія)"),
        content=ft.Column([add_btn] + tree, scroll=ft.ScrollMode.AUTO),
        actions=[ft.TextButton("Закрити", on_click=lambda e: (setattr(page.dialog, 'open', False), page.update()))],
        open=True
    )
    page.overlay.append(page.dialog)
    page.update()

def refresh_inventory(page):
    from db import get_inventory
    page.inv_state['inventory'] = get_inventory(
        sort_by=page.inv_state['sort_by'],
        ascending=page.inv_state['ascending'],
        filters={page.inv_state['filter_field']: page.inv_state['filter_value']} if page.inv_state['filter_field'] and page.inv_state['filter_value'] else None
    )
    # спочатку зробимо fade-out
    page.inventory_container.opacity = 0
    page.inventory_container.update()
    # оновлюємо контент
    page.inventory_container.content = ft.Column(build_inventory_list(page), expand=True)
    # fade-in
    page.inventory_container.opacity = 1
    page.inventory_container.update()
    page.update()

def set_sort_field(page, field):
    page.inv_state['sort_by'] = field
    refresh_inventory(page)

def set_sort_order(page, ascending):
    page.inv_state['ascending'] = ascending
    refresh_inventory(page)

def set_filter_field(page, field):
    page.inv_state['filter_field'] = field
    refresh_inventory(page)

def set_filter_value(page, value):
    page.inv_state['filter_value'] = value
    refresh_inventory(page)

def clear_filters(page):
    page.inv_state['filter_field'] = None
    page.inv_state['filter_value'] = ''
    refresh_inventory(page)

# --- Допоміжний діалог для повного зображення ---
def show_full_image(page, img_path: str):
    """Відкриває зображення у великому розмірі в діалозі."""
    if not img_path:
        return
    page.dialog = ft.AlertDialog(
        modal=True,
        content=ft.Image(src=img_path, width=800, fit=ft.ImageFit.CONTAIN),
        actions=[ft.TextButton("Закрити", on_click=lambda e: (setattr(page.dialog, 'open', False), page.update()))],
        open=True
    )
    page.overlay.append(page.dialog)
    page.update()
