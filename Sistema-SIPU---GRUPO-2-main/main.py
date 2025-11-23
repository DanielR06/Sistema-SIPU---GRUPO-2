import customtkinter as ctk
from clases import InMemoryAuthService, DEFAULT_DB, Usuario, Administrador, Aspirante, AuthService
from db import SQLiteRepository
import os

# Intentamos importar Pillow para manejar imágenes (logo). Si no está,
# la app seguirá funcionando.
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

# Tamaño máximo del logo en la cabecera (ajústable aquí)
LOGO_MAX_WIDTH = 160
LOGO_MAX_HEIGHT = 48

# Interfaz gráfica
# Demuestra inyección de dependencias: la App recibe un AuthService

class App(ctk.CTk):
    def __init__(self, auth_service: AuthService):
        super().__init__()
        self.title("SISTEMA SIPU - Login")
        self.geometry("900x560")
        self.resizable(False, False)

        # Inyectamos el servicio de autenticación y el repositorio de datos
        self.auth_service = auth_service
        # Repositorio: persistencia para estudiantes y documentos
        self.repository = None

        # Tema
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("blue")

        # Variables para menú
        self.current_menu = None

        # --- Diseño: cabecera superior y tarjeta de login centrada ---
        # Cabecera superior (barra gris oscuro)
        self.header = ctk.CTkFrame(self, fg_color="#3b3b3b", height=64)
        self.header.place(x=0, y=0, relwidth=1)
        # Logo a la izquierda (si existe, mostramos imagen)
        logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
        if PIL_AVAILABLE and os.path.exists(logo_path):
            try:
                img = Image.open(logo_path)
                # Redimensionar manteniendo la proporción para que quepa en el área
                w, h = img.size
                scale = min(LOGO_MAX_WIDTH / w, LOGO_MAX_HEIGHT / h, 1.0)
                new_w = max(1, int(w * scale))
                new_h = max(1, int(h * scale))
                img = img.resize((new_w, new_h), Image.LANCZOS)
                self._logo_img = ImageTk.PhotoImage(img)
                self.logo_lbl = ctk.CTkLabel(self.header, image=self._logo_img, text="")
                self.logo_lbl.place(x=12, y=12)
            except Exception:
                # En caso de fallo al cargar la imagen, caemos al texto
                self.logo_lbl = ctk.CTkLabel(self.header, text="Uleam", text_color="#ffffff", font=ctk.CTkFont(size=16, weight="bold"))
                self.logo_lbl.place(x=12, y=16)
        else:
            self.logo_lbl = ctk.CTkLabel(self.header, text="Uleam", text_color="#ffffff", font=ctk.CTkFont(size=16, weight="bold"))
            self.logo_lbl.place(x=12, y=16)

        # Texto derecho (bienvenida placeholder)
        self.top_user_lbl = ctk.CTkLabel(self.header, text="", text_color="#ffffff")
        self.top_user_lbl.place(relx=0.75, y=20)

        # Fondo central
        self.configure(fg_color="#f6f7f8")

        # Tarjeta blanca central (login)
        self.container = ctk.CTkFrame(self, corner_radius=8, fg_color="#ffffff", border_width=1, border_color="#e6e6e6", width=640, height=260)
        self.container.place(relx=0.5, rely=0.45, anchor=ctk.CENTER)

        # Cabecera de la tarjeta (oscura)
        self.card_top = ctk.CTkFrame(self.container, fg_color="#4a4a4a", height=46)
        self.card_top.place(relx=0, y=0, relwidth=1)
        self.card_title = ctk.CTkLabel(self.card_top, text="DGCANU | ADMISIÓN | INICIAR SESIÓN", text_color="#ffffff", font=ctk.CTkFont(size=12, weight="bold"))
        self.card_title.place(x=12, y=10)

        # Campos en la tarjeta
        lbl_user = ctk.CTkLabel(self.container, text="Usuario")
        lbl_user.place(x=20, y=66)
        self.entry_user = ctk.CTkEntry(self.container, placeholder_text="correo o usuario", width=420, height=30)
        self.entry_user.place(x=20, y=90)

        lbl_pass = ctk.CTkLabel(self.container, text="Contraseña")
        lbl_pass.place(x=20, y=132)
        self.entry_pass = ctk.CTkEntry(self.container, placeholder_text="contraseña", show="*", width=420, height=30)
        self.entry_pass.place(x=20, y=156)

        # Mostrar contraseña
        self.show_var = ctk.BooleanVar(value=False)
        chk_show = ctk.CTkCheckBox(self.container, text="Mostrar", variable=self.show_var, command=self._toggle_password)
        chk_show.place(x=460, y=156)

        # Mensaje
        self.lbl_msg = ctk.CTkLabel(self.container, text="", text_color="#ff0000")
        self.lbl_msg.place(x=20, y=196)

        # Botones
        btn_register = ctk.CTkButton(self.container, text="Regístrate aquí", command=self._on_register, fg_color="#e1e7eb", text_color="#000", width=160, height=32)
        btn_register.place(x=20, y=220)
        btn_login = ctk.CTkButton(self.container, text="Iniciar sesión", command=self._on_login, fg_color="#13ce88", width=140, height=36)
        btn_login.place(x=460, y=216)

    def _toggle_password(self):
        if self.show_var.get():
            self.entry_pass.configure(show="")
        else:
            self.entry_pass.configure(show="*")

    def _on_login(self):
        correo = self.entry_user.get().strip()
        contrasena = self.entry_pass.get().strip()

        if not correo or not contrasena:
            self.lbl_msg.configure(text="Por favor complete usuario y contraseña", text_color="#d9534f")
            return

        usuario = self.auth_service.authenticate(correo, contrasena)
        if usuario is None:
            self.lbl_msg.configure(text="Credenciales incorrectas", text_color="#d9534f")
            return

        # Polimorfismo: comportamiento según el tipo concreto de Usuario
        if isinstance(usuario, Administrador):
            # inicializamos repositorio y abrimos panel principal
            self.repository = SQLiteRepository()
            self._open_main_panel(usuario)
        elif isinstance(usuario, Aspirante):
            self.repository = SQLiteRepository()
            self._open_main_panel(usuario)
        else:
            self.repository = SQLiteRepository()
            self._open_main_panel(usuario)

    def _on_register(self):
        # Abrir el formulario real de inscripción
        # Reutilizamos _open_inscripcion que abre un modal completo
        self._open_inscripcion(self)

    def _open_dashboard(self, mensaje: str):
        # Reutilizamos ventana para mostrar mensaje de acceso
        dash = ctk.CTkToplevel(self)
        dash.geometry("480x240")
        dash.title("Dashboard")
        lbl = ctk.CTkLabel(dash, text=mensaje, font=ctk.CTkFont(size=14, weight="bold"))
        lbl.pack(pady=24)
        # Información ejemplo
        info = ctk.CTkLabel(dash, text="(Aquí se integraría la funcionalidad real según el rol)")
        info.pack(pady=8)

    # Panel principal post-login

    def _open_main_panel(self, usuario: Usuario):
        """Muestra la interfaz principal en la misma ventana (no usar Toplevel).
        Oculta la tarjeta de login y crea la barra de menú, submenu y el área de contenido
        como atributos de la App para poder destruirlos al cerrar sesión.
        """
        # Ajustes de ventana principal
        self.geometry("1100x640")
        self.title(f"SIPU - Sesión: {usuario.nombre} ({usuario.get_rol()})")

        # Actualizar usuario en la cabecera
        if hasattr(self, 'top_user_lbl'):
            self.top_user_lbl.configure(text=f"Bienvenido/a, {usuario.nombre}")

        # Ocultar tarjeta de login
        if hasattr(self, 'container'):
            try:
                self.container.place_forget()
            except Exception:
                self.container.destroy()

        # Barra superior (reutilizamos self.header)
        self.header.configure(fg_color="#3b3b3b")

        # Menú horizontal (simulando botones tipo pestaña)
        self.menu_frame = ctk.CTkFrame(self, height=44, fg_color="#f0f0f0")
        self.menu_frame.place(x=0, y=64, relwidth=1)

        # Creamos botones que abren un pequeño submenu (como en la imagen)
        btn_asp = ctk.CTkButton(self.menu_frame, text="Aspirante", command=self._on_menu_aspirante, width=120, height=32)
        btn_asp.place(x=12, y=6)
        btn_seg = ctk.CTkButton(self.menu_frame, text="Seguridad", command=self._on_menu_seguridad, width=120, height=32)
        btn_seg.place(x=138, y=6)
        btn_exit = ctk.CTkButton(self.menu_frame, text="Salir", command=self._logout, width=80, height=32)
        btn_exit.place(x=264, y=6)

        # Submenu frame (aparece bajo los botones)
        # Hacemos el submenu más visible (color claro y borde) para depuración/UX
        self.submenu = ctk.CTkFrame(self, fg_color="#ffffff", border_width=1, border_color="#bfbfbf", width=240, height=120)
        self.submenu.place(x=12, y=118)
        self.submenu.lower()  # ocultar inicialmente

        # Contenedor principal donde cambian las vistas
        self.content_frame = ctk.CTkFrame(self, fg_color="#ffffff", width=1076, height=370)
        self.content_frame.place(x=12, y=246)

        # Mostrar vista por defecto
        # Mostrar el submenu de 'aspirante' por defecto para exponer las opciones
        self._toggle_submenu('aspirante')
        self._show_aspirante_view(self.content_frame)

    def _logout(self):
        # Cerrar repositorio si está abierto
        try:
            if self.repository:
                self.repository.close()
        except Exception:
            pass

        # Destruir elementos del panel principal
        for attr in ('menu_frame', 'submenu', 'content_frame'):
            if hasattr(self, attr):
                try:
                    getattr(self, attr).destroy()
                except Exception:
                    pass
                finally:
                    if hasattr(self, attr):
                        delattr(self, attr)

        # Restaurar título y tamaño inicial si se desea
        self.title("SISTEMA SIPU - Login")
        self.geometry("900x560")

        # Volver a mostrar la tarjeta de login
        if hasattr(self, 'container'):
            try:
                self.container.place(relx=0.5, rely=0.45, anchor=ctk.CENTER)
            except Exception:
                pass

    def _toggle_submenu(self, which: str):
        # Mostrar opciones según botón (aspirante/seguridad)
        print(f"DEBUG: _toggle_submenu called with {which}")
        for child in self.submenu.winfo_children():
            child.destroy()
        if which == 'aspirante':
            opt1 = ctk.CTkButton(self.submenu, text="Verificar registro nacional", command=self._verificar_registro_in_place, width=220, height=28)
            opt1.place(x=8, y=8)
            opt2 = ctk.CTkButton(self.submenu, text="Inscripción", command=lambda: self._show_inscripciones_view(self.content_frame), width=220, height=28)
            opt2.place(x=8, y=44)
            # aseguramos que el submenu quede encima de otros elementos
            self.submenu.lift()
            self.menu_frame.lift()
        elif which == 'seguridad':
            opt1 = ctk.CTkButton(self.submenu, text="Cambiar Contraseña", command=self._show_change_password_view, width=220, height=28)
            opt1.place(x=8, y=8)
            opt2 = ctk.CTkButton(self.submenu, text="Actualizar información", command=self._show_update_user_view, width=220, height=28)
            opt2.place(x=8, y=44)
            self.submenu.lift()
            self.menu_frame.lift()

    def _on_menu_aspirante(self):
        # Mostrar submenu y la vista aspirante por defecto
        self._toggle_submenu('aspirante')
        self._show_aspirante_view(self.content_frame)

    def _on_menu_seguridad(self):
        # Mostrar submenu y la vista de seguridad por defecto
        self._toggle_submenu('seguridad')
        self._show_seguridad_view(self.content_frame)

    # --- Vistas "in-place" para mostrar dentro de self.content_frame ---
    def _verificar_registro_in_place(self):
        if not hasattr(self, 'content_frame'):
            return
        frame = self.content_frame
        self._clear_frame(frame)
        lbl = ctk.CTkLabel(frame, text="Verificar registro nacional", font=ctk.CTkFont(size=16, weight="bold"))
        lbl.pack(anchor="nw", pady=(8,6))

        lbl_ced = ctk.CTkLabel(frame, text="Ingrese número de identificación (DNI)")
        lbl_ced.pack(anchor="nw", pady=(6,2))
        ent = ctk.CTkEntry(frame, width=280)
        ent.pack(anchor="nw", pady=(0,8))

        res_lbl = ctk.CTkLabel(frame, text="", text_color="#0b3d91")
        res_lbl.pack(anchor="nw", pady=(6,4))

        def buscar():
            dni = ent.get().strip()
            if not dni:
                res_lbl.configure(text="Ingrese un DNI para verificar", text_color="#d9534f")
                return
            # Simulación: buscamos en repository
            if self.repository is None:
                self.repository = SQLiteRepository()
            rows = self.repository.list_students()
            found = [r for r in rows if r['dni'] == dni]
            if found:
                u = found[0]
                res_lbl.configure(text=f"Registro encontrado: {u['nombre']} - {u['correo']}", text_color="#28a745")
            else:
                res_lbl.configure(text="No se encontró registro para el DNI proporcionado", text_color="#d9534f")

        btn = ctk.CTkButton(frame, text="Buscar", command=buscar, width=120)
        btn.pack(anchor="nw", pady=(8,0))

    def _show_change_password_view(self):
        if not hasattr(self, 'content_frame'):
            return
        frame = self.content_frame
        self._clear_frame(frame)
        lbl = ctk.CTkLabel(frame, text="Cambiar Contraseña", font=ctk.CTkFont(size=16, weight="bold"))
        lbl.pack(anchor="nw", pady=(8,6))

        lbl_cor = ctk.CTkLabel(frame, text="Correo")
        lbl_cor.pack(anchor="nw")
        ent_cor = ctk.CTkEntry(frame, width=320)
        ent_cor.pack(anchor="nw", pady=(0,6))

        lbl_old = ctk.CTkLabel(frame, text="Contraseña actual")
        lbl_old.pack(anchor="nw")
        ent_old = ctk.CTkEntry(frame, show="*", width=320)
        ent_old.pack(anchor="nw", pady=(0,6))

        lbl_new = ctk.CTkLabel(frame, text="Nueva contraseña")
        lbl_new.pack(anchor="nw")
        ent_new = ctk.CTkEntry(frame, show="*", width=320)
        ent_new.pack(anchor="nw", pady=(0,6))

        msg = ctk.CTkLabel(frame, text="")
        msg.pack(anchor="nw", pady=(6,0))

        def cambiar():
            correo = ent_cor.get().strip()
            old = ent_old.get().strip()
            new = ent_new.get().strip()
            if not correo or not old or not new:
                msg.configure(text="Complete todos los campos", text_color="#d9534f")
                return
            ok = self.auth_service.change_password(correo, old, new)
            if ok:
                msg.configure(text="Contraseña cambiada correctamente", text_color="#28a745")
            else:
                msg.configure(text="No se pudo cambiar la contraseña (revise datos)", text_color="#d9534f")

        btn = ctk.CTkButton(frame, text="Cambiar", command=cambiar, width=120)
        btn.pack(anchor="nw", pady=(8,0))

    def _show_update_user_view(self):
        if not hasattr(self, 'content_frame'):
            return
        frame = self.content_frame
        self._clear_frame(frame)
        lbl = ctk.CTkLabel(frame, text="Actualizar información de usuario", font=ctk.CTkFont(size=16, weight="bold"))
        lbl.pack(anchor="nw", pady=(8,6))

        lbl_cor = ctk.CTkLabel(frame, text="Correo actual")
        lbl_cor.pack(anchor="nw")
        ent_cor = ctk.CTkEntry(frame, width=320)
        ent_cor.pack(anchor="nw", pady=(0,6))

        lbl_nombre = ctk.CTkLabel(frame, text="Nuevo nombre")
        lbl_nombre.pack(anchor="nw")
        ent_nombre = ctk.CTkEntry(frame, width=320)
        ent_nombre.pack(anchor="nw", pady=(0,6))

        lbl_newcor = ctk.CTkLabel(frame, text="Nuevo correo")
        lbl_newcor.pack(anchor="nw")
        ent_newcor = ctk.CTkEntry(frame, width=320)
        ent_newcor.pack(anchor="nw", pady=(0,6))

        msg = ctk.CTkLabel(frame, text="")
        msg.pack(anchor="nw", pady=(6,0))

        def actualizar():
            correo = ent_cor.get().strip()
            nombre = ent_nombre.get().strip() or None
            newc = ent_newcor.get().strip() or None
            if not correo:
                msg.configure(text="Ingrese el correo actual", text_color="#d9534f")
                return
            ok = self.auth_service.update_user_info(correo, nombre, newc)
            if ok:
                msg.configure(text="Información actualizada", text_color="#28a745")
            else:
                msg.configure(text="No se pudo actualizar (correo duplicado o inexistente)", text_color="#d9534f")

        btn = ctk.CTkButton(frame, text="Actualizar", command=actualizar, width=120)
        btn.pack(anchor="nw", pady=(8,0))

    def _clear_frame(self, frame: ctk.CTkFrame):
        for child in frame.winfo_children():
            child.destroy()

    def _show_aspirante_view(self, frame: ctk.CTkFrame):
        # Depuración: indicar en consola que se está mostrando la vista
        print("DEBUG: _show_aspirante_view called")
        self._clear_frame(frame)

        # Añadimos un recuadro visible para comprobar que el contenedor se muestra
        debug_box = ctk.CTkFrame(frame, fg_color="#eef5ff", corner_radius=6)
        debug_box.pack(anchor="nw", padx=8, pady=8, fill="both", expand=True)
        debug_box.configure(border_width=1, border_color="#99c2ff")

        lbl = ctk.CTkLabel(debug_box, text="Aspirante", font=ctk.CTkFont(size=16, weight="bold"), text_color="#0b3d91")
        lbl.pack(anchor="nw", padx=8, pady=(8,4))

        # Sub-opciones
        btn_ver = ctk.CTkButton(debug_box, text="Verificar registro nacional", command=self._verificar_registro, width=260)
        btn_ver.pack(anchor="nw", pady=6, padx=8)
        btn_insc = ctk.CTkButton(debug_box, text="Inscripción", command=lambda: self._open_inscripcion(frame), width=260)
        btn_insc.pack(anchor="nw", pady=6, padx=8)

        # Lista de estudiantes
        lbl2 = ctk.CTkLabel(debug_box, text="Estudiantes registrados:", text_color="#0b3d91")
        lbl2.pack(anchor="nw", pady=(12, 4), padx=8)
        self.students_box = ctk.CTkTextbox(debug_box, width=600, height=180)
        self.students_box.pack(anchor="nw", padx=8, pady=(0,8))
        self._refresh_students()

    def _show_inscripciones_view(self, frame: ctk.CTkFrame):
        """Muestra un listado tipo tabla de inscripciones/aspirantes.
        Si la información está completa, se mostrará Periodo, Identificación, Apellidos, Nombres y Estado de inscripción.
        """
        if self.repository is None:
            self.repository = SQLiteRepository()

        self._clear_frame(frame)
        hdr = ctk.CTkFrame(frame, fg_color="#ffffff")
        hdr.pack(fill="x", padx=8, pady=(8,4))
        title = ctk.CTkLabel(hdr, text="Aspirante", font=ctk.CTkFont(size=16, weight="bold"), text_color="#0b3d91")
        title.pack(side="left", padx=8, pady=8)

        # area scrollable para la tabla
        table_frame = ctk.CTkScrollableFrame(frame, width=1040, height=320, fg_color="#ffffff")
        table_frame.pack(padx=8, pady=(4,8), fill="both", expand=True)

        # Encabezados (usamos un grid dentro del scrollable)
        headers = ["Período", "Identificación", "Apellidos", "Nombres", "Inscripción Finalizada", "Acciones"]
        for col, h in enumerate(headers):
            lbl = ctk.CTkLabel(table_frame, text=h, fg_color="#f3f6f9", width=180, height=32, corner_radius=6, anchor="w")
            lbl.grid(row=0, column=col, padx=4, pady=4, sticky="nsew")

        rows = self.repository.list_students()
        for r_idx, r in enumerate(rows, start=1):
            # nombre puede contener apellidos y nombres; intentamos separarlos
            nombre_full = (r.get('nombre') if isinstance(r, dict) else r['nombre']) if r is not None else ""
            parts = nombre_full.split()
            if len(parts) >= 3:
                nombres = " ".join(parts[-2:])
                apellidos = " ".join(parts[:-2])
            elif len(parts) == 2:
                apellidos, nombres = parts[0], parts[1]
            else:
                apellidos, nombres = "", nombre_full

            periodo = r.get('periodo') if isinstance(r, dict) and 'periodo' in r else "-"
            identificacion = r.get('dni') if isinstance(r, dict) else r['dni']
            inscr_final = "Sí" if (r.get('inscripcion_finalizada') if isinstance(r, dict) and 'inscripcion_finalizada' in r else False) else "No"

            vals = [periodo, identificacion or "", apellidos, nombres, inscr_final]
            for col, v in enumerate(vals):
                cell = ctk.CTkLabel(table_frame, text=str(v), anchor="w", width=180)
                cell.grid(row=r_idx, column=col, padx=4, pady=6, sticky="nsew")

            # acciones (editar/ver)
            btn_edit = ctk.CTkButton(table_frame, text="✏️", width=40, height=28, command=lambda sid=r['id']: print(f"Editar {sid}"))
            btn_edit.grid(row=r_idx, column=len(headers)-1, padx=4, pady=6)

        # ajustar columnas para distribución
        for c in range(len(headers)):
            table_frame.grid_columnconfigure(c, weight=1)

    def _show_seguridad_view(self, frame: ctk.CTkFrame):
        self._clear_frame(frame)
        lbl = ctk.CTkLabel(frame, text="Seguridad", font=ctk.CTkFont(size=16, weight="bold"))
        lbl.pack(anchor="nw")

        # Opciones de seguridad: Cambiar Contraseña, Actualizar información
        btn_pwd = ctk.CTkButton(frame, text="Cambiar Contraseña", command=self._open_change_password)
        btn_pwd.pack(anchor="nw", pady=6)

        btn_update = ctk.CTkButton(frame, text="Actualizar información de usuario", command=self._open_update_user)
        btn_update.pack(anchor="nw", pady=6)

        # Mensaje de ayuda
        help_lbl = ctk.CTkLabel(frame, text="Use las opciones para actualizar su cuenta (simulado)")
        help_lbl.pack(anchor="nw", pady=(12,0))

    def _open_change_password(self):
        modal = ctk.CTkToplevel(self)
        modal.title("Cambiar Contraseña")
        modal.geometry("420x220")

        lbl_info = ctk.CTkLabel(modal, text="Ingrese su correo y las contraseñas")
        lbl_info.place(x=12, y=12)

        lbl_cor = ctk.CTkLabel(modal, text="Correo")
        lbl_cor.place(x=12, y=48)
        ent_cor = ctk.CTkEntry(modal, width=260)
        ent_cor.place(x=140, y=48)

        lbl_old = ctk.CTkLabel(modal, text="Contraseña actual")
        lbl_old.place(x=12, y=88)
        ent_old = ctk.CTkEntry(modal, show="*", width=260)
        ent_old.place(x=140, y=88)

        lbl_new = ctk.CTkLabel(modal, text="Nueva contraseña")
        lbl_new.place(x=12, y=128)
        ent_new = ctk.CTkEntry(modal, show="*", width=260)
        ent_new.place(x=140, y=128)

        msg = ctk.CTkLabel(modal, text="")
        msg.place(x=12, y=168)

        def cambiar():
            correo = ent_cor.get().strip()
            old = ent_old.get().strip()
            new = ent_new.get().strip()
            if not correo or not old or not new:
                msg.configure(text="Complete todos los campos", text_color="#d9534f")
                return
            ok = self.auth_service.change_password(correo, old, new)
            if ok:
                msg.configure(text="Contraseña cambiada correctamente", text_color="#28a745")
            else:
                msg.configure(text="No se pudo cambiar la contraseña (revise datos)", text_color="#d9534f")
        btn = ctk.CTkButton(modal, text="Cambiar", command=cambiar, width=100)
        btn.place(x=300, y=164)

    def _open_update_user(self):
        modal = ctk.CTkToplevel(self)
        modal.title("Actualizar información de usuario")
        modal.geometry("480x260")

        lbl_info = ctk.CTkLabel(modal, text="Ingrese correo actual y los nuevos datos")
        lbl_info.place(x=12, y=12)

        lbl_cor = ctk.CTkLabel(modal, text="Correo actual")
        lbl_cor.place(x=12, y=48)
        ent_cor = ctk.CTkEntry(modal, width=280)
        ent_cor.place(x=180, y=48)

        lbl_nombre = ctk.CTkLabel(modal, text="Nuevo nombre")
        lbl_nombre.place(x=12, y=88)
        ent_nombre = ctk.CTkEntry(modal, width=280)
        ent_nombre.place(x=180, y=88)

        lbl_newcor = ctk.CTkLabel(modal, text="Nuevo correo")
        lbl_newcor.place(x=12, y=128)
        ent_newcor = ctk.CTkEntry(modal, width=280)
        ent_newcor.place(x=180, y=128)

        msg = ctk.CTkLabel(modal, text="")
        msg.place(x=12, y=168)

        def actualizar():
            correo = ent_cor.get().strip()
            nombre = ent_nombre.get().strip() or None
            newc = ent_newcor.get().strip() or None
            if not correo:
                msg.configure(text="Ingrese el correo actual", text_color="#d9534f")
                return
            ok = self.auth_service.update_user_info(correo, nombre, newc)
            if ok:
                msg.configure(text="Información actualizada", text_color="#28a745")
            else:
                msg.configure(text="No se pudo actualizar (correo duplicado o inexistente)", text_color="#d9534f")

        btn = ctk.CTkButton(modal, text="Actualizar", command=actualizar, width=100)
        btn.place(x=360, y=208)

    def _verificar_registro(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Verificar registro nacional")
        popup.geometry("400x160")
        lbl = ctk.CTkLabel(popup, text="Comprobar registro nacional (simulado)")
        lbl.pack(pady=24)
        btn = ctk.CTkButton(popup, text="Cerrar", command=popup.destroy)
        btn.pack()

    def _open_inscripcion(self, parent_frame: ctk.CTkFrame):
        # Modal para crear estudiante con selección de período
        modal = ctk.CTkToplevel(self)
        modal.title("Inscripción - Nuevo Aspirante")
        modal.geometry("640x420")

        # Cabecera visual 
        header = ctk.CTkFrame(modal, fg_color="#3b3b3b", height=48)
        header.place(x=0, y=0, relwidth=1)
        title_lbl = ctk.CTkLabel(header, text="CREACIÓN DE CUENTA", text_color="#ffffff", font=ctk.CTkFont(size=12, weight="bold"))
        title_lbl.place(x=12, y=12)
        date_lbl = ctk.CTkLabel(header, text="{:%d/%m/%Y}".format(__import__("datetime").datetime.now()), text_color="#ffffff")
        date_lbl.place(relx=0.88, y=12)

        # header
        base_y = 64

        lbl = ctk.CTkLabel(modal, text="Datos del aspirante", font=ctk.CTkFont(size=14, weight="bold"))
        lbl.place(x=12, y=base_y)

        # Asegurar repositorio
        if self.repository is None:
            self.repository = SQLiteRepository()

        # Cargar periodos
        periods = self.repository.list_periods()
        if not periods:
            # Crear un periodo demo si no existen
            self.repository.add_period("Periodo demo 2025", active=1)
            periods = self.repository.list_periods()

        # Lista para el option menu
        period_labels = [f"{p['name']} ({'ACTIVO' if p['active'] else 'INACTIVO'})" for p in periods]
        # Var para selección
        selected_period = ctk.StringVar(value=period_labels[0] if period_labels else "")

        lbl_period = ctk.CTkLabel(modal, text="Período *")
        lbl_period.place(x=12, y=base_y+40)
        try:
            opt = ctk.CTkOptionMenu(modal, values=period_labels, variable=selected_period)
            opt.place(x=120, y=base_y+40)
        except Exception:
            # Si CTkOptionMenu no está disponible, usar Entry como fallback
            opt = ctk.CTkEntry(modal, textvariable=selected_period, width=300)
            opt.place(x=120, y=base_y+40)

        lbl_ap = ctk.CTkLabel(modal, text="Apellidos")
        lbl_ap.place(x=12, y=base_y+80)
        ent_ap = ctk.CTkEntry(modal, width=300)
        ent_ap.place(x=120, y=base_y+80)

        lbl_nom = ctk.CTkLabel(modal, text="Nombres")
        lbl_nom.place(x=12, y=base_y+120)
        ent_nom = ctk.CTkEntry(modal, width=300)
        ent_nom.place(x=120, y=base_y+120)

        lbl_c = ctk.CTkLabel(modal, text="Correo")
        lbl_c.place(x=12, y=base_y+160)
        ent_c = ctk.CTkEntry(modal, width=300)
        ent_c.place(x=120, y=base_y+160)

        lbl_d = ctk.CTkLabel(modal, text="DNI")
        lbl_d.place(x=12, y=base_y+200)
        ent_d = ctk.CTkEntry(modal, width=200)
        ent_d.place(x=120, y=base_y+200)

        # Mover la nota de campos obligatorios hacia abajo para evitar solapamiento
        note_lbl = ctk.CTkLabel(modal, text="* Campos obligatorios", text_color="#b22222")
        note_lbl.place(x=12, y=base_y+240)

        msg = ctk.CTkLabel(modal, text="")
        msg.place(x=12, y=base_y+224)

        def guardar():
            apellidos = ent_ap.get().strip()
            nombres = ent_nom.get().strip()
            correo = ent_c.get().strip()
            dni = ent_d.get().strip()
            periodo_sel = selected_period.get()
            if not periodo_sel:
                msg.configure(text="Seleccione un período", text_color="#d9534f")
                return
            # obtener objeto periodo
            idx = period_labels.index(periodo_sel)
            p = periods[idx]
            if not p['active']:
                msg.configure(text="El período seleccionado no está activo. No se puede inscribir.", text_color="#d9534f")
                return
            if not (apellidos or nombres) or not correo:
                msg.configure(text="Apellidos/Nombres y correo son obligatorios", text_color="#d9534f")
                return
            try:
                # Guardado separado apellidos y nombres y referenciando el periodo
                self.repository.add_student(nombre=f"{apellidos} {nombres}".strip(), correo=correo, dni=dni, period_id=p['id'], inscripcion_finalizada=0, apellidos=apellidos, nombres=nombres)
                msg.configure(text="Aspirante registrado", text_color="#28a745")
                self._refresh_students()
                modal.destroy()
            except Exception as e:
                msg.configure(text=str(e), text_color="#d9534f")

        btn_save = ctk.CTkButton(modal, text="Guardar", command=guardar, width=120)
        # Usamos relx para evitar solapamiento y que sea estable si cambia el tamaño del modal
        btn_save.place(relx=0.98, y=base_y+252, anchor="e")

        # botón de volver del lado izquierdo
        btn_back = ctk.CTkButton(modal, text="← Volver", command=modal.destroy, width=120, fg_color="#e9eef2", text_color="#333")
        btn_back.place(relx=0.02, y=base_y+252, anchor="w")

    def _refresh_students(self):
        if self.repository is None:
            return
        rows = self.repository.list_students()
        text = []
        for r in rows:
            text.append(f"[{r['id']}] {r['nombre']} - {r['correo']} - DNI: {r['dni']}")
        if hasattr(self, 'students_box'):
            self.students_box.delete("0.0", "end")
            self.students_box.insert("0.0", "\n".join(text))


if __name__ == "__main__":
    # Inyectamos la implementación concreta (InMemoryAuthService) en la App
    auth_service = InMemoryAuthService(DEFAULT_DB)
    app = App(auth_service)
    app.mainloop()
