import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any, Optional
from core.utils import utils

class CustomTable(ttk.Frame):
    """Tabla personalizada con funcionalidades avanzadas"""
    
    def __init__(self, parent, columns: List[Dict], height: int = 15, 
                 show_toolbar: bool = True, **kwargs):
        super().__init__(parent)
        self.parent = parent
        self.columns = columns
        self.height = height
        self.show_toolbar = show_toolbar
        self.data = []
        
        self._create_style()
        self._setup_table()
        
    def _create_style(self):
        """Crear estilos para la tabla"""
        style = ttk.Style()
        style.configure("Table.Treeview", 
                       rowheight=25,
                       font=("Arial", 10))
        style.configure("Table.Treeview.Heading",
                       font=("Arial", 10, "bold"),
                       background="#34495e",
                       foreground="white")
        style.map("Table.Treeview.Heading",
                 background=[('active', '#2c3e50')])
        
    def _setup_table(self):
        """Configurar la tabla con sus componentes"""
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True)
        
        # Toolbar (opcional)
        if self.show_toolbar:
            self._create_toolbar(main_frame)
        
        # Frame para tabla y scrollbars
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill="both", expand=True, pady=(5, 0))
        
        # Configurar grid para tabla y scrollbars
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Scrollbar vertical
        self.v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical")
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Scrollbar horizontal
        self.h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Treeview (tabla)
        self.tree = ttk.Treeview(
            table_frame,
            columns=[col['id'] for col in self.columns],
            show="headings",
            height=self.height,
            style="Table.Treeview",
            yscrollcommand=self.v_scrollbar.set,
            xscrollcommand=self.h_scrollbar.set
        )
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        # Configurar scrollbars
        self.v_scrollbar.config(command=self.tree.yview)
        self.h_scrollbar.config(command=self.tree.xview)
        
        # Configurar columnas
        self._configure_columns()
        
        # Bind eventos
        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Button-3>", self._on_right_click)
        
    def _create_toolbar(self, parent):
        """Crear barra de herramientas de la tabla"""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill="x", pady=(0, 5))
        
        # Botones de la toolbar
        ttk.Button(
            toolbar,
            text="🔄 Actualizar",
            command=self.refresh,
            style="Secondary.TButton"
        ).pack(side="left", padx=2)
        
        ttk.Button(
            toolbar,
            text="📋 Exportar",
            command=self.export_data,
            style="Secondary.TButton"
        ).pack(side="left", padx=2)
        
        ttk.Button(
            toolbar,
            text="🔍 Buscar",
            command=self.show_search,
            style="Secondary.TButton"
        ).pack(side="left", padx=2)
        
        # Campo de búsqueda
        search_frame = ttk.Frame(toolbar)
        search_frame.pack(side="right", padx=2)
        
        ttk.Label(search_frame, text="Buscar:").pack(side="left", padx=2)
        
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=20
        )
        self.search_entry.pack(side="left", padx=2)
        self.search_entry.bind("<KeyRelease>", self._on_search)
        
        ttk.Button(
            search_frame,
            text="❌",
            command=self.clear_search,
            width=3
        ).pack(side="left", padx=2)
        
    def _configure_columns(self):
        """Configurar las columnas de la tabla"""
        for col in self.columns:
            self.tree.heading(col['id'], text=col['text'])
            
            # Configurar ancho de columna
            width = col.get('width', 100)
            minwidth = col.get('minwidth', 50)
            anchor = col.get('anchor', 'w')
            
            self.tree.column(col['id'], width=width, minwidth=minwidth, anchor=anchor)
            
    def load_data(self, data: List[Dict]):
        """Cargar datos en la tabla"""
        self.data = data
        self._refresh_table()
        
    def _refresh_table(self):
        """Refrescar la tabla con los datos actuales"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Insertar datos
        for row in self.data:
            values = [row.get(col['id'], '') for col in self.columns]
            
            # Formatear valores si hay formateadores
            for i, col in enumerate(self.columns):
                if 'formatter' in col and values[i]:
                    try:
                        values[i] = col['formatter'](values[i])
                    except Exception:
                        pass
            
            self.tree.insert("", "end", values=values, tags=(row.get('_tags', ''),))
            
        # Aplicar tags si existen
        self._apply_tags()
        
    def _apply_tags(self):
        """Aplicar estilos a las filas basados en tags"""
        # Configurar tags para filas
        self.tree.tag_configure('even', background='#f8f9fa')
        self.tree.tag_configure('odd', background='white')
        self.tree.tag_configure('warning', background='#fff3cd')
        self.tree.tag_configure('danger', background='#f8d7da')
        self.tree.tag_configure('success', background='#d1edff')
        
        # Aplicar tags alternados
        for i, item in enumerate(self.tree.get_children()):
            tag = 'even' if i % 2 == 0 else 'odd'
            current_tags = list(self.tree.item(item, 'tags'))
            if tag not in current_tags:
                current_tags.append(tag)
                self.tree.item(item, tags=current_tags)
                
    def get_selected_item(self):
        """Obtener item seleccionado"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item, 'values')
            
            # Convertir a diccionario
            selected_data = {}
            for i, col in enumerate(self.columns):
                selected_data[col['id']] = values[i] if i < len(values) else ''
                
            return selected_data
        return None
        
    def get_selected_items(self):
        """Obtener todos los items seleccionados"""
        selections = self.tree.selection()
        selected_data = []
        
        for item in selections:
            values = self.tree.item(item, 'values')
            
            # Convertir a diccionario
            data = {}
            for i, col in enumerate(self.columns):
                data[col['id']] = values[i] if i < len(values) else ''
                
            selected_data.append(data)
            
        return selected_data
        
    def clear_selection(self):
        """Limpiar selección"""
        for item in self.tree.selection():
            self.tree.selection_remove(item)
            
    def refresh(self):
        """Refrescar tabla"""
        self._refresh_table()
        
    def export_data(self):
        """Exportar datos a CSV"""
        try:
            import csv
            from tkinter import filedialog
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    
                    # Escribir encabezados
                    headers = [col['text'] for col in self.columns]
                    writer.writerow(headers)
                    
                    # Escribir datos
                    for row in self.data:
                        values = [row.get(col['id'], '') for col in self.columns]
                        writer.writerow(values)
                        
                utils.show_message(self.parent, "Éxito", f"Datos exportados a {filename}", "info")
                
        except Exception as e:
            utils.show_message(self.parent, "Error", f"Error al exportar: {str(e)}", "error")
            
    def show_search(self):
        """Mostrar diálogo de búsqueda avanzada"""
        self.search_entry.focus()
        
    def _on_search(self, event=None):
        """Manejar búsqueda en tiempo real"""
        search_term = self.search_var.get().lower()
        
        if not search_term:
            self._refresh_table()
            return
            
        filtered_data = []
        for row in self.data:
            # Buscar en todos los valores de la fila
            for value in row.values():
                if search_term in str(value).lower():
                    filtered_data.append(row)
                    break
                    
        # Mostrar datos filtrados
        self._show_filtered_data(filtered_data)
        
    def _show_filtered_data(self, filtered_data):
        """Mostrar datos filtrados"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Insertar datos filtrados
        for row in filtered_data:
            values = [row.get(col['id'], '') for col in self.columns]
            self.tree.insert("", "end", values=values)
            
    def clear_search(self):
        """Limpiar búsqueda"""
        self.search_var.set("")
        self._refresh_table()
        
    def _on_double_click(self, event):
        """Manejar doble click"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            if hasattr(self, 'on_double_click'):
                self.on_double_click(self.get_selected_item())
                
    def _on_right_click(self, event):
        """Manejar click derecho (context menu)"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            if hasattr(self, 'on_right_click'):
                self.on_right_click(event, self.get_selected_item())
                
    def add_context_menu(self, menu_items: List[Dict]):
        """Agregar menú contextual"""
        self.context_menu = tk.Menu(self, tearoff=0)
        
        for item in menu_items:
            if item.get('separator'):
                self.context_menu.add_separator()
            else:
                self.context_menu.add_command(
                    label=item['label'],
                    command=item['command']
                )
                
        # Bind menú contextual
        self.tree.bind("<Button-3>", self._show_context_menu)
        
    def _show_context_menu(self, event):
        """Mostrar menú contextual"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            try:
                self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.context_menu.grab_release()
                
    def set_column_visibility(self, column_id: str, visible: bool):
        """Mostrar/ocultar columna"""
        if visible:
            self.tree.heading(column_id, text=next(col['text'] for col in self.columns if col['id'] == column_id))
        else:
            self.tree.heading(column_id, text="")
            
    def sort_by_column(self, column_id: str, reverse: bool = False):
        """Ordenar por columna"""
        col_index = next(i for i, col in enumerate(self.columns) if col['id'] == column_id)
        
        def sort_key(row):
            value = row.get(column_id, '')
            try:
                return float(value) if value else 0
            except (ValueError, TypeError):
                return str(value).lower()
                
        self.data.sort(key=sort_key, reverse=reverse)
        self._refresh_table()