import tkinter as tk
from tkinter import messagebox
from datetime import datetime, date
from typing import Any, Dict, List
from .logger import logger

class Utils:
    """Funciones utilitarias para la aplicación"""
    
    @staticmethod
    def format_currency(amount: float) -> str:
        """Formatear número como moneda chilena"""
        try:
            return f"${amount:,.0f}".replace(",", ".")
        except (ValueError, TypeError):
            return "$0"
    
    @staticmethod
    def format_rut(rut: str) -> str:
        """Formatear RUT chileno"""
        try:
            rut = rut.upper().replace(".", "").replace("-", "").strip()
            if not rut:
                return ""
            
            cuerpo = rut[:-1]
            dv = rut[-1]
            
            # Formatear con puntos y guión
            rut_formateado = ""
            for i, char in enumerate(reversed(cuerpo)):
                if i > 0 and i % 3 == 0:
                    rut_formateado = "." + rut_formateado
                rut_formateado = char + rut_formateado
            
            return f"{rut_formateado}-{dv}"
        except Exception:
            return rut
    
    @staticmethod
    def parse_date(date_str: str) -> date:
        """Parsear fecha desde string"""
        try:
            if isinstance(date_str, date):
                return date_str
            formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue
            raise ValueError(f"Formato de fecha no reconocido: {date_str}")
        except Exception as e:
            logger.error(f"Error parseando fecha: {e}")
            raise
    
    @staticmethod
    def format_date(date_obj: date) -> str:
        """Formatear fecha como string"""
        try:
            if isinstance(date_obj, str):
                return date_obj
            return date_obj.strftime('%d/%m/%Y')
        except Exception:
            return ""
    
    @staticmethod
    def show_message(parent, title: str, message: str, type: str = "info"):
        """Mostrar mensaje al usuario"""
        if type == "info":
            messagebox.showinfo(title, message, parent=parent)
        elif type == "warning":
            messagebox.showwarning(title, message, parent=parent)
        elif type == "error":
            messagebox.showerror(title, message, parent=parent)
        elif type == "question":
            return messagebox.askyesno(title, message, parent=parent)
        return None
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validar formato de email"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def calculate_age(birth_date: date) -> int:
        """Calcular edad desde fecha de nacimiento"""
        today = date.today()
        return today.year - birth_date.year - (
            (today.month, today.day) < (birth_date.month, birth_date.day)
        )
    
    @staticmethod
    def center_window(window, width: int = None, height: int = None):
        """Centrar ventana en la pantalla"""
        window.update_idletasks()
        if width and height:
            window.geometry(f"{width}x{height}")
        
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

# Instancia global
utils = Utils()