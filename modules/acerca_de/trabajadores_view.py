import tkinter as tk
from tkinter import ttk
from datetime import datetime
from app.base_view import BaseView
from services.trabajador_service import TrabajadorService
from core.auth import AuthService
from models.usuario import Usuario
from core.exceptions import DatabaseError, ValidationError
from core.logger import logger
from core.utils import utils
from ui.components.table import CustomTable
from ui.components.modal import InputModal

class TrabajadoresView(BaseView):
    """Vista de gestión de trabajadores"""
    
    def _setup_view(self):
        """Configurar vista de trabajadores"""
        # Título
        self.create_title("👥 Gestión de Trabajadores", 0, 0, columnspan=2)
        
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        
        # Configurar grid principal
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Toolbar
        self._create_toolbar(main_frame)
        
        # Tabla de trabajadores
        self._create_trabajadores_table(main_frame)
        
        # Cargar datos
        self._load_trabajadores()
    
    def _create_toolbar(self, parent):
        """Crear barra de herramientas"""
        toolbar = ttk.Frame(parent)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # Botones principales
        # Crear botones y mantener referencias para habilitar/deshabilitar según rol
        self._btn_nuevo = ttk.Button(
            toolbar,
            text="➕ Nuevo Trabajador",
            command=self._nuevo_trabajador,
            style="Primary.TButton"
        )
        self._btn_nuevo.pack(side="left", padx=2)
        
        self._btn_editar = ttk.Button(
            toolbar,
            text="✏️ Editar",
            command=self._editar_trabajador,
            style="Secondary.TButton"
        )
        self._btn_editar.pack(side="left", padx=2)
        
        self._btn_ver = ttk.Button(
            toolbar,
            text="👁️ Ver Detalles",
            command=self._ver_detalles,
            style="Secondary.TButton"
        )
        self._btn_ver.pack(side="left", padx=2)
        
        self._btn_desactivar = ttk.Button(
            toolbar,
            text="🗑️ Desactivar",
            command=self._desactivar_trabajador,
            style="Danger.TButton"
        )
        self._btn_desactivar.pack(side="left", padx=2)

        # Si el usuario actual no es admin, deshabilitar las acciones de administración
        try:
            current = AuthService.get_current_user()
            if not current or current.rol != 'admin':
                self._btn_nuevo.config(state='disabled')
                self._btn_editar.config(state='disabled')
                self._btn_desactivar.config(state='disabled')
        except Exception:
            pass
        
        # Búsqueda
        search_frame = ttk.Frame(toolbar)
        search_frame.pack(side="right", padx=2)
        
        ttk.Label(search_frame, text="Buscar:").pack(side="left", padx=2)
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=20
        )
        search_entry.pack(side="left", padx=2)
        search_entry.bind("<KeyRelease>", self._buscar_trabajadores)
        
        ttk.Button(
            search_frame,
            text="❌",
            command=self._limpiar_busqueda,
            width=3
        ).pack(side="left", padx=2)

        # Botón para crear cuenta de usuario asociada a trabajador (solo admin)
        try:
            if AuthService.get_current_user() and AuthService.get_current_user().rol == 'admin':
                ttk.Button(
                    toolbar,
                    text="🔑 Crear Cuenta",
                    command=self._crear_cuenta_seleccionada,
                    style="Secondary.TButton"
                ).pack(side="left", padx=6)
        except Exception:
            pass
    
    def _create_trabajadores_table(self, parent):
        """Crear tabla de trabajadores"""
        columns = [
            {'id': 'id', 'text': 'ID', 'width': 60},
            {'id': 'rut', 'text': 'RUT', 'width': 120},
            {'id': 'nombre_completo', 'text': 'Nombre Completo', 'width': 200},
            {'id': 'cargo', 'text': 'Cargo', 'width': 150},
            {'id': 'telefono', 'text': 'Teléfono', 'width': 120},
            {'id': 'email', 'text': 'Email', 'width': 200},
            {'id': 'salario', 'text': 'Salario', 'width': 100, 'formatter': utils.format_currency},
            {'id': 'fecha_contratacion', 'text': 'Fecha Contratación', 'width': 120},
            {'id': 'activo', 'text': 'Estado', 'width': 80}
        ]
        
        self.table = CustomTable(
            parent,
            columns=columns,
            height=20,
            show_toolbar=False
        )
        self.table.grid(row=1, column=0, sticky="nsew")
        
        # Configurar menú contextual
        menu_items = [
            {'label': 'Ver Detalles', 'command': self._ver_detalles},
            {'label': 'Editar', 'command': self._editar_trabajador},
            {'separator': True},
            {'label': 'Desactivar', 'command': self._desactivar_trabajador}
        ]
        self.table.add_context_menu(menu_items)
    
    def _load_trabajadores(self):
        """Cargar trabajadores en la tabla"""
        try:
            self.trabajadores = TrabajadorService.obtener_todos(activos_only=False)
            
            # Preparar datos para la tabla
            table_data = []
            for trabajador in self.trabajadores:
                table_data.append({
                    'id': trabajador.id,
                    'rut': utils.format_rut(trabajador.rut),
                    'nombre_completo': f"{trabajador.nombre} {trabajador.apellido}",
                    'cargo': trabajador.cargo,
                    'telefono': trabajador.telefono,
                    'email': trabajador.email,
                    'salario': trabajador.salario,
                    'fecha_contratacion': utils.format_date(trabajador.fecha_contratacion),
                    'activo': 'Activo' if trabajador.activo else 'Inactivo',
                    '_tags': 'success' if trabajador.activo else 'danger'
                })
            
            self.table.load_data(table_data)
            
        except Exception as e:
            logger.error(f"Error cargando trabajadores: {e}")
            self.show_message("Error", "No se pudieron cargar los trabajadores", "error")
    
    def _nuevo_trabajador(self):
        """Abrir modal para nuevo trabajador"""
        fields = [
            {
                'name': 'rut',
                'label': 'RUT *',
                'type': 'entry',
                'required': True
            },
            {
                'name': 'nombre',
                'label': 'Nombre *',
                'type': 'entry',
                'required': True
            },
            {
                'name': 'apellido',
                'label': 'Apellido *',
                'type': 'entry',
                'required': True
            },
            {
                'name': 'cargo',
                'label': 'Cargo *',
                'type': 'entry',
                'required': True
            },
            {
                'name': 'telefono',
                'label': 'Teléfono',
                'type': 'entry',
                'required': False
            },
            {
                'name': 'email',
                'label': 'Email',
                'type': 'entry',
                'required': False
            },
            {
                'name': 'salario',
                'label': 'Salario',
                'type': 'entry',
                'required': False
            },
            {
                'name': 'fecha_contratacion',
                'label': 'Fecha Contratación (DD/MM/AAAA)',
                'type': 'entry',
                'required': False
            }
        ]
        
        modal = InputModal(self, "Nuevo Trabajador", fields)
        result = modal.show()
        
        if result:
            self._guardar_nuevo_trabajador(result)
    
    def _guardar_nuevo_trabajador(self, datos):
        """Guardar nuevo trabajador"""
        try:
            from models.trabajador import Trabajador
            
            # Parsear fecha
            fecha_contratacion = None
            if datos['fecha_contratacion']:
                try:
                    fecha_contratacion = utils.parse_date(datos['fecha_contratacion'])
                except ValueError:
                    self.show_message("Error", "Formato de fecha inválido. Use DD/MM/AAAA", "error")
                    return
            
            # Parsear salario
            salario = 0.0
            if datos['salario']:
                try:
                    salario = float(datos['salario'].replace('$', '').replace('.', ''))
                except ValueError:
                    self.show_message("Error", "Formato de salario inválido", "error")
                    return
            
            # Crear objeto trabajador
            trabajador = Trabajador(
                rut=datos['rut'],
                nombre=datos['nombre'],
                apellido=datos['apellido'],
                cargo=datos['cargo'],
                telefono=datos.get('telefono', ''),
                email=datos.get('email', ''),
                salario=salario,
                fecha_contratacion=fecha_contratacion,
                activo=True
            )
            
            # Guardar en base de datos
            TrabajadorService.crear_trabajador(trabajador)
            
            self.show_message("Éxito", "Trabajador creado correctamente", "info")
            self._load_trabajadores()
            # Si el usuario actual es admin, ofrecer crear cuenta de usuario
            try:
                current = AuthService.get_current_user()
                if current and current.rol == 'admin':
                    # Buscar el trabajador creado por RUT para obtener su id
                    trabajadores = TrabajadorService.buscar_por_nombre(trabajador.nombre)
                    # Intentar encontrar por rut también
                    creado = None
                    for t in trabajadores:
                        if t.rut == trabajador.rut:
                            creado = t
                            break
                    # Si no lo encontramos por nombre, tomar el último insertado (fallback)
                    if not creado:
                        listado = TrabajadorService.obtener_todos(activos_only=False)
                        if listado:
                            creado = listado[-1]
                    if creado:
                        self._preguntar_crear_cuenta(creado)
            except Exception:
                pass
            
        except ValidationError as e:
            self.show_message("Error de Validación", str(e), "error")
        except Exception as e:
            logger.error(f"Error creando trabajador: {e}")
            self.show_message("Error", "No se pudo crear el trabajador", "error")
    
    def _editar_trabajador(self):
        """Editar trabajador seleccionado"""
        selected = self.table.get_selected_item()
        if not selected:
            self.show_message("Advertencia", "Seleccione un trabajador para editar", "warning")
            return
        
        # Buscar trabajador completo
        trabajador_id = selected['id']
        trabajador = next((t for t in self.trabajadores if t.id == trabajador_id), None)
        
        if not trabajador:
            self.show_message("Error", "Trabajador no encontrado", "error")
            return
        
        fields = [
            {
                'name': 'rut',
                'label': 'RUT *',
                'type': 'entry',
                'required': True,
                'value': trabajador.rut
            },
            {
                'name': 'nombre',
                'label': 'Nombre *',
                'type': 'entry',
                'required': True,
                'value': trabajador.nombre
            },
            {
                'name': 'apellido',
                'label': 'Apellido *',
                'type': 'entry',
                'required': True,
                'value': trabajador.apellido
            },
            {
                'name': 'cargo',
                'label': 'Cargo *',
                'type': 'entry',
                'required': True,
                'value': trabajador.cargo
            },
            {
                'name': 'telefono',
                'label': 'Teléfono',
                'type': 'entry',
                'required': False,
                'value': trabajador.telefono
            },
            {
                'name': 'email',
                'label': 'Email',
                'type': 'entry',
                'required': False,
                'value': trabajador.email
            },
            {
                'name': 'salario',
                'label': 'Salario',
                'type': 'entry',
                'required': False,
                'value': str(trabajador.salario)
            },
            {
                'name': 'fecha_contratacion',
                'label': 'Fecha Contratación (DD/MM/AAAA)',
                'type': 'entry',
                'required': False,
                'value': utils.format_date(trabajador.fecha_contratacion) if trabajador.fecha_contratacion else ''
            }
        ]
        
        modal = InputModal(self, f"Editar Trabajador: {trabajador.nombre}", fields)
        result = modal.show()
        
        if result:
            self._actualizar_trabajador(trabajador_id, result)
    
    def _actualizar_trabajador(self, trabajador_id, datos):
        """Actualizar trabajador"""
        try:
            # Parsear datos
            update_data = {}
            
            if 'salario' in datos and datos['salario']:
                try:
                    update_data['salario'] = float(datos['salario'].replace('$', '').replace('.', ''))
                except ValueError:
                    self.show_message("Error", "Formato de salario inválido", "error")
                    return
            
            if 'fecha_contratacion' in datos and datos['fecha_contratacion']:
                try:
                    update_data['fecha_contratacion'] = utils.parse_date(datos['fecha_contratacion'])
                except ValueError:
                    self.show_message("Error", "Formato de fecha inválido. Use DD/MM/AAAA", "error")
                    return
            
            # Agregar otros campos
            for field in ['rut', 'nombre', 'apellido', 'cargo', 'telefono', 'email']:
                if field in datos:
                    update_data[field] = datos[field]
            
            # Actualizar en base de datos
            TrabajadorService.actualizar_trabajador(trabajador_id, **update_data)
            
            self.show_message("Éxito", "Trabajador actualizado correctamente", "info")
            self._load_trabajadores()
            
        except Exception as e:
            logger.error(f"Error actualizando trabajador: {e}")
            self.show_message("Error", "No se pudo actualizar el trabajador", "error")
    
    def _ver_detalles(self):
        """Ver detalles del trabajador seleccionado"""
        selected = self.table.get_selected_item()
        if not selected:
            self.show_message("Advertencia", "Seleccione un trabajador para ver detalles", "warning")
            return
        
        # Buscar trabajador completo
        trabajador_id = selected['id']
        trabajador = next((t for t in self.trabajadores if t.id == trabajador_id), None)
        
        if not trabajador:
            self.show_message("Error", "Trabajador no encontrado", "error")
            return
        
        # Mostrar detalles en un mensaje
        detalles = f"""
        📋 Detalles del Trabajador
        
        🆔 ID: {trabajador.id}
        🏷️ RUT: {utils.format_rut(trabajador.rut)}
        👤 Nombre: {trabajador.nombre} {trabajador.apellido}
        💼 Cargo: {trabajador.cargo}
        📞 Teléfono: {trabajador.telefono or 'No especificado'}
        📧 Email: {trabajador.email or 'No especificado'}
        💰 Salario: {utils.format_currency(trabajador.salario)}
        📅 Fecha Contratación: {utils.format_date(trabajador.fecha_contratacion) or 'No especificada'}
        🟢 Estado: {'Activo' if trabajador.activo else 'Inactivo'}
        """
        
        self.show_message(f"Detalles: {trabajador.nombre}", detalles.strip(), "info")

    def _preguntar_crear_cuenta(self, trabajador):
        """Preguntar si se desea crear una cuenta de usuario para el trabajador"""
        if not (AuthService.get_current_user() and AuthService.get_current_user().rol == 'admin'):
            return

        if utils.show_message(self, f"Crear cuenta para {trabajador.nombre}", "¿Desea crear una cuenta de usuario para este trabajador?", "question"):
            self._crear_cuenta_para_trabajador(trabajador)

    def _crear_cuenta_para_trabajador(self, trabajador):
        """Mostrar modal para crear cuenta y llamar a AuthService.crear_usuario"""
        fields = [
            {'name': 'username', 'label': 'Nombre de usuario *', 'type': 'entry', 'required': True, 'value': trabajador.rut.replace('.', '').replace('-', '')[:12]},
            {'name': 'password', 'label': 'Contraseña *', 'type': 'password', 'required': True},
            {'name': 'rol', 'label': 'Rol', 'type': 'combobox', 'values': ['trabajador', 'admin'], 'required': True, 'value': 'trabajador'}
        ]

        modal = InputModal(self, f"Crear cuenta para {trabajador.nombre}", fields)
        result = modal.show()
        if not result:
            return

        try:
            usuario = Usuario(
                username=result['username'],
                nombre=f"{trabajador.nombre} {trabajador.apellido}",
                email=trabajador.email or '',
                rol=result.get('rol', 'trabajador'),
                activo=True
            )
            AuthService.crear_usuario(usuario, result['password'])
            self.show_message("Éxito", "Cuenta creada correctamente", "info")
        except Exception as e:
            logger.error(f"Error creando cuenta para trabajador: {e}")
            self.show_message("Error", f"No se pudo crear la cuenta: {str(e)}", "error")

    def _crear_cuenta_seleccionada(self):
        """Crear cuenta para el trabajador seleccionado en la tabla"""
        selected = self.table.get_selected_item()
        if not selected:
            self.show_message("Advertencia", "Seleccione un trabajador para crear cuenta", "warning")
            return

        trabajador_id = selected['id']
        trabajador = next((t for t in self.trabajadores if t.id == trabajador_id), None)
        if not trabajador:
            self.show_message("Error", "Trabajador no encontrado", "error")
            return

        self._crear_cuenta_para_trabajador(trabajador)
    
    def _desactivar_trabajador(self):
        """Desactivar trabajador seleccionado"""
        selected = self.table.get_selected_item()
        if not selected:
            self.show_message("Advertencia", "Seleccione un trabajador para desactivar", "warning")
            return
        
        trabajador_id = selected['id']
        nombre = selected['nombre_completo']
        
        if not self.show_message(
            "Confirmar Desactivación",
            f"¿Está seguro que desea desactivar al trabajador {nombre}?",
            "question"
        ):
            return
        
        try:
            TrabajadorService.desactivar_trabajador(trabajador_id)
            self.show_message("Éxito", "Trabajador desactivado correctamente", "info")
            self._load_trabajadores()
            
        except Exception as e:
            logger.error(f"Error desactivando trabajador: {e}")
            self.show_message("Error", "No se pudo desactivar el trabajador", "error")
    
    def _buscar_trabajadores(self, event=None):
        """Buscar trabajadores por nombre"""
        search_term = self.search_var.get().strip()
        
        if not search_term:
            self._load_trabajadores()
            return
        
        try:
            resultados = TrabajadorService.buscar_por_nombre(search_term)
            
            # Preparar datos para la tabla
            table_data = []
            for trabajador in resultados:
                table_data.append({
                    'id': trabajador.id,
                    'rut': utils.format_rut(trabajador.rut),
                    'nombre_completo': f"{trabajador.nombre} {trabajador.apellido}",
                    'cargo': trabajador.cargo,
                    'telefono': trabajador.telefono,
                    'email': trabajador.email,
                    'salario': trabajador.salario,
                    'fecha_contratacion': utils.format_date(trabajador.fecha_contratacion),
                    'activo': 'Activo' if trabajador.activo else 'Inactivo',
                    '_tags': 'success' if trabajador.activo else 'danger'
                })
            
            self.table.load_data(table_data)
            
        except Exception as e:
            logger.error(f"Error buscando trabajadores: {e}")
    
    def _limpiar_busqueda(self):
        """Limpiar búsqueda"""
        self.search_var.set("")
        self._load_trabajadores()
    
    def on_show(self):
        """Cuando se muestra la vista"""
        super().on_show()
        # Verificar permisos de administrador (usar AuthService/app_context cuando no hay controller)
        from core.auth import AuthService
        user = AuthService.get_current_user()
        if not user or user.rol != 'admin':
            self.show_message("Acceso Denegado", "Se requieren permisos de administrador", "error")
            from app.router import router
            router.navigate_to('dashboard')